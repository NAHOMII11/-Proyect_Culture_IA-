from fastapi import APIRouter, HTTPException, Request, Response
import httpx

from app.core.config import settings
from app.core.http_client import get_async_client #cliente de extraccion de contendores 
from app.services.upstreams import UPSTREAM_SERVICES #cliente de mapeo de los contendores

router = APIRouter(prefix="/api", tags=["api"]) # define nombre madre del servicio

ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


def _requires_auth(service_name: str, path: str, method: str) -> bool:
    verb = method.upper()
    if verb in {"GET", "OPTIONS", "HEAD"}:
        return False

    if service_name == "v1_quality" and verb == "POST" and path.startswith("imports"):
        return True

    if service_name == "v1_places" and verb in {"POST", "PUT", "PATCH", "DELETE"}:
        return True

    if service_name == "v1_config" and verb in {"POST", "PUT", "PATCH", "DELETE"}:
        return True

    return False


async def _validate_token(request: Request) -> None:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")

    async with get_async_client() as client:
        response = await client.get(
            f"{settings.auth_api_url}/auth/me",
            headers={"Authorization": auth_header},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Token inválido")


@router.api_route("/{service_name}/{path:path}", methods=ALLOWED_METHODS)
async def proxy_request(service_name: str, path: str, request: Request):
    if _requires_auth(service_name, path, request.method):
        await _validate_token(request)

    base_url = UPSTREAM_SERVICES.get(service_name)

    if not base_url:
        raise HTTPException(status_code=404, detail=f"Servicio '{service_name}' no configurado")

    target_url = f"{base_url}/{path}"

    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()
    query_params = dict(request.query_params)

    async with get_async_client() as client:
        upstream_response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=query_params,
            content=body,
        )

    excluded_headers = {"content-encoding", "transfer-encoding", "connection"}
    response_headers = {
        key: value
        for key, value in upstream_response.headers.items()
        if key.lower() not in excluded_headers
    }

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )