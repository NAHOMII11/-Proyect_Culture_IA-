from app.core.config import settings

    # AQUÍ SE MAPEAN LOS CONTENDORES QUE HAYA O QUE SE VAYAN AGREGANDO
UPSTREAM_SERVICES = {
    "v1_auth": settings.auth_api_url,  
    "v1_geo": settings.geo_api_url,  
    "v1_places": settings.places_api_url,
    "v1_config": settings.config_api_url,
    "v1_quality": settings.quality_api_url,
    "v1_iaenri": settings.iaenri_api_url,
}