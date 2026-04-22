from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Dict, Any

class AuditEventCreate(BaseModel):
    event_type: str
    source_service: str
    reference_id: str
    payload_summary: Dict[str, Any]

class AuditEventResponse(BaseModel):
    id: UUID
    event_type: str
    source_service: str
    reference_id: str
    payload_summary: Dict[str, Any]
    created_at: datetime