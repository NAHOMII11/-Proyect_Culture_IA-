from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
import httpx

from app.core.audit_client import send_audit_event
from app.infrastructure.database import get_db
from app.infrastructure.geopoint_repository import GeoPointRepository
from app.application.geo_service import GeoService
from app.schemas.geopoint_schema import (
    GeoPointCreate,
    GeoPointResponse,
    NearbyPlaceResponse,
    DistanceResponse,
)

router = APIRouter(prefix="/geo", tags=["Geo"])


def get_geo_service() -> GeoService:
    """
    Construye GeoService inyectando el repositorio concreto.
    Principio DIP: el router no instancia el servicio directamente,
    FastAPI lo resuelve via Depends en cada request.
    """
    return GeoService(repository=GeoPointRepository())


@router.post("/points", response_model=GeoPointResponse, status_code=201)
def register_point(
    data: GeoPointCreate,
    db: Session = Depends(get_db),
    service: GeoService = Depends(get_geo_service),
):
    try:
        return service.register_point(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/places/{place_id}", response_model=GeoPointResponse)
def get_by_place_id(
    place_id: UUID,
    db: Session = Depends(get_db),
    service: GeoService = Depends(get_geo_service),
):
    try:
        return service.get_by_place_id(db, place_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/nearby", response_model=List[NearbyPlaceResponse])
def get_nearby(
    lat: float,
    lng: float,
    radius_km: float = 5.0,
    db: Session = Depends(get_db),
    service: GeoService = Depends(get_geo_service),
):
    try:
        return service.get_nearby(db, lat, lng, radius_km)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/distance", response_model=DistanceResponse)
def calculate_distance(
    place_id_origin: UUID,
    place_id_destination: UUID,
    db: Session = Depends(get_db),
    service: GeoService = Depends(get_geo_service),
):
    try:
        return service.calculate_distance(db, place_id_origin, place_id_destination)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/asignar")
async def asignar_coordenadas():
    """
    Consulta todos los lugares de la API de catálogo,
    enriquece sus coordenadas vía Nominatim y devuelve confirmación.
    """
    try:
        # 1. Obtener todos los lugares de la API de catálogo
        async with httpx.AsyncClient() as client:
            places_response = await client.get("http://api_place_container:8003/places/")
            places_response.raise_for_status()
            places = places_response.json()
        
        if not places:
            return {"status": "Ok", "message": "No hay lugares para actualizar", "updated": 0}
        
        # 2. Para cada lugar, hacer PATCH a /enrich
        updated_count = 0
        async with httpx.AsyncClient() as client:
            for place in places:
                place_id = place.get("id")
                if not place_id:
                    continue
                
                try:
                    # Enviar PATCH para enriquecer coordenadas
                    enrich_url = f"http://api_place_container:8003/places/{place_id}/enrich"
                    response = await client.patch(enrich_url)
                    
                    if response.status_code in [200, 201]:
                        updated_count += 1
                except Exception as e:
                    print(f"Error enriqueciendo lugar {place_id}: {str(e)}")
                    continue
        
        send_audit_event(
            event_type="coordenadas_asignadas",
            source_service="geo-service",
            reference_id=f"asignacion-{updated_count}",
            payload_summary={
                "total_places": len(places),
                "updated": updated_count,
            },
        )

        return {
            "status": "Ok",
            "message": "Coordenadas actualizadas",
            "total_places": len(places),
            "updated": updated_count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al asignar coordenadas: {str(e)}"
        )


@router.get("/cerca")
async def sincronizar_puntos_cercanos():
    """
    Sincroniza puntos geográficos de lugares del catálogo.
    
    Flujo:
    1. Obtiene todos los lugares del catálogo (api_place_container)
    2. Para cada lugar, verifica si ya existe en geo/places
    3. Si NO existe (error/404), lo crea en geo/points con POST
    4. Si YA existe (200), no hace nada (evita duplicados)
    5. Retorna OK
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Obtener todos los lugares del catálogo
            places_response = await client.get("http://api_place_container:8003/places/")
            places_response.raise_for_status()
            places = places_response.json()
        
        if not places:
            return {"status": "Ok", "message": "No hay lugares para sincronizar"}
        
        # 2. Para cada lugar, verificar si existe y sincronizar si es necesario
        async with httpx.AsyncClient(timeout=30.0) as client:
            for place in places:
                place_id = place.get("id")
                latitude = place.get("latitude")
                longitude = place.get("longitude")
                address = place.get("address")
                
                if not place_id or latitude is None or longitude is None:
                    continue
                
                try:
                    # Verificar si ya existe en geo/places
                    check_url = f"http://cultureia-geo-api:8002/geo/places/{place_id}"
                    check_response = await client.get(check_url)
                    
                    # Si responde con 200, ya existe - no hacer nada
                    if check_response.status_code == 200:
                        print(f"Lugar {place_id} ya existe en geo/places, omitiendo...")
                        continue
                    
                    # Si no existe (error/404), crear el punto
                    create_point_data = {
                        "place_id": place_id,
                        "latitude": latitude,
                        "longitude": longitude,
                        "address": address
                    }
                    
                    create_url = "http://cultureia-geo-api:8002/geo/points"
                    create_response = await client.post(create_url, json=create_point_data)
                    
                    if create_response.status_code in [200, 201]:
                        print(f"Punto creado para lugar {place_id}")
                    else:
                        print(f"Error creando punto para {place_id}: {create_response.status_code}")
                
                except Exception as e:
                    print(f"Error procesando lugar {place_id}: {str(e)}")
                    continue
        
        return {"status": "Ok", "message": "Sincronización completada"}
    
    except Exception as e:
        print(f"Error en sincronización: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al sincronizar puntos: {str(e)}"
        )