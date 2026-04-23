from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

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