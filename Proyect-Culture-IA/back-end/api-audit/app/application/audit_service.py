from app.infrastructure.audit_repository import AuditRepository
from uuid import uuid4
from datetime import datetime

class AuditService:
    def __init__(self, repository: AuditRepository):
        self.repository = repository

    def register_event(self, event_type: str, source_service: str, reference_id: str, payload_summary: dict) -> dict:
        event_id = uuid4()
        now = datetime.utcnow()
        event_data = {
            "id": event_id,
            "event_type": event_type,
            "source_service": source_service,
            "reference_id": reference_id,
            "payload_summary": payload_summary,
            "created_at": now,
        }
        return self.repository.create_event(event_data)

    def get_events(self, skip: int = 0, limit: int = 100) -> list:
        return self.repository.list_events(skip, limit)