import os
import pandas as pd
import httpx
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

# Guardaremos el historial de recomendaciones entregadas para persistencia si es necesario
class HistoricalRecommendation(Base):
    __tablename__ = "historical_recommendations"
    id = Column(String, primary_key=True)
    place_id = Column(String, index=True)
    user_preference = Column(String)
    relevance_index = Column(Float)
    explanation = Column(JSON)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CulturalRoute AI - Recommendation Service (S2-H2)")

# URL externa del contenedor CRUD de lugares
PLACES_API_URL = "http://api_place_container:8003/places/"

# --- ENDPOINT SOLICITADO: GET /recomendaciones ---
@app.get("/recomendaciones")
async def get_recommendations(
    preferencia: Optional[str] = Query(None, description="Categoría preferida por el usuario (ej: Museo)"),
    max_distancia: Optional[float] = Query(5.0, description="Distancia máxima permitida en kilómetros")
):
    # 1. Consultar de forma dinámica al contenedor del CRUD de lugares
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(PLACES_API_URL, timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Error al consultar el servicio de lugares (CRUD)")
            places_data = response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"No se pudo conectar con el servicio de lugares: {exc}")

    if not places_data:
        return []

    # 2. Cargar los datos obtenidos del CRUD en un DataFrame de Pandas
    try:
        df = pd.DataFrame(places_data)
        
        # Mapeo por si el CRUD usa 'id' en lugar de 'place_id'
        if 'place_id' not in df.columns and 'id' in df.columns:
            df = df.rename(columns={'id': 'place_id'})
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la estructura de datos: {e}")

    # Verificar campos mínimos requeridos para la analítica
    required_columns = ["place_id", "name", "category", "score_value", "distance_km"]
    for col in required_columns:
        if col not in df.columns:
            raise HTTPException(status_code=500, detail=f"El servicio CRUD no retornó la columna requerida: {col}")

    # 3. Criterio de Aceptación: Filtrar por cercanía (distancia máxima) usando Pandas
    df["distance_km"] = pd.to_numeric(df["distance_km"], errors='coerce').fillna(999.0)
    df = df[df["distance_km"] <= max_distancia]

    if df.empty:
        return []

    # 4. Lógica de recomendación con Pandas: Calcular Índice de Relevancia Combinado
    df["score_value"] = pd.to_numeric(df["score_value"], errors='coerce').fillna(0.0)
    
    if preferencia:
        df["match_preference"] = df["category"].str.lower() == preferencia.lower()
    else:
        df["match_preference"] = False
    
    # Algoritmo matemático: 70% peso del scoring, 20% cercanía (inversa de distancia), 10% bonus preferencia
    df["relevance_index"] = (df["score_value"] * 0.7) + ((1 / (df["distance_km"] + 0.1)) * 0.2) + (df["match_preference"].astype(int) * 0.1)
    
    # Ordenar los resultados descendentemente para priorizar la relevancia
    df_sorted = df.sort_values(by="relevance_index", ascending=False)

    # 5. Criterio de Aceptación: Formatear la salida asegurando la Explicabilidad
    recommendations = []
    for _, row in df_sorted.iterrows():
        reasons = [f"Tiene un excelente puntaje de relevancia cultural configurado en ({row['score_value']})."]
        
        if row["distance_km"] <= 1.0:
            reasons.append(f"Está muy cerca de tu ubicación reportada (a solo {row['distance_km']} km).")
        else:
            reasons.append(f"Se encuentra dentro de tu rango de movilidad a {row['distance_km']} km.")
            
        if row["match_preference"]:
            reasons.append(f"Coincide explícitamente con tu preferencia guardada para la categoría '{preferencia}'.")

        recommendations.append({
            "place_id": str(row["place_id"]),
            "name": row["name"],
            "category": row["category"],
            "relevance_index": round(row["relevance_index"], 2),
            "distance_km": row["distance_km"],
            "explanation": reasons
        })

    return recommendations