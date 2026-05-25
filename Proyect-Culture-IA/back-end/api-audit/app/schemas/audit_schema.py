from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.audit_event import AuditEventType


class AuditEventCreate(BaseModel):
    event_type: AuditEventType
    source_service: str = Field(..., min_length=1, max_length=120)
    reference_id: str = Field(..., min_length=1, max_length=255)
    payload_summary: Dict[str, Any] = Field(default_factory=dict)


class AuditEventResponse(BaseModel):
    id: UUID
    event_type: str
    source_service: str
    reference_id: str
    payload_summary: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditSummaryResponse(BaseModel):
    total: int
    by_event_type: Dict[str, int]
    by_source_service: Dict[str, int]


class AuditEventListResponse(BaseModel):
    items: list[AuditEventResponse]
    total: int
    skip: int
    limit: int


class AuditEventTypesResponse(BaseModel):
    event_types: list[str]
