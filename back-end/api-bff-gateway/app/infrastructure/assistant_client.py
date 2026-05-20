import httpx
from app.core.config import settings


async def query_assistant(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.post(
            f"{settings.assistant_api_url}/assistant/query", json=payload
        )
        response.raise_for_status()
        return response.json()
