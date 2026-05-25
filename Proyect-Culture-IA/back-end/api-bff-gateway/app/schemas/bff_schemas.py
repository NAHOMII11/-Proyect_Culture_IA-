from pydantic import BaseModel, Field
from typing import Optional


class CatalogPlaceOut(BaseModel):
    id: str
    name: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    score: Optional[float] = None
    score_level: Optional[str] = None

    class Config:
        extra = "allow"


class RouteRequest(BaseModel):
    user_lat: float = Field(..., description="Latitud del usuario")
    user_lng: float = Field(..., description="Longitud del usuario")
    preferred_categories: list[str] = Field(
        default=[], description="Categorías preferidas (ej: museo, monumento)"
    )
    available_time_minutes: int = Field(
        default=180, description="Tiempo disponible en minutos"
    )
    max_places: int = Field(default=4, description="Número máximo de lugares")


class AssistantQueryRequest(BaseModel):
    question: str = Field(..., description="Pregunta del usuario al asistente")
    user_context: Optional[dict] = Field(
        default=None, description="Contexto del usuario (lat, lng, user_id, etc.)"
    )
