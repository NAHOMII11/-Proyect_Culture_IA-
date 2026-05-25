import httpx
from app.core.config import settings


async def create_route(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.post(f"{settings.route_api_url}/routes", json=payload)
        response.raise_for_status()
        return response.json()


async def get_route(route_id: str) -> dict:
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(f"{settings.route_api_url}/routes/{route_id}")
        response.raise_for_status()
        return response.json()


async def list_routes() -> list:
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(f"{settings.route_api_url}/routes")
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
