import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base


class RouteRequestModel(Base):
    __tablename__ = "route_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_lat = Column(Float, nullable=False)
    user_lng = Column(Float, nullable=False)
    preferred_categories = Column(JSON, nullable=False, default=list)
    available_time_minutes = Column(Integer, nullable=False)
    max_places = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("RouteResultModel", back_populates="request", cascade="all, delete-orphan")


class RouteResultModel(Base):
    __tablename__ = "route_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_request_id = Column(UUID(as_uuid=True), ForeignKey("route_requests.id"), nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=False)
    total_places = Column(Integer, nullable=False)
    average_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("RouteRequestModel", back_populates="results")
    stops = relationship("RouteStopModel", back_populates="result", order_by="RouteStopModel.stop_order", cascade="all, delete-orphan")


class RouteStopModel(Base):
    __tablename__ = "route_stops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_result_id = Column(UUID(as_uuid=True), ForeignKey("route_results.id"), nullable=False)
    place_id = Column(String, nullable=False)
    stop_order = Column(Integer, nullable=False)
    distance_from_previous_km = Column(Float, nullable=False, default=0.0)
    score_value = Column(Float, nullable=False, default=0.0)
    name = Column(String, nullable=True)
    arrival_estimated = Column(String, nullable=True)
    departure_estimated = Column(String, nullable=True)

    result = relationship("RouteResultModel", back_populates="stops")