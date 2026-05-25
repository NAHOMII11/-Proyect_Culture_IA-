import httpx
from typing import Optional

from app.core.config import settings


async def get_recommendations(
    *,
    preferencia: Optional[str] = None,
    max_distancia: float = 5.0,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
) -> list:
    params = {"max_distancia": max_distancia}
    if preferencia:
        params["preferencia"] = preferencia
    if lat is not None:
        params["lat"] = lat
    if lng is not None:
        params["lng"] = lng

    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(
            f"{settings.recommendation_api_url}/recomendaciones",
            params=params,
        )
        response.raise_for_status()
        return response.json()
