import math
import os
import uuid
from typing import Optional

import httpx
import pandas as pd
from audit_client import send_audit_event
from fastapi import HTTPException

from db import HistoricalRecommendation, SessionLocal

PLACES_API_URL = os.getenv(
    "PLACES_API_URL",
    "http://api_place_container:8003/places/",
)
DEFAULT_USER_LAT = 4.6097
DEFAULT_USER_LNG = -74.0817


def _in_colombia(lat, lng) -> bool:
    try:
        la, lo = float(lat), float(lng)
    except (TypeError, ValueError):
        return False
    return -4.3 <= la <= 13.5 and -81.8 <= lo <= -66.8


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _normalize_places_dataframe(
    df: pd.DataFrame,
    user_lat: float = DEFAULT_USER_LAT,
    user_lng: float = DEFAULT_USER_LNG,
) -> pd.DataFrame:
    if "place_id" not in df.columns and "id" in df.columns:
        df = df.rename(columns={"id": "place_id"})

    if "score_value" not in df.columns:
        if "importance_score" in df.columns:
            df["score_value"] = df["importance_score"]
        else:
            df["score_value"] = 0.0

    if "distance_km" not in df.columns:
        if "latitude" in df.columns and "longitude" in df.columns:
            df["distance_km"] = df.apply(
                lambda row: _haversine_km(
                    user_lat,
                    user_lng,
                    row["latitude"],
                    row["longitude"],
                )
                if pd.notna(row["latitude"]) and pd.notna(row["longitude"])
                else 999.0,
                axis=1,
            )
        else:
            df["distance_km"] = 1.0

    return df


async def build_recommendations(
    *,
    preferencia: Optional[str] = None,
    max_distancia: float = 5.0,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
) -> list:
    user_lat = lat if lat is not None else DEFAULT_USER_LAT
    user_lng = lng if lng is not None else DEFAULT_USER_LNG

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PLACES_API_URL}?limit=100", timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail="Error al consultar el servicio de lugares (CRUD)",
                )
            places_data = response.json()
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"No se pudo conectar con el servicio de lugares: {exc}",
            )

    if not places_data:
        return []

    places_data = [
        p for p in places_data
        if _in_colombia(p.get("latitude"), p.get("longitude"))
    ]

    if not places_data:
        return []

    try:
        df = pd.DataFrame(places_data)
        df = _normalize_places_dataframe(df, user_lat, user_lng)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la estructura de datos: {e}")

    required_columns = ["place_id", "name", "category", "score_value", "distance_km"]
    for col in required_columns:
        if col not in df.columns:
            raise HTTPException(
                status_code=500,
                detail=f"El servicio CRUD no retornó la columna requerida: {col}",
            )

    df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce").fillna(999.0)
    df = df[df["distance_km"] <= max_distancia]

    if df.empty:
        return []

    df["score_value"] = pd.to_numeric(df["score_value"], errors="coerce").fillna(0.0)

    if preferencia:
        df["match_preference"] = df["category"].str.lower() == preferencia.lower()
    else:
        df["match_preference"] = False

    df["relevance_index"] = (
        (df["score_value"] * 0.7)
        + ((1 / (df["distance_km"] + 0.1)) * 0.2)
        + (df["match_preference"].astype(int) * 0.1)
    )

    df_sorted = df.sort_values(by="relevance_index", ascending=False)

    recommendations = []
    for _, row in df_sorted.iterrows():
        reasons = [
            f"Tiene un excelente puntaje de relevancia cultural configurado en ({row['score_value']})."
        ]

        if row["distance_km"] <= 1.0:
            reasons.append(
                f"Está muy cerca de tu ubicación reportada (a solo {row['distance_km']} km)."
            )
        else:
            reasons.append(
                f"Se encuentra dentro de tu rango de movilidad a {row['distance_km']} km."
            )

        if row["match_preference"]:
            reasons.append(
                f"Coincide explícitamente con tu preferencia guardada para la categoría '{preferencia}'."
            )

        recommendations.append(
            {
                "place_id": str(row["place_id"]),
                "name": row["name"],
                "category": row["category"],
                "relevance_index": round(row["relevance_index"], 2),
                "distance_km": row["distance_km"],
                "explanation": reasons,
            }
        )

    pref_key = (preferencia or "general").lower().replace(" ", "-")

    db = SessionLocal()
    try:
        for rec in recommendations:
            db.add(
                HistoricalRecommendation(
                    id=str(uuid.uuid4()),
                    place_id=str(rec["place_id"]),
                    user_preference=pref_key,
                    relevance_index=rec["relevance_index"],
                    explanation=rec["explanation"],
                )
            )
        db.commit()
    finally:
        db.close()

    send_audit_event(
        event_type="recomendacion_generada",
        source_service="recommendation-service",
        reference_id=f"rec-{pref_key}-{len(recommendations)}",
        payload_summary={
            "preferencia": preferencia,
            "max_distancia": max_distancia,
            "total_recomendaciones": len(recommendations),
        },
    )

    return recommendations
