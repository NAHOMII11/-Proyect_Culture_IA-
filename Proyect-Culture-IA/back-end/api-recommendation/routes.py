from typing import Optional

from fastapi import APIRouter, Query

from recommendation_service import build_recommendations

router = APIRouter(tags=["recomendaciones"])


@router.get("/recomendaciones/health")
async def health_check():
    return {"status": "healthy", "service": "recommendation-api"}


@router.get("/recomendaciones")
async def get_recommendations(
    preferencia: Optional[str] = Query(
        None, description="Categoría preferida por el usuario (ej: Museo)"
    ),
    max_distancia: Optional[float] = Query(
        5.0, description="Distancia máxima permitida en kilómetros"
    ),
    lat: Optional[float] = Query(None, description="Latitud del usuario"),
    lng: Optional[float] = Query(None, description="Longitud del usuario"),
):
    return await build_recommendations(
        preferencia=preferencia,
        max_distancia=max_distancia,
        lat=lat,
        lng=lng,
    )
