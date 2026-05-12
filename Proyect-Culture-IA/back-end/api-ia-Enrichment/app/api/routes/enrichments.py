from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.core.audit_client import send_audit_event
from app.core.enrichment import enrich_logic
from app.db.models import Place
from app.db.session import get_db
from app.schemas.place import PlaceIn, PlaceOut, PlaceBatchIn, BatchOut

router = APIRouter(prefix="/enrichments", tags=["enrichments"])


def save_enrichment(place: PlaceIn, db: Session) -> PlaceOut:
    existing = db.query(Place).filter(Place.place_id == place.place_id).first()
    if existing:
        # Si ya existe, devolverlo como está (idempotente)
        return PlaceOut(
            place_id=existing.place_id,
            name=existing.name,
            description=existing.description,
            category=existing.category,
            tags=existing.tags.split(","),
            confidence=existing.confidence,
            enriched_at=existing.enriched_at
        )

    category, tags, confidence = enrich_logic(place.name, place.description)
    enriched_at = datetime.utcnow().isoformat()

    db_place = Place(
        place_id=place.place_id,
        name=place.name,
        description=place.description,
        category=category,
        tags=",".join(tags),
        confidence=confidence,
        enriched_at=enriched_at
    )

    db.add(db_place)
    db.commit()
    db.refresh(db_place)

    return PlaceOut(
        place_id=db_place.place_id,
        name=db_place.name,
        description=db_place.description,
        category=db_place.category,
        tags=db_place.tags.split(","),
        confidence=db_place.confidence,
        enriched_at=db_place.enriched_at
    )


@router.post("", response_model=PlaceOut)
def enrich_place(place: PlaceIn, db: Session = Depends(get_db)):
    enriched = save_enrichment(place, db)
    send_audit_event(
        event_type="lugar enriquecido",
        source_service="ai-enrichment-service",
        reference_id=enriched.place_id,
        payload_summary={
            "normalized_category": enriched.category,
            "labels": enriched.tags,
            "confidence": enriched.confidence,
        },
    )
    return enriched


@router.post("/batch", response_model=BatchOut)
def enrich_batch(batch: PlaceBatchIn, db: Session = Depends(get_db)):
    enriched: List[PlaceOut] = [save_enrichment(place, db) for place in batch.places]
    for item in enriched:
        send_audit_event(
            event_type="lugar enriquecido",
            source_service="ai-enrichment-service",
            reference_id=item.place_id,
            payload_summary={
                "normalized_category": item.category,
                "labels": item.tags,
                "confidence": item.confidence,
            },
        )
    return BatchOut(enriched=enriched, total=len(enriched))


