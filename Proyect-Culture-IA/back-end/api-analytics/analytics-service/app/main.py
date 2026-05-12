from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .infrastructure.database import SessionLocal
from .infrastructure.repository import ScoreRepository
from .domain.logic import calculate_place_score
from .domain.models import ScoringRequest
import json
from fastapi.middleware.cors import CORSMiddleware
import httpx
import random

app = FastAPI(title="CulturalRoute AI - Analytics Service")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def get_ranking():
    """
    Obtiene ranking de lugares ordenados por importance_score:
    1. Consulta la API de places
    2. Elimina duplicados por id
    3. Ordena por importance_score (descendente)
    4. Devuelve con rank, place_id, name, score y level
    """
    try:
        async with httpx.AsyncClient() as client:
            # Obtener lista de lugares
            places_response = await client.get("http://api_place_container:8003/places/")
            places_response.raise_for_status()
            places = places_response.json()
            
            # Eliminar duplicados por id manteniendo el último
            seen_ids = set()
            unique_places = []
            for place in reversed(places):
                if place.get("id") not in seen_ids:
                    seen_ids.add(place.get("id"))
                    unique_places.append(place)
            
            # Invertir para mantener el orden correcto
            unique_places = list(reversed(unique_places))
            
            # Ordenar por importance_score descendente
            sorted_places = sorted(
                unique_places,
                key=lambda x: x.get("importance_score", 0),
                reverse=True
            )
            
            # Mapear a formato de respuesta con ranking
            ranking = []
            for rank, place in enumerate(sorted_places, 1):
                score = place.get("importance_score", 0)
                
                # Determinar nivel basado en score
                if score >= 0.8:
                    level = "excellent"
                elif score >= 0.5:
                    level = "good"
                elif score >= 0.3:
                    level = "fair"
                else:
                    level = "low"
                
                ranking.append({
                    "rank": rank,
                    "place_id": place.get("id"),
                    "name": place.get("name"),
                    "score": score,
                    "level": level
                })
            
            return ranking
    
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error consultando places API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando ranking: {str(e)}")
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

@app.get("/analytics/puntuar")
async def score_all_places(db: Session = Depends(get_db)):
    """
    Endpoint que calcula scores para todos los lugares:
    1. Obtiene lista de lugares desde api-place
    2. Genera variables aleatorias para cada lugar
    3. Envía a /analytics/score
    4. Obtiene scores actualizados desde /analytics/places/{place_id}/score
    5. Actualiza importance_score en api-place
    """
    try:
        async with httpx.AsyncClient() as client:
            # 1. Obtener lista de lugares
            places_response = await client.get("http://api_place_container:8003/places/")
            places_response.raise_for_status()
            places = places_response.json()
            
            results = []
            
            # 2-5. Procesar cada lugar
            for place in places:
                place_id = place.get("id")
                
                try:
                    # Generar variables aleatorias
                    variables = {
                        "visitor_count": random.randint(1000, 10000),
                        "rating": round(random.uniform(1.0, 10.0), 1),
                        "accessibility": round(random.uniform(0.1, 0.9), 1),
                        "cultural_importance": round(random.uniform(0.1, 0.9), 1)
                    }
                    
                    # Enviar a /analytics/score
                    scoring_request = {
                        "place_id": place_id,
                        "variables": variables
                    }
                    
                    score_response = await client.post(
                        "http://analytics-service:8007/analytics/score",
                        json=scoring_request
                    )
                    score_response.raise_for_status()
                    
                    # Obtener score actualizado
                    get_score_response = await client.get(
                        f"http://analytics-service:8007/analytics/places/{place_id}/score"
                    )
                    get_score_response.raise_for_status()
                    score_data = get_score_response.json()
                    
                    score_value = score_data.get("score_value", 0.0)
                    
                    # Actualizar importance_score en api-place
                    patch_response = await client.patch(
                        f"http://api_place_container:8003/places/{place_id}",
                        json={"importance_score": score_value}
                    )
                    patch_response.raise_for_status()
                    
                    results.append({
                        "place_id": place_id,
                        "name": place.get("name"),
                        "score": score_value,
                        "level": score_data.get("level"),
                        "status": "success"
                    })
                
                except Exception as e:
                    results.append({
                        "place_id": place_id,
                        "name": place.get("name"),
                        "status": "error",
                        "error": str(e)
                    })
            
            return {
                "status": "completed",
                "total_places": len(places),
                "processed": len([r for r in results if r.get("status") == "success"]),
                "failed": len([r for r in results if r.get("status") == "error"]),
                "results": results
            }
    
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error comunicándose con servicios externos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando puntuaciones: {str(e)}")

