import os
import uuid
import pandas as pd
from fastapi import FastAPI, Query, HTTPException
from sqlalchemy import create_engine, Column, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional

# --- CONFIGURACIÓN DE BASE DE DATOS PROPIA ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@db-recommendation:5432/recommendation_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de tabla para almacenar el catálogo de lugares recomendables
class RecommendablePlace(Base):
    __tablename__ = "recommendable_places"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    category = Column(String)       # Ej: "Museo", "Parque", "Histórico"
    score_value = Column(Float)     # Nivel de relevancia que viene de analítica
    distance_km = Column(Float)     # Cercanía simulada

# Crear las tablas automáticamente al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CulturalRoute AI - Recommendation Service (S2-H2)")

# --- POBLAR BASE DE DATOS CON DATOS DE PRUEBA AL INICIAR ---
@app.on_event("startup")
def populate_db():
    db = SessionLocal()
    if db.query(RecommendablePlace).count() == 0:
        test_places = [
            RecommendablePlace(name="Museo del Oro", category="Museo", score_value=0.95, distance_km=1.2),
            RecommendablePlace(name="Plaza de Bolívar", category="Histórico", score_value=0.85, distance_km=0.5),
            RecommendablePlace(name="Parque Nacional", category="Parque", score_value=0.75, distance_km=3.4),
            RecommendablePlace(name="Museo Botero", category="Museo", score_value=0.90, distance_km=0.8),
            RecommendablePlace(name="Teatro Colón", category="Histórico", score_value=0.80, distance_km=1.5),
        ]
        db.add_all(test_places)
        db.commit()
    db.close()

# --- ENDPOINT SOLICITADO: GET /recomendaciones ---
@app.get("/recomendaciones")
def get_recommendations(
    preferencia: Optional[str] = Query(None, description="Categoría preferida por el usuario (ej: Museo)"),
    max_distancia: Optional[float] = Query(5.0, description="Distancia máxima permitida en kilómetros")
):
    db = SessionLocal()
    places = db.query(RecommendablePlace).all()
    db.close()
    
    if not places:
        return []

    # 1. Cargar la información desde Postgres hacia un DataFrame de Pandas
    df = pd.DataFrame([{
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "score_value": p.score_value,
        "distance_km": p.distance_km
    } for p in places])

    # 2. Criterio de Aceptación: Filtrar por cercanía (distancia máxima)
    df = df[df["distance_km"] <= max_distancia]

    if df.empty:
        return []

    # 3. Lógica de recomendación con Pandas: Calcular Índice de Relevancia Combinado
    # Evaluamos si coincide con la preferencia string enviada por el usuario
    df["match_preference"] = df["category"].str.lower() == preferencia.lower() if preferencia else False
    
    # Algoritmo matemático: 70% peso del scoring base, 20% penalización por distancia, 10% bonus si coincide con preferencia
    df["relevance_index"] = (df["score_value"] * 0.7) + ((1 / (df["distance_km"] + 0.1)) * 0.2) + (df["match_preference"].astype(int) * 0.1)
    
    # Ordenar los resultados de forma descendente usando Pandas para priorizar los mejores lugares
    df_sorted = df.sort_values(by="relevance_index", ascending=False)

    # 4. Criterio de Aceptación: Formatear la salida asegurando la Explicabilidad
    recommendations = []
    for _, row in df_sorted.iterrows():
        # Construcción dinámica de la explicación por cada registro
        reasons = [f"Tiene un excelente puntaje de relevancia cultural configurado en ({row['score_value']})."]
        
        if row["distance_km"] <= 1.0:
            reasons.append(f"Está muy cerca de tu ubicación reportada (a solo {row['distance_km']} km).")
        else:
            reasons.append(f"Se encuentra dentro de tu rango de movilidad a {row['distance_km']} km.")
            
        if row["match_preference"]:
            reasons.append(f"Coincide explícitamente con tu preferencia guardada para la categoría '{preferencia}'.")

        recommendations.append({
            "place_id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "relevance_index": round(row["relevance_index"], 2),
            "distance_km": row["distance_km"],
            "explanation": reasons
        })

    return recommendations