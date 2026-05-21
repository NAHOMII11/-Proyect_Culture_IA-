from sqlalchemy import Column, Integer, String, Float, Text
from app.db.base import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    tags = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    enriched_at = Column(String, nullable=False)