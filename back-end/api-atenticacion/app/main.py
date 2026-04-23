from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.infrastructure.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Service - CulturalRoute AI",
    description="Servicio de autenticación y autorización",
    version="1.0.0"
)

app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}