from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class AuditEvent:
    id: UUID
    event_type: str
    source_service: str
    reference_id: str
    payload_summary: dict
    created_at: datetime