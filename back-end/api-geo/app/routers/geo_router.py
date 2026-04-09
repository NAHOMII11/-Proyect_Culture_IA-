from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.infrastructure.database import get_db
from app.application.geo_service import GeoService
from app.schemas.geopoint_schema import GeoPointCreate, GeoPointResponse, NearbyPlaceResponse, DistanceResponse
from typing import List

router = APIRouter(prefix="/geo", tags=["Geo"])
geo_service = GeoService()


@router.post("/points", response_model=GeoPointResponse, status_code=201)
def register_point(data: GeoPointCreate, db: Session = Depends(get_db)):
    try:
        point = geo_service.register_point(db, data)
        return point
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/places/{place_id}", response_model=GeoPointResponse)
def get_by_place_id(place_id: UUID, db: Session = Depends(get_db)):
    try:
        point = geo_service.get_by_place_id(db, place_id)
        return point
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/nearby", response_model=List[NearbyPlaceResponse])
def get_nearby(lat: float, lng: float, radius_km: float, db: Session = Depends(get_db)):
    try:
        results = geo_service.get_nearby(db, lat, lng, radius_km)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/distance", response_model=DistanceResponse)
def calculate_distance(place_id_origin: UUID, place_id_destination: UUID, db: Session = Depends(get_db)):
    try:
        result = geo_service.calculate_distance(db, place_id_origin, place_id_destination)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))