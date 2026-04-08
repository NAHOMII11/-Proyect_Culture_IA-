from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import random
from database import SessionLocal, Place
from sqlalchemy.orm import Session
from fastapi import Depends

app = FastAPI(title="AI Enrichment Service (Mock)")

# --- Modelos ---
class PlaceIn(BaseModel):
    place_id: str
    name: str
    description: str

class PlaceBatchIn(BaseModel):
    places: List[PlaceIn]

class PlaceOut(BaseModel):
    place_id: str
    name: str
    description: str
    category: str
    tags: List[str]
    confidence: float
    enriched_at: str

class BatchOut(BaseModel):
    enriched: List[PlaceOut]
    total: int

# --- Lógica mock ---
CATEGORIES = [
    ("Museo", ["arte", "historia", "exhibición", "cultura", "educación"], ["museo", "arte", "exhibición", "galería"]),
    ("Parque", ["naturaleza", "aire libre", "familia", "jardín", "recreación"], ["parque", "jardín", "verde", "naturaleza"]),
    ("Restaurante", ["comida", "gastronomía", "servicio", "cocina", "chef"], ["restaurante", "comida", "gastronomía", "cocina"]),
    ("Monumento", ["histórico", "arquitectura", "cultural", "patrimonio"], ["monumento", "histórico", "patrimonio", "escultura"]),
    ("Teatro", ["espectáculo", "cultura", "entretenimiento", "danza", "ópera"], ["teatro", "espectáculo", "danza", "ópera"]),
    ("Iglesia", ["religión", "historia", "arquitectura", "fe"], ["iglesia", "templo", "catedral", "basílica"]),
    ("Mercado", ["comercio", "tradición", "local", "artesanía"], ["mercado", "plaza", "artesanía", "comercio"]),
    ("Lugar Cultural", ["cultura", "evento", "comunidad", "arte"], ["cultural", "evento", "comunidad", "arte"]),
]

def enrich_logic(name: str, description: str):
    text = f"{name} {description}".lower()
    best = None
    max_hits = 0
    for cat, tags, keywords in CATEGORIES:
        hits = sum(1 for kw in keywords if kw in text)
        if hits > max_hits:
            best = (cat, tags, hits)
            max_hits = hits
    if not best:
        best = ("Lugar Cultural", ["cultura", "evento", "comunidad", "arte"], 0)
    category, tags, hits = best
    confidence = round(0.6 + min(hits, 3) * 0.13 + random.uniform(0, 0.14), 2)
    confidence = min(confidence, 1.0)
    return category, tags, confidence

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---
@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-enrichment-service", "timestamp": datetime.utcnow().isoformat()}

@app.post("/enrichments", response_model=PlaceOut)
def enrich_place(place: PlaceIn, db: Session = Depends(get_db)):
    category, tags, confidence = enrich_logic(place.name, place.description)
    enriched_at = datetime.utcnow().isoformat()
    db_place = Place(
        place_id=place.place_id,
        name=place.name,
        description=place.description,
        category=category,
        tags=','.join(tags),
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
        tags=db_place.tags.split(','),
        confidence=db_place.confidence,
        enriched_at=db_place.enriched_at
    )

@app.post("/enrichments/batch", response_model=BatchOut)
def enrich_batch(batch: PlaceBatchIn):
    enriched = [
        enrich_place(place) for place in batch.places
    ]
    return BatchOut(enriched=enriched, total=len(enriched))

@app.get("/places", response_model=List[PlaceOut])
def get_places(db: Session = Depends(get_db)):
    places = db.query(Place).all()
    return [
        PlaceOut(
            place_id=p.place_id,
            name=p.name,
            description=p.description,
            category=p.category,
            tags=p.tags.split(','),
            confidence=p.confidence,
            enriched_at=p.enriched_at
        ) for p in places
    ]
