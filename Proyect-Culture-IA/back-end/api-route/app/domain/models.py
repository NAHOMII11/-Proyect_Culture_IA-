from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class RouteStop:
    place_id: str
    stop_order: int
    distance_from_previous_km: float
    score_value: float
    name: str = ""
    arrival_estimated: Optional[str] = None
    departure_estimated: Optional[str] = None


@dataclass
class RouteResult:
    id: Optional[UUID]
    route_request_id: UUID
    estimated_duration_minutes: int
    total_places: int
    average_score: float
    stops: list[RouteStop] = field(default_factory=list)
    created_at: Optional[datetime] = None


@dataclass
class RouteRequest:
    id: Optional[UUID]
    user_lat: float
    user_lng: float
    preferred_categories: list[str]
    available_time_minutes: int
    max_places: int
    created_at: Optional[datetime] = None