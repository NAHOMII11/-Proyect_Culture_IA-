from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List

# DTO de entrada para registrar coordenadas
class GeoPointCreate(BaseModel):
    place_id: UUID
    latitude: float
    longitude: float
    source: Optional[str] = "manual"

    @field_validator("latitude")
    def validate_latitude(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError("Latitud debe estar entre -90 y 90")
        return v

    @field_validator("longitude")
    def validate_longitude(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError("Longitud debe estar entre -180 y 180")
        return v

# DTO de salida con datos del punto geográfico
class GeoPointResponse(BaseModel):
    id: UUID
    place_id: UUID
    latitude: float
    longitude: float
    geocode_status: str
    source: Optional[str]
    validated_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# DTO de respuesta para lugares cercanos
class NearbyPlaceResponse(BaseModel):
    place_id: UUID
    latitude: float
    longitude: float
    distance_km: float

# DTO de respuesta para cálculo de distancia
class DistanceResponse(BaseModel):
    place_id_origin: UUID
    place_id_destination: UUID
    distance_km: float