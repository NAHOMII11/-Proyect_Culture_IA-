import os
import httpx
from typing import Optional

GEO_BASE = os.getenv("GEO_SERVICE_URL", "http://cultureia-geo-api:8002")
ANALYTICS_BASE = os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8007")
PLACES_BASE = os.getenv("PLACES_SERVICE_URL", "http://api_place_container:8003")

TIMEOUT = 10.0


async def get_nearby_places(lat: float, lng: float, radius_km: float = 10.0) -> list[dict]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(
            f"{GEO_BASE}/geo/nearby",
            params={"lat": lat, "lng": lng, "radius_km": radius_km},
        )
        resp.raise_for_status()
        places = resp.json()

        enriched = []
        for p in places:
            place_id = p.get("place_id") or p.get("id")
            name = p.get("name", "")

            if not name and place_id:
                try:
                    detail_resp = await client.get(f"{PLACES_BASE}/places/{place_id}")
                    if detail_resp.status_code == 200:
                        name = detail_resp.json().get("name", "")
                except Exception:
                    pass

            p["name"] = name
            p["place_id"] = place_id
            enriched.append(p)

        return enriched


async def get_place_score(place_id: str) -> Optional[float]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            resp = await client.get(f"{ANALYTICS_BASE}/analytics/places/{place_id}/score")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
            raw = float(data.get("score_value", 0.5))
            if raw <= 1.0:
                return raw * 100.0
            return raw
        except Exception:
            return 50.0


async def get_place_detail(place_id: str) -> Optional[dict]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            resp = await client.get(f"{PLACES_BASE}/places/{place_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None


async def get_place_coordinates(place_id: str) -> Optional[dict]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            resp = await client.get(f"{GEO_BASE}/geo/places/{place_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
            return {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            }
        except Exception:
            return None