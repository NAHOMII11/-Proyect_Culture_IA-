import httpx
from app.core.config import settings


async def get_score(place_id: str) -> dict:
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(
            f"{settings.analytics_api_url}/analytics/places/{place_id}/score"
        )
        response.raise_for_status()
        return response.json()


async def get_ranking() -> list[dict]:
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(f"{settings.analytics_api_url}/analytics/ranking")
        response.raise_for_status()
        return response.json()
