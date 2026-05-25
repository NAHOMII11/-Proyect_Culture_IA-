from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class ChatQueryRequest(BaseModel):
    user_id: str
    query_text: str


class ChatQueryResponse(BaseModel):
    query_id: UUID
    user_id: str
    query_text: str
    response_text: Optional[str] = None
    ai_provider: str
    status: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class ChatQueryListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[ChatQueryResponse]


class HealthResponse(BaseModel):
    status: str
    database: str

