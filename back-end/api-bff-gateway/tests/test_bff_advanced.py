"""
Tests unitarios – S3-H5 BFF Avanzado
Validan la lógica del aggregator sin levantar servicios reales (mocks con pytest).
"""

import pytest
from unittest.mock import AsyncMock, patch


# ── Catalog aggregator ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_catalog_with_scores_includes_score():
    """El catálogo enriquecido debe incluir score cuando analytics responde."""
    fake_places = [{"id": "uuid-1", "name": "Museo del Oro", "city": "Bogotá"}]
    fake_score = {"score_value": 0.85, "level": "alta", "explanation": []}

    with (
        patch("app.application.catalog_aggregator.place_client.get_places", new=AsyncMock(return_value=fake_places)),
        patch("app.application.catalog_aggregator.analytics_client.get_score", new=AsyncMock(return_value=fake_score)),
    ):
        from app.application.catalog_aggregator import get_catalog_with_scores
        result = await get_catalog_with_scores()

    assert result["total"] == 1
    assert result["data"][0]["score"] == 0.85
    assert result["data"][0]["score_level"] == "alta"


@pytest.mark.asyncio
async def test_catalog_degraded_when_analytics_fails():
    """Si analytics falla, el catálogo igual responde con score=None (modo degradado)."""
    fake_places = [{"id": "uuid-1", "name": "Museo del Oro", "city": "Bogotá"}]

    with (
        patch("app.application.catalog_aggregator.place_client.get_places", new=AsyncMock(return_value=fake_places)),
        patch("app.application.catalog_aggregator.analytics_client.get_score", new=AsyncMock(side_effect=Exception("analytics down"))),
    ):
        from app.application.catalog_aggregator import get_catalog_with_scores
        result = await get_catalog_with_scores()

    assert result["total"] == 1
    assert result["data"][0]["score"] is None       # modo degradado
    assert result["data"][0]["name"] == "Museo del Oro"  # catálogo intacto


@pytest.mark.asyncio
async def test_place_detail_aggregates_all_services():
    """El detalle debe incluir datos de Place + Geo + Analytics."""
    fake_place = {"id": "uuid-1", "name": "Catedral Primada", "city": "Bogotá"}
    fake_geo = {"latitude": 4.598, "longitude": -74.076, "geocode_status": "validated"}
    fake_score = {"score_value": 0.90, "level": "alta", "explanation": []}

    with (
        patch("app.application.catalog_aggregator.place_client.get_place_by_id", new=AsyncMock(return_value=fake_place)),
        patch("app.application.catalog_aggregator.geo_client.get_geo_point", new=AsyncMock(return_value=fake_geo)),
        patch("app.application.catalog_aggregator.analytics_client.get_score", new=AsyncMock(return_value=fake_score)),
    ):
        from app.application.catalog_aggregator import get_place_detail
        result = await get_place_detail("uuid-1")

    assert result["name"] == "Catedral Primada"
    assert result["coordinates"]["latitude"] == 4.598
    assert result["score"] == 0.90


@pytest.mark.asyncio
async def test_place_detail_geo_optional():
    """Si Geo falla, el detalle responde igual con coordinates=None."""
    import httpx
    fake_place = {"id": "uuid-1", "name": "Catedral Primada", "city": "Bogotá"}
    fake_score = {"score_value": 0.90, "level": "alta", "explanation": []}

    with (
        patch("app.application.catalog_aggregator.place_client.get_place_by_id", new=AsyncMock(return_value=fake_place)),
        patch("app.application.catalog_aggregator.geo_client.get_geo_point", new=AsyncMock(side_effect=httpx.ConnectError("geo down"))),
        patch("app.application.catalog_aggregator.analytics_client.get_score", new=AsyncMock(return_value=fake_score)),
    ):
        from app.application.catalog_aggregator import get_place_detail
        result = await get_place_detail("uuid-1")

    assert result["coordinates"] is None    # geo caído → null, no error
    assert result["score"] == 0.90          # analytics igual responde


@pytest.mark.asyncio
async def test_ranking_enriched_with_names():
    """El ranking debe incluir el nombre del lugar junto con su posición."""
    fake_ranking = [
        {"place_id": "uuid-1", "position": 1, "score_value": 0.9},
        {"place_id": "uuid-2", "position": 2, "score_value": 0.7},
    ]
    fake_place_1 = {"id": "uuid-1", "name": "Museo del Oro", "category": "museo", "city": "Bogotá"}
    fake_place_2 = {"id": "uuid-2", "name": "Monserrate", "category": "monumento", "city": "Bogotá"}

    async def mock_get_place(place_id):
        return fake_place_1 if place_id == "uuid-1" else fake_place_2

    with (
        patch("app.application.catalog_aggregator.analytics_client.get_ranking", new=AsyncMock(return_value=fake_ranking)),
        patch("app.application.catalog_aggregator.place_client.get_place_by_id", new=AsyncMock(side_effect=mock_get_place)),
    ):
        from app.application.catalog_aggregator import get_ranking_with_names
        result = await get_ranking_with_names()

    assert result["total"] == 2
    assert result["data"][0]["name"] == "Museo del Oro"
    assert result["data"][1]["name"] == "Monserrate"
