from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.application.audit_service import AuditService, get_audit_service
from app.domain.audit_event import EVENT_TYPES, AuditEvent, AuditEventFilter
from app.schemas.audit_schema import (
    AuditEventCreate,
    AuditEventListResponse,
    AuditEventResponse,
    AuditEventTypesResponse,
    AuditSummaryResponse,
)

router = APIRouter(tags=["audit"])


def _to_response(event: AuditEvent) -> AuditEventResponse:
    return AuditEventResponse(
        id=event.id,
        event_type=event.event_type,
        source_service=event.source_service,
        reference_id=event.reference_id,
        payload_summary=event.payload_summary,
        created_at=event.created_at,
    )


def _build_filter(
    event_type: Optional[str],
    source_service: Optional[str],
    reference_id: Optional[str],
    date_from: Optional[datetime],
    date_to: Optional[datetime],
    skip: int,
    limit: int,
) -> AuditEventFilter:
    return AuditEventFilter(
        event_type=event_type,
        source_service=source_service,
        reference_id=reference_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )


@router.post("/audit/events", response_model=AuditEventResponse, status_code=201)
def create_event(
    event: AuditEventCreate,
    service: AuditService = Depends(get_audit_service),
):
    created = service.register_event(
        event_type=event.event_type.value,
        source_service=event.source_service,
        reference_id=event.reference_id,
        payload_summary=event.payload_summary,
    )
    return _to_response(created)


@router.get("/audit/events", response_model=AuditEventListResponse)
def list_events(
    event_type: Optional[str] = Query(None),
    source_service: Optional[str] = Query(None),
    reference_id: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: AuditService = Depends(get_audit_service),
):
    filters = _build_filter(
        event_type, source_service, reference_id, date_from, date_to, skip, limit
    )
    items = service.list_events(filters)
    total = service.count_events(
        AuditEventFilter(
            event_type=filters.event_type,
            source_service=filters.source_service,
            reference_id=filters.reference_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
        )
    )
    return AuditEventListResponse(
        items=[_to_response(item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/audit/events/summary", response_model=AuditSummaryResponse)
def get_summary(
    event_type: Optional[str] = Query(None),
    source_service: Optional[str] = Query(None),
    reference_id: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    service: AuditService = Depends(get_audit_service),
):
    filters = _build_filter(
        event_type, source_service, reference_id, date_from, date_to, 0, 100
    )
    return AuditSummaryResponse(**service.get_summary(filters))


@router.get("/audit/event-types", response_model=AuditEventTypesResponse)
def list_event_types():
    return AuditEventTypesResponse(event_types=list(EVENT_TYPES))


@router.get("/audit/events/{event_id}", response_model=AuditEventResponse)
def get_event(
    event_id: UUID,
    service: AuditService = Depends(get_audit_service),
):
    return _to_response(service.get_event(event_id))
