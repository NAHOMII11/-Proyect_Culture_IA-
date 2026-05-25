from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class AuditEventType(str, Enum):
    """Catálogo Sprint 3 (E14) — trazabilidad funcional global."""

    IMPORT_BATCH_PROCESSED = "importacion_procesada"
    PLACE_ENRICHED = "lugar_enriquecido"
    SCORE_CALCULATED = "puntuacion_calculada"
    ROUTE_GENERATED = "ruta_generada"
    ASSISTANT_INTERACTION = "consulta_asistente"
    COORDINATES_ASSIGNED = "coordenadas_asignadas"
    PLACE_CREATED = "lugar_creado"
    RECOMMENDATION_GENERATED = "recomendacion_generada"


EVENT_TYPES = tuple(event_type.value for event_type in AuditEventType)


class AuditValidationError(ValueError):
    pass


@dataclass
class AuditEvent:
    id: UUID
    event_type: str
    source_service: str
    reference_id: str
    payload_summary: dict
    created_at: datetime


@dataclass(frozen=True)
class AuditEventFilter:
    event_type: Optional[str] = None
    source_service: Optional[str] = None
    reference_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    skip: int = 0
    limit: int = 100


def _normalize_event_type(event_type: str) -> str:
    normalized = (event_type or "").strip()
    if not normalized:
        raise AuditValidationError("event_type es obligatorio")
    if normalized not in EVENT_TYPES:
        allowed = ", ".join(EVENT_TYPES)
        raise AuditValidationError(
            f"event_type inválido: '{normalized}'. Valores permitidos: {allowed}"
        )
    return normalized


def normalize_audit_filter(filters: AuditEventFilter) -> AuditEventFilter:
    """Valida filtros de consulta (dominio)."""
    event_type = filters.event_type
    if event_type is not None:
        stripped_type = event_type.strip()
        if not stripped_type:
            event_type = None
        else:
            event_type = _normalize_event_type(stripped_type)

    if filters.date_from and filters.date_to and filters.date_from > filters.date_to:
        raise AuditValidationError("date_from no puede ser posterior a date_to")

    return AuditEventFilter(
        event_type=event_type,
        source_service=(filters.source_service or "").strip() or None,
        reference_id=(filters.reference_id or "").strip() or None,
        date_from=filters.date_from,
        date_to=filters.date_to,
        skip=max(filters.skip, 0),
        limit=min(max(filters.limit, 1), 500),
    )


def create_audit_event(
    event_type: str,
    source_service: str,
    reference_id: str,
    payload_summary: dict[str, Any],
) -> AuditEvent:
    """Factory: valida reglas de negocio antes de persistir (dominio)."""
    normalized_type = _normalize_event_type(event_type)
    normalized_source = (source_service or "").strip()
    normalized_reference = (reference_id or "").strip()

    if not normalized_source:
        raise AuditValidationError("source_service es obligatorio")
    if not normalized_reference:
        raise AuditValidationError("reference_id es obligatorio")
    if not isinstance(payload_summary, dict):
        raise AuditValidationError("payload_summary debe ser un objeto JSON")

    return AuditEvent(
        id=uuid4(),
        event_type=normalized_type,
        source_service=normalized_source,
        reference_id=normalized_reference,
        payload_summary=payload_summary,
        created_at=datetime.now(timezone.utc),
    )
