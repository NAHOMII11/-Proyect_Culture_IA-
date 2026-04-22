from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit_client import send_audit_event
from app.core.enrichment import enrich_logic
from app.db.models import Place
from app.db.session import get_db
from app.schemas.place import PlaceIn, PlaceOut, PlaceBatchIn, BatchOut

router = APIRouter(prefix="/enrichments", tags=["enrichments"])


def save_enrichment(place: PlaceIn, db: Session) -> PlaceOut:
    existing = db.query(Place).filter(Place.place_id == place.place_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="place_id already exists")

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