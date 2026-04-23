from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime

class PlaceCreate(BaseModel):
    name: str
    description: str
    category: str  # Ejemplo: 'Museo', 'Parque', 'Monumento'
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    imagelink: str
    
    # Campos requeridos para la IA y Analítica según el documento
    importance_score: float = Field(default=0.0, ge=0.0, le=1.0) 
    tags: List[str] = []
    
    # Metadata técnica
    status: str = "active"

class Place(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    category: str  # Ejemplo: 'Museo', 'Parque', 'Monumento'
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    imagelink: str
    
    # Campos requeridos para la IA y Analítica según el documento
    importance_score: float = Field(default=0.0, ge=0.0, le=1.0) 
    tags: List[str] = []
    
    # Metadata técnica
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    imagelink: Optional[str] = None
    importance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None