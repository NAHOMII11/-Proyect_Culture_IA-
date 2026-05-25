from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging

from app.core.config import settings
from app.routers.gateway import router as gateway_router
from app.routers.bff import router as bff_router
from app.routers.bff_advanced import router as bff_advanced_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
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


@app.exception_handler(httpx.ConnectError)
async def connect_error_handler(request: Request, exc: httpx.ConnectError):
    return JSONResponse(
        status_code=503,
        content={
            "error": "service_unavailable",
            "message": "Un servicio interno no está disponible en este momento",
        },
    )


@app.exception_handler(httpx.TimeoutException)
async def timeout_handler(request: Request, exc: httpx.TimeoutException):
    return JSONResponse(
        status_code=504,
        content={
            "error": "gateway_timeout",
            "message": "Un servicio interno tardó demasiado en responder",
        },
    )


app.include_router(gateway_router)
app.include_router(bff_router)
app.include_router(bff_advanced_router)


@app.get("/health", tags=["health"])
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
