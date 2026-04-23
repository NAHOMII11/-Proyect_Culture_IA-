from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.router import router
from src.infrastructure.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="CulturalRoute AI - Place Service",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/")
def root():
    return {"status": "Microservicio de Lugares Activo"}