from fastapi import APIRouter, Depends
from app.application.audit_service import AuditService
from app.infrastructure.audit_repository import AuditRepository
from app.schemas.audit_schema import AuditEventCreate, AuditEventResponse

router = APIRouter()

def get_audit_service():
    repo = AuditRepository()
    return AuditService(repo)

@router.post("/audit/events", response_model=AuditEventResponse, status_code=201)
def create_event(event: AuditEventCreate, service: AuditService = Depends(get_audit_service)):
    created = service.register_event(
        event_type=event.event_type,
        source_service=event.source_service,
        reference_id=event.reference_id,
        payload_summary=event.payload_summary
    )
    return created

@router.get("/audit/events", response_model=list[AuditEventResponse])
def list_events(skip: int = 0, limit: int = 100, service: AuditService = Depends(get_audit_service)):
    return service.get_events(skip, limit)