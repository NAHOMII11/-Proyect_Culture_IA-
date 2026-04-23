from fastapi import APIRouter, Query
from app.core.http_client import get_async_client #cliente de extraccion de contendores 
from app.services.upstreams import UPSTREAM_SERVICES #cliente de mapeo de los contendores

router = APIRouter(prefix="/bff", tags=["bff"])


@router.get("/dashboard")
async def dashboard_summary():
    auth_url = f"{UPSTREAM_SERVICES['v1_auth']}/auth/me"
    geo_url = f"{UPSTREAM_SERVICES['v1_geo']}/geo/distance"
    places_url = f"{UPSTREAM_SERVICES['v1_places']}/places"
    config_url = f"{UPSTREAM_SERVICES['v1_config']}/health"
    quality_url = f"{UPSTREAM_SERVICES['v1_quality']}/imports"
    iaenri_url = f"{UPSTREAM_SERVICES['v1_iaenri']}/v1_iaenri/me"

    async with get_async_client() as client:
        auth_resp = await client.get(auth_url)
        geo_resp = await client.get(geo_url)
        places_resp = await client.get(places_url)
        config_resp = await client.get(config_url)
        quality_resp = await client.get(quality_url)
        iaenri_resp = await client.get(iaenri_url)

    return {
        "profile": auth_resp.json() if auth_resp.content else {},
        "orders": geo_resp.json() if geo_resp.content else {},
        "featured_products": places_resp.json() if places_resp.content else [],
        "profile1": config_resp.json() if config_resp.content else {},
        "profile2": quality_resp.json() if quality_resp.content else {},
        "profile3": iaenri_resp.json() if iaenri_resp.content else {},
    }

@router.get("/dashplaces")
async def dashboard_summary():
    places_url = f"{UPSTREAM_SERVICES['v1_places']}/places/"

    async with get_async_client() as client:
        places_resp = await client.get(places_url)
    
    # Transformar la respuesta para incluir solo los campos deseados
    places_data = places_resp.json() if places_resp.content else []
    
    filtered_places = [
        {
            "id": place.get("id"),
            "name": place.get("name"),
            "description": place.get("description"),
            "category": place.get("category"),
            "address": place.get("address"),
            "imagelink": place.get("imagelink"),
            "status": place.get("status")
        }
        for place in places_data
    ]

    return {
        "featured_products": filtered_places
    }
    
    # ---- S2-H5: lugares cercanos ----
@router.get("/nearby")
async def get_nearby_places(
    lat: float = Query(..., description="Latitud del punto de referencia"),
    lng: float = Query(..., description="Longitud del punto de referencia"),
    radius_km: float = Query(5.0, description="Radio de búsqueda en kilómetros"),
):
    geo_url = (
        f"{UPSTREAM_SERVICES['v1_geo']}/geo/nearby"
        f"?lat={lat}&lng={lng}&radius_km={radius_km}"
    )

    async with get_async_client() as client:
        geo_resp = await client.get(geo_url)

    if geo_resp.status_code != 200:
        return {"nearby_places": [], "total": 0, "radius_km": radius_km}

    geo_results = geo_resp.json()

    # Enriquecer con datos del catálogo
    enriched = []
    async with get_async_client() as client:
        for item in geo_results:
            place_id = item.get("place_id")
            name, category, address, imagelink = None, None, None, None

            try:
                catalog_url = f"{UPSTREAM_SERVICES['v1_places']}/places/{place_id}"
                catalog_resp = await client.get(catalog_url)
                if catalog_resp.status_code == 200:
                    data = catalog_resp.json()
                    name = data.get("name")
                    category = data.get("category")
                    address = data.get("address")
                    imagelink = data.get("imagelink")
            except Exception:
                pass

            enriched.append({
                "place_id": place_id,
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "distance_km": item.get("distance_km"),
                "name": name,
                "category": category,
                "address": address,
                "imagelink": imagelink,
            })

    return {
        "nearby_places": enriched,
        "total": len(enriched),
        "radius_km": radius_km,
        "reference_point": {"lat": lat, "lng": lng},
    }


# ---- S2-H5: distancia entre dos lugares ----
@router.get("/distance")
async def get_distance(
    place_id_origin: str = Query(..., description="UUID del lugar de origen"),
    place_id_destination: str = Query(..., description="UUID del lugar de destino"),
):
    geo_url = (
        f"{UPSTREAM_SERVICES['v1_geo']}/geo/distance"
        f"?place_id_origin={place_id_origin}&place_id_destination={place_id_destination}"
    )

    async with get_async_client() as client:
        geo_resp = await client.get(geo_url)

    return geo_resp.json()