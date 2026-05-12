from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base
from datetime import datetime

class PlaceEntity(Base):
    __tablename__ = "places"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    imagelink = Column(String)
    importance_score = Column(Float, default=0.0)
    tags = Column(JSON)  # Guardaremos la lista de tags como JSON
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)