from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.application.errors import AppError
from app.infrastructure.audit_repository import init_tables
from app.routers import audit


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_tables()
    yield


app = FastAPI(
    title="Audit Service",
    description="Trazabilidad funcional - CulturalRoute AI",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


app.include_router(audit.router)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "audit-service"}
