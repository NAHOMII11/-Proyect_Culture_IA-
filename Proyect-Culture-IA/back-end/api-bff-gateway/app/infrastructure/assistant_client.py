import httpx
from app.core.config import settings


async def query_assistant(payload: dict) -> dict:
    user_context = payload.get("user_context") or {}
    body = {
        "user_id": user_context.get("user_id", "bff-user"),
        "query_text": payload.get("question", ""),
    }

    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.post(
            f"{settings.aiassistant_api_url}/aiassistant/chat",
            json=body,
        )
        response.raise_for_status()
        return response.json()
