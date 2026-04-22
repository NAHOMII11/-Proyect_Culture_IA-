from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .infrastructure.database import SessionLocal
from .infrastructure.repository import ScoreRepository
from .domain.logic import calculate_place_score
from .domain.models import ScoringRequest
import json

app = FastAPI(title="CulturalRoute AI - Analytics Service")

# Dependencia para obtener la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/analytics/score")
async def create_score(request: ScoringRequest, db: Session = Depends(get_db)):
    # 1. Lógica de Dominio
    val, level, expl = calculate_place_score(request.variables)
    
    score_data = {
        "place_id": request.place_id,
        "score_value": val,
        "level": level,
        "explanation": json.dumps(expl)
    }
    
    # 2. Persistencia
    repo = ScoreRepository(db)
    repo.save_score(score_data)
    
    return {
        "place_id": request.place_id,
        "score_value": val,
        "level": level,
        "explanation": expl
    }

@app.get("/analytics/places/{place_id}/score")
async def get_score(place_id: str, db: Session = Depends(get_db)):
    repo = ScoreRepository(db)
    result = repo.get_by_id(place_id)
    if not result:
        raise HTTPException(status_code=404, detail="Score no encontrado")
    return {
        "place_id": result.place_id,
        "score_value": result.score_value,
        "level": result.level,
        "explanation": json.loads(result.explanation)
    }

@app.get("/analytics/ranking")
async def get_ranking(db: Session = Depends(get_db)):
    repo = ScoreRepository(db)
    results = repo.get_top_ranking()
    return [
        {
            "place_id": r.place_id,
            "score_value": r.score_value,
            "level": r.level,
            "explanation": json.loads(r.explanation)
        }
        for r in results
    ]

@app.put("/analytics/places/{place_id}/score")
async def update_score(place_id: str, request: ScoringRequest, db: Session = Depends(get_db)):
    # Recalcular score con nuevas variables
    val, level, expl = calculate_place_score(request.variables)
    score_data = {
        "score_value": val,
        "level": level,
        "explanation": json.dumps(expl)
    }
    repo = ScoreRepository(db)
    updated = repo.update_score(place_id, score_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Score no encontrado")
    return {
        "place_id": place_id,
        "score_value": val,
        "level": level,
        "explanation": expl
    }

@app.delete("/analytics/places/{place_id}/score")
async def delete_score_endpoint(place_id: str, db: Session = Depends(get_db)):
    repo = ScoreRepository(db)
    deleted = repo.delete_score(place_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Score no encontrado")
    return {"message": "Score eliminado"}
