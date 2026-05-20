from app.core.config import settings

    # AQUÍ SE MAPEAN LOS CONTENDORES QUE HAYA O QUE SE VAYAN AGREGANDO
UPSTREAM_SERVICES = {
    "v1_auth": settings.auth_api_url,
    "v1_geo": settings.geo_api_url,
    "v1_places": settings.places_api_url,
    "v1_config": settings.config_api_url,
    "v1_quality": settings.quality_api_url,
    "v1_iaenri": settings.iaenri_api_url,
    "v1_analytics": settings.analytics_api_url,
    "v1_audit": settings.audit_api_url,
    # S3-H5: nuevos servicios
    "v1_routes": settings.route_api_url,
    "v1_assistant": settings.assistant_api_url,
}

