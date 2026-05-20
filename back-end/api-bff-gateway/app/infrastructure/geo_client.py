import httpx
from app.core.config import settings


async def get_geo_point(place_id: str) -> dict:
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(f"{settings.geo_api_url}/geo/places/{place_id}")
        response.raise_for_status()
        return response.json()