@router.get("/enriquecer")
async def orquestar_enriquecimiento():
    """
    Orquesta el enriquecimiento completo de lugares:
    
    1. Obtiene todos los lugares del catálogo
    2. Enriquece cada uno individualmente
    3. Enriquece en batch
    4. Consulta enriquecimientos por lugar
    5. Actualiza tags en el catálogo
    6. Retorna OK
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Obtener todos los lugares del catálogo
            places_response = await client.get("http://api_place_container:8003/places/")
            places_response.raise_for_status()
            places = places_response.json()
        
        if not places:
            return {"status": "Ok", "message": "No hay lugares para enriquecer"}
        
        # 2-3. Enriquecer individualmente y recolectar para batch
        enriched_places = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for place in places:
                place_id = place.get("id")
                name = place.get("name")
                description = place.get("description", "")
                category = place.get("category", "")
                address = place.get("address", "")
                
                if not place_id or not name:
                    continue
                
                try:
                    # POST individual a /enrichments
                    enrich_data = {
                        "place_id": place_id,
                        "name": name,
                        "description": description,
                        "category": category,
                        "address": address
                    }
                    
                    enrich_response = await client.post(
                        "http://ai-enrichment-api:8006/enrichments",
                        json=enrich_data
                    )
                    
                    if enrich_response.status_code in [200, 201]:
                        enriched = enrich_response.json()
                        enriched_places.append(enriched)
                        print(f"Enriquecido individualmente: {place_id}")
                    else:
                        print(f"Error enriqueciendo {place_id}: {enrich_response.status_code}")
                
                except Exception as e:
                    print(f"Error procesando lugar {place_id}: {str(e)}")
                    continue
            
            # POST batch
            if enriched_places:
                try:
                    batch_data = {"places": enriched_places}
                    batch_response = await client.post(
                        "http://ai-enrichment-api:8006/enrichments/batch",
                        json=batch_data
                    )
                    print(f"Batch response: {batch_response.status_code}")
                except Exception as e:
                    print(f"Error en batch: {str(e)}")
            
            # 4. Consultar enriquecimientos y actualizar tags en catálogo
            updated_count = 0
            not_found_count = 0
            error_count = 0
            
            for place in places:
                place_id = place.get("id")
                if not place_id:
                    continue
                
                try:
                    # GET /enrichments/{place_id}
                    get_response = await client.get(
                        f"http://ai-enrichment-api:8006/enrichments/{place_id}"
                    )
                    
                    if get_response.status_code == 200:
                        enrichment = get_response.json()
                        tags = enrichment.get("tags", [])
                        
                        # 5. PATCH a places para actualizar tags
                        patch_data = {
                            "name": place.get("name"),
                            "tags": tags
                        }
                        
                        patch_response = await client.patch(
                            f"http://api_place_container:8003/places/{place_id}",
                            json=patch_data
                        )
                        
                        print(f"DEBUG PATCH {place_id}:")
                        print(f"  Status: {patch_response.status_code}")
                        print(f"  Request body: {patch_data}")
                        try:
                            print(f"  Response body: {patch_response.json()}")
                        except:
                            print(f"  Response text: {patch_response.text}")
                        
                        if patch_response.status_code in [200, 204]:
                            # Verificar inmediatamente que persiste
                            import asyncio
                            await asyncio.sleep(0.1)
                            
                            verify_response = await client.get(
                                f"http://api_place_container:8003/places/{place_id}"
                            )
                            
                            if verify_response.status_code == 200:
                                verified_place = verify_response.json()
                                verified_tags = verified_place.get("tags", [])
                                print(f"  ✓ Verificación GET: tags persistidos = {verified_tags}")
                                if verified_tags == tags:
                                    print(f"✓ Tags actualizados CORRECTAMENTE para {place_id}: {tags}")
                                    updated_count += 1
                                else:
                                    print(f"✗ MISMATCH: Enviamos {tags}, pero en BD tiene {verified_tags}")
                                    error_count += 1
                            else:
                                print(f"✗ Error verificando GET {place_id}: {verify_response.status_code}")
                                error_count += 1
                        else:
                            print(f"✗ Error actualizando tags {place_id}: {patch_response.status_code}")
                            error_count += 1
                    else:
                        print(f"✗ Enriquecimiento no encontrado (GET 404) para {place_id}")
                        not_found_count += 1
                
                except Exception as e:
                    print(f"✗ Error procesando {place_id}: {str(e)}")
                    error_count += 1
                    continue
            
            print(f"\n=== Resumen ===")
            print(f"Total lugares: {len(places)}")
            print(f"Tags actualizados: {updated_count}")
            print(f"No encontrados en enrichment: {not_found_count}")
            print(f"Errores: {error_count}")
        
        return {
            "status": "Ok", 
            "message": "Enriquecimiento completado",
            "total": len(places),
            "updated": updated_count,
            "not_found": not_found_count,
            "errors": error_count
        }
    
    except Exception as e:
        print(f"Error en orquestación: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al enriquecer: {str(e)}"
        )


@router.get("/{place_id}", response_model=PlaceOut)
def get_enrichment(place_id: str, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.place_id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="place_id not found")

    return PlaceOut(
        place_id=place.place_id,
        name=place.name,
        description=place.description,
        category=place.category,
        tags=place.tags.split(","),
        confidence=place.confidence,
        enriched_at=place.enriched_at,
    )