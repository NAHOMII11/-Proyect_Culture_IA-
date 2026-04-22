from fastapi import FastAPI
from app.routers import audit
from app.infrastructure.audit_repository import metadata, engine

metadata.create_all(bind=engine)

app = FastAPI(title="Audit Service", description="Servicio de auditoría para CulturalRoute AI")

app.include_router(audit.router)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "audit-service"}