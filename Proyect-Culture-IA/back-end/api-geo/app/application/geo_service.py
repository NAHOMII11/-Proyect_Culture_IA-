from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
import math

from app.domain.interfaces import IGeoPointRepository
from app.domain.geopoint import GeoPoint
from app.schemas.geopoint_schema import GeoPointCreate


class GeoService:

    COLOMBIA_LAT_MIN = -4.3
    COLOMBIA_LAT_MAX = 13.5
    COLOMBIA_LNG_MIN = -81.8
    COLOMBIA_LNG_MAX = -66.8

    def __init__(self, repository: IGeoPointRepository):
        self._repository = repository

    def register_point(self, db: Session, data: GeoPointCreate) -> GeoPoint:
        if self._repository.exists_by_place_id(db, data.place_id):
            raise ValueError("Ya existe una coordenada para este lugar")

        new_point = GeoPoint(
            place_id=data.place_id,
            latitude=data.latitude,
            longitude=data.longitude,
            source=data.source,
            geocode_status="validated"
        )
        return self._repository.create(db, new_point)

    def get_by_place_id(self, db: Session, place_id: UUID) -> GeoPoint:
        point = self._repository.get_by_place_id(db, place_id)
        if not point:
            raise ValueError("No se encontraron coordenadas para este lugar")
        return point

    def _in_colombia(self, lat: float, lng: float) -> bool:
        return (
            self.COLOMBIA_LAT_MIN <= lat <= self.COLOMBIA_LAT_MAX
            and self.COLOMBIA_LNG_MIN <= lng <= self.COLOMBIA_LNG_MAX
        )

    def get_nearby(self, db: Session, lat: float, lng: float, radius_km: float) -> List[dict]:
        if not self._in_colombia(lat, lng):
            return []

        all_points = self._repository.get_all(db)
        nearby = []
        for point in all_points:
            point_lat = float(point.latitude)
            point_lng = float(point.longitude)
            if not self._in_colombia(point_lat, point_lng):
                continue

            distance = self._haversine(lat, lng, point_lat, point_lng)
            if distance <= radius_km:
                nearby.append({
                    "place_id": point.place_id,
                    "latitude": float(point.latitude),
                    "longitude": float(point.longitude),
                    "distance_km": round(distance, 3)
                })
        nearby.sort(key=lambda x: x["distance_km"])
        return nearby

    def calculate_distance(self, db: Session, place_id_origin: UUID, place_id_destination: UUID) -> dict:
        origin = self._repository.get_by_place_id(db, place_id_origin)
        if not origin:
            raise ValueError("No se encontraron coordenadas para el lugar de origen")

        destination = self._repository.get_by_place_id(db, place_id_destination)
        if not destination:
            raise ValueError("No se encontraron coordenadas para el lugar de destino")

        distance = self._haversine(
            float(origin.latitude),
            float(origin.longitude),
            float(destination.latitude),
            float(destination.longitude)
        )
        return {
            "place_id_origin": place_id_origin,
            "place_id_destination": place_id_destination,
            "distance_km": round(distance, 3)
        }

    def _haversine(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        R = 6371.0
        lat1_r = math.radians(lat1)
        lat2_r = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c