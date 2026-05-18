from uuid import UUID

from fastapi import Depends

from app.application.errors import AppError
from app.domain.audit_event import (
    AuditEvent,
    AuditEventFilter,
    AuditValidationError,
    create_audit_event,
    normalize_audit_filter,
)
from app.infrastructure.audit_repository import AuditRepository, get_audit_repository


class AuditService:
    """
    Casos de uso Sprint 3 (E14 - Auditoría):
    - Registrar eventos globales del sistema
    - Consultar y filtrar eventos para monitoreo
    """

    def __init__(self, repository: AuditRepository):
        self._repository = repository

    def _validation_error(self, exc: AuditValidationError) -> AppError:
        return AppError(
            message=str(exc),
            error="validation_error",
            status_code=422,
        )

    def prepare_filters(self, filters: AuditEventFilter) -> AuditEventFilter:
        try:
            return normalize_audit_filter(filters)
        except AuditValidationError as exc:
            raise self._validation_error(exc) from exc

    def register_event(
        self,
        event_type: str,
        source_service: str,
        reference_id: str,
        payload_summary: dict,
    ) -> AuditEvent:
        try:
            event = create_audit_event(
                event_type=event_type,
                source_service=source_service,
                reference_id=reference_id,
                payload_summary=payload_summary,
            )
        except AuditValidationError as exc:
            raise self._validation_error(exc) from exc

        return self._repository.create(event)

    def list_events(self, filters: AuditEventFilter) -> list[AuditEvent]:
        safe_filters = self.prepare_filters(filters)
        return self._repository.list_by_filter(safe_filters)

    def get_event(self, event_id: UUID) -> AuditEvent:
        event = self._repository.get_by_id(event_id)
        if not event:
            raise AppError(
                message="Evento de auditoría no encontrado",
                error="not_found",
                status_code=404,
            )
        return event

    def count_events(self, filters: AuditEventFilter) -> int:
        safe_filters = self.prepare_filters(
            AuditEventFilter(
                event_type=filters.event_type,
                source_service=filters.source_service,
                reference_id=filters.reference_id,
                date_from=filters.date_from,
                date_to=filters.date_to,
            )
        )
        return self._repository.count_by_filter(safe_filters)

    def get_summary(self, filters: AuditEventFilter) -> dict:
        safe_filters = self.prepare_filters(
            AuditEventFilter(
                event_type=filters.event_type,
                source_service=filters.source_service,
                reference_id=filters.reference_id,
                date_from=filters.date_from,
                date_to=filters.date_to,
                skip=0,
                limit=100,
            )
        )
        return {
            "total": self._repository.count_by_filter(safe_filters),
            "by_event_type": self._repository.summary_by_field("event_type", safe_filters),
            "by_source_service": self._repository.summary_by_field(
                "source_service", safe_filters
            ),
        }


def get_audit_service(
    repository: AuditRepository = Depends(get_audit_repository),
) -> AuditService:
    return AuditService(repository=repository)
