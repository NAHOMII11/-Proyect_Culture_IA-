from sqlalchemy.orm import Session

from app.infrastructure.models import ConfigParameterORM


_DEFAULT_ROWS: list[tuple[str, str, str]] = [
    (
        "scoring.weights",
        '{"data_quality":0.3,"cultural_relevance":0.4,"accessibility":0.3}',
        "Pesos del scoring por variable (JSON).",
    ),
    (
        "geo.proximity_radius_meters",
        "500",
        "Radio por defecto para búsqueda de lugares cercanos (metros).",
    ),
    (
        "route.max_places_default",
        "6",
        "Máximo de lugares sugeridos por ruta si el cliente no envía otro valor.",
    ),
    (
        "catalog.enabled_categories",
        '["museo","monumento","iglesia","plaza","teatro"]',
        "Lista JSON de categorías habilitadas en recomendaciones y rutas.",
    ),
]


def seed_if_empty(session: Session) -> None:
    count = session.query(ConfigParameterORM).count()
    if count > 0:
        return
    for key, value, description in _DEFAULT_ROWS:
        session.add(
            ConfigParameterORM(
                config_key=key,
                config_value=value,
                description=description,
            )
        )
    session.commit()
