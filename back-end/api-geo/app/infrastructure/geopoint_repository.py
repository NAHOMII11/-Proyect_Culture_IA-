from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.domain.interfaces import IGeoPointRepository
from app.domain.geopoint import GeoPoint


class GeoPointRepository(IGeoPointRepository):

    def create(self, db: Session, geopoint: GeoPoint) -> GeoPoint:
        db.add(geopoint)
        db.commit()
        db.refresh(geopoint)
        return geopoint

    def get_by_place_id(self, db: Session, place_id: UUID) -> Optional[GeoPoint]:
        return db.query(GeoPoint).filter(GeoPoint.place_id == place_id).first()

    def get_all(self, db: Session) -> List[GeoPoint]:
        return db.query(GeoPoint).all()

    def exists_by_place_id(self, db: Session, place_id: UUID) -> bool:
        return (
            db.query(GeoPoint).filter(GeoPoint.place_id == place_id).first()
            is not None
        )