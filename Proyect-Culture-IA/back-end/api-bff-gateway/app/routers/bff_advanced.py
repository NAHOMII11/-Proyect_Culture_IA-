"""
S3-H5 – BFF Avanzado
Router principal con los endpoints consolidados del Sprint 3.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query
import httpx

from app.application.catalog_aggregator import (
    get_catalog_with_scores,
    get_place_detail,
    get_ranking_with_names,
)
from app.infrastructure.route_client import create_route, get_route, list_routes
from app.infrastructure.assistant_client import query_assistant
from app.infrastructure.recommendation_client import get_recommendations
from app.schemas.bff_schemas import RouteRequest, AssistantQueryRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bff/v2", tags=["bff-avanzado"])


def _upstream_error(service: str, exc: Exception) -> HTTPException:
    if isinstance(exc, httpx.ConnectError):
        logger.error("Servicio %s no disponible: %s", service, exc)
        return HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": f"El servicio '{service}' no está disponible",
                "service": service,
            },
        )
    if isinstance(exc, httpx.TimeoutException):
        logger.error("Timeout en servicio %s: %s", service, exc)
        return HTTPException(
            status_code=504,
            detail={
                "error": "gateway_timeout",
                "message": f"El servicio '{service}' tardó demasiado en responder",
                "service": service,
            },
        )
    if isinstance(exc, httpx.HTTPStatusError):
        logger.error("Error HTTP %s en servicio %s: %s", exc.response.status_code, service, exc)
        if exc.response.status_code == 404:
            return HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": f"Recurso no encontrado en '{service}'",
                    "service": service,
                },
            )
        return HTTPException(
            status_code=502,
            detail={
                "error": "upstream_error",
                "message": f"Error en servicio '{service}'",
                "service": service,
                "upstream_status": exc.response.status_code,
            },
        )
    logger.exception("Error inesperado en servicio %s", service)
    return HTTPException(
        status_code=502,
        detail={
            "error": "upstream_error",
            "message": f"Error inesperado al consultar '{service}'",
            "service": service,
        },
    )


@router.get(
    "/catalog",
    summary="Catálogo consolidado con score",
    description=(
        "Agrega Place Service + Analytics Service. "
        "Si Analytics no responde, devuelve el catálogo igualmente (modo degradado)."
    ),
)
async def get_catalog():
    try:
        return await get_catalog_with_scores()
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
        raise _upstream_error("place-service", exc)
    except Exception as exc:
        raise _upstream_error("catalog-aggregator", exc)


@router.get(
    "/catalog/{place_id}",
    summary="Detalle de lugar con coordenadas y score",
    description=(
        "Agrega Place Service + Geo Service + Analytics Service en paralelo. "
        "Geo y Analytics son opcionales: si fallan, se devuelven como null."
    ),
)
async def get_place(
    place_id: str = Path(..., description="UUID del lugar cultural"),
):
    try:
        return await get_place_detail(place_id)
    except httpx.HTTPStatusError as exc:
        raise _upstream_error("place-service", exc)
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        raise _upstream_error("place-service", exc)
    except Exception as exc:
        raise _upstream_error("catalog-detail-aggregator", exc)


@router.get(
    "/ranking",
    summary="Ranking de lugares con nombre incluido",
    description=(
        "Consulta Analytics Service para el ranking y enriquece cada "
        "resultado con el nombre del lugar desde Place Service."
    ),
)
async def get_ranking():
    try:
        return await get_ranking_with_names()
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
        raise _upstream_error("analytics-service", exc)
    except Exception as exc:
        raise _upstream_error("ranking-aggregator", exc)


@router.get(
    "/routes",
    summary="Listar rutas generadas",
    description="Delega al Route Service sin exponer su URL al frontend.",
)
async def get_routes():
    try:
        routes = await list_routes()
        return {"data": routes, "total": len(routes)}
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
        raise _upstream_error("route-service", exc)
    except Exception as exc:
        raise _upstream_error("route-service", exc)


@router.get(
    "/routes/{route_id}",
    summary="Detalle de ruta cultural",
)
async def get_route_detail(route_id: str = Path(..., description="UUID de la ruta")):
    try:
        return await get_route(route_id)
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
        raise _upstream_error("route-service", exc)
    except Exception as exc:
        raise _upstream_error("route-service", exc)


@router.post(
    "/routes",
    summary="Generar ruta cultural",
    description=(
        "Recibe preferencias del usuario y delega al Route Service "
        "la generación de la ruta optimizada."
    ),
)
async def post_route(body: RouteRequest):
    try:
        return await create_route(body.model_dump())
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
        raise _upstream_error("route-service", exc)
    except Exception as exc:
        raise _upstream_error("route-service", exc)


@router.get(
    "/recommendations",
    summary="Recomendaciones culturales",
    description="Agrega la consulta al Recommendation Service vía gateway interno.",
)
async def get_recommendations_bff(
    preferencia: Optional[str] = Query(None),
    max_distancia: float = Query(5.0),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
):
    try:
        data = await get_recommendations(
            preferencia=preferencia,
            max_distancia=max_distancia,
            lat=lat,
            lng=lng,
        )
        return {"data": data, "total": len(data)}
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
        raise _upstream_error("recommendation-service", exc)
    except Exception as exc:
        raise _upstream_error("recommendation-service", exc)


@router.post(
    "/assistant/query",
    summary="Consulta al asistente IA",
    description=(
        "Envía la pregunta del usuario al AI Assistant Service, "
        "que construye su respuesta consultando servicios internos reales."
    ),
)
async def post_assistant_query(body: AssistantQueryRequest):
    try:
        return await query_assistant(body.model_dump())
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
        raise _upstream_error("assistant-service", exc)
    except Exception as exc:
        raise _upstream_error("assistant-service", exc)
