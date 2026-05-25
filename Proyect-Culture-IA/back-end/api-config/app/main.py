import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.application.errors import AppError
from app.infrastructure.settings import settings
from app.infrastructure.database import Base, SessionLocal, engine
from app.infrastructure.seed import seed_if_empty
from app.routers import config as config_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if os.getenv("SKIP_DB_BOOTSTRAP", "").lower() in ("1", "true", "yes"):
        yield
        return
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_if_empty(session)
    yield


app = FastAPI(title=settings.app_title, lifespan=lifespan)


@app.exception_handler(AppError)
async def app_error_handler(_request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "La solicitud no cumple el esquema esperado.",
            "details": exc.errors(),
        },
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "config"}


@app.get("/")
def root():
    return {"status": "CulturalRoute AI - Config Service activo"}


app.include_router(config_router.router, prefix="/config")
