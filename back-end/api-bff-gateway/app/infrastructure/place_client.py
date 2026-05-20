import httpx
from app.core.config import settings


async def get_places() -> list[dict]:
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(f"{settings.places_api_url}/places")
        response.raise_for_status()
        return response.json()


async def get_place_by_id(place_id: str) -> dict:
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(f"{settings.places_api_url}/places/{place_id}")
        response.raise_for_status()
        return response.json()
