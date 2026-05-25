from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from uuid import UUID
from typing import Optional

from app.infrastructure.database import init_db, get_db
from app.application.schemas import (
    ChatQueryRequest,
    ChatQueryResponse,
    ChatQueryListResponse,
    HealthResponse,
)
from app.application.services import AIAssistantService
from openai import OpenAIError

app = FastAPI(title="CulturalRoute AI - Assistant Service")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/aiassistant/chat", response_model=ChatQueryResponse)
def create_chat(
    request: ChatQueryRequest,
    db: Session = Depends(get_db),
) -> ChatQueryResponse:
    service = AIAssistantService(db)
    try:
        result = service.process_query(
            user_id=request.user_id,
            query_text=request.query_text,
        )
    except OpenAIError as exc:
        error_msg = str(exc)
        # Provide more helpful error messages
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise HTTPException(
                status_code=401, 
                detail="Invalid Groq API key. Check your GROQ_API_KEY in .env"
            )
        elif "405" in error_msg or "Method Not Allowed" in error_msg:
            raise HTTPException(
                status_code=405, 
                detail="Groq API error. Verify your API key is valid."
            )
        else:
            raise HTTPException(status_code=502, detail=f"Groq error: {error_msg}")
    return ChatQueryResponse(**result)


@app.get("/aiassistant/chat/{query_id}", response_model=ChatQueryResponse)
def get_chat(
    query_id: UUID,
    db: Session = Depends(get_db),
) -> ChatQueryResponse:
    service = AIAssistantService(db)
    result = service.get_query(query_id)
    if not result:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    return ChatQueryResponse(**result)


@app.get("/aiassistant/chat", response_model=ChatQueryListResponse)
def list_chat(
    user_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ChatQueryListResponse:
    service = AIAssistantService(db)
    result = service.list_queries(user_id=user_id, skip=skip, limit=limit)
    return ChatQueryListResponse(**result)


@app.get("/aiassistant/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database not connected")
    return HealthResponse(status="healthy", database="connected")

