"""
S3-H5 – BFF Avanzado
Capa de aplicación: agrega respuestas de catálogo + score + geo.
"""

import asyncio
from app.infrastructure import place_client, analytics_client, geo_client


async def get_catalog_with_scores() -> dict:
    places = await place_client.get_places()

    async def _enrich_score(place: dict) -> dict:
        try:
            score_data = await analytics_client.get_score(place["id"])
            place["score"] = score_data.get("score_value")
            place["score_level"] = score_data.get("level")
            place["score_explanation"] = score_data.get("explanation", [])
        except Exception:
            place["score"] = None
            place["score_level"] = None
            place["score_explanation"] = []
        return place

    enriched = await asyncio.gather(*[_enrich_score(p) for p in places])
    return {"data": list(enriched), "total": len(enriched)}


async def get_place_detail(place_id: str) -> dict:
    place_result, geo_result, score_result = await asyncio.gather(
        place_client.get_place_by_id(place_id),
        geo_client.get_geo_point(place_id),
        analytics_client.get_score(place_id),
        return_exceptions=True,
    )

    if isinstance(place_result, Exception):
        raise place_result

    response = dict(place_result)

    if not isinstance(geo_result, Exception):
        response["coordinates"] = {
            "latitude": geo_result.get("latitude"),
            "longitude": geo_result.get("longitude"),
            "geocode_status": geo_result.get("geocode_status"),
        }
    else:
        response["coordinates"] = None

    if not isinstance(score_result, Exception):
        response["score"] = score_result.get("score_value")
        response["score_level"] = score_result.get("level")
        response["score_explanation"] = score_result.get("explanation", [])
    else:
        response["score"] = None
        response["score_level"] = None
        response["score_explanation"] = []

    return response


async def get_ranking_with_names() -> dict:
    ranking = await analytics_client.get_ranking()

    async def _enrich_name(item: dict) -> dict:
        try:
            place = await place_client.get_place_by_id(item["place_id"])
            item["name"] = place.get("name")
            item["category"] = place.get("category")
            item["city"] = place.get("city")
        except Exception:
            item["name"] = None
            item["category"] = None
            item["city"] = None
        return item

    enriched = await asyncio.gather(*[_enrich_name(i) for i in ranking])
    return {"data": list(enriched), "total": len(enriched)}
