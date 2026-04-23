from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
    return save_enrichment(place, db)


@router.post("/batch", response_model=BatchOut)
def enrich_batch(batch: PlaceBatchIn, db: Session = Depends(get_db)):
    enriched: List[PlaceOut] = [save_enrichment(place, db) for place in batch.places]
    return BatchOut(enriched=enriched, total=len(enriched))