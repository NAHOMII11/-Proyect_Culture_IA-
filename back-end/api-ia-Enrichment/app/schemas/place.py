from pydantic import BaseModel
from typing import List


class PlaceIn(BaseModel):
    place_id: str
    name: str
    description: str


class PlaceBatchIn(BaseModel):
    places: List[PlaceIn]


class PlaceOut(BaseModel):
    place_id: str
    name: str
    description: str
    category: str
    tags: List[str]
    confidence: float
    enriched_at: str


class BatchOut(BaseModel):
    enriched: List[PlaceOut]
    total: int