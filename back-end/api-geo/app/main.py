from fastapi import FastAPI
from app.routers.geo_router import router as geo_router
from app.infrastructure.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Geo Service - CulturalRoute AI",
    description="Servicio de georreferenciación y cálculo de distancias",
    version="1.0.0"
)

app.include_router(geo_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "geo-service"}