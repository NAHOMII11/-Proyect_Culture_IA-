from fastapi import FastAPI
from app.infrastructure.database import Base, engine
from app.infrastructure.orm_models import RouteRequestModel, RouteResultModel, RouteStopModel  # noqa: F401
from app.routers.route_router import router as route_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CulturalRoute AI - Route Service",
    version="1.0.0",
)

app.include_router(route_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "route-service"}


@app.get("/")
def root():
    return {"service": "route-service", "version": "1.0.0"}