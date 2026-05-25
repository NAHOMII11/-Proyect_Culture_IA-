from typing import Optional
from pydantic import BaseModel, Field


class RouteRequestSchema(BaseModel):
    user_lat: float = Field(..., ge=-90, le=90)
    user_lng: float = Field(..., ge=-180, le=180)
    preferred_categories: list[str] = Field(default=[])
    available_time_minutes: int = Field(..., gt=0, le=1440)
    max_places: int = Field(..., gt=0, le=20)

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_lat": 4.6097,
                "user_lng": -74.0817,
                "preferred_categories": ["museo", "monumento"],
                "available_time_minutes": 180,
                "max_places": 4,
            }
        }
    }


class StopSchema(BaseModel):
    place_id: str
    order: int
    name: Optional[str] = None
    distance_from_previous_km: float
    score_value: float
    arrival_estimated: Optional[str] = None
    departure_estimated: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RouteResponseSchema(BaseModel):
    route_id: str
    route_request_id: str
    estimated_duration_minutes: int
    total_places: int
    average_score: float
    places: list[StopSchema]