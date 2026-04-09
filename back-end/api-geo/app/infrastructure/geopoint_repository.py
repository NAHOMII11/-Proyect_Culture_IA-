from sqlalchemy.orm import Session
from app.domain.geopoint import GeoPoint
from uuid import UUID

class GeoPointRepository:

    def create(self, db: Session, geopoint: GeoPoint) -> GeoPoint:
        db.add(geopoint)
        db.commit()
        db.refresh(geopoint)
        return geopoint

    def get_by_place_id(self, db: Session, place_id: UUID):
        return db.query(GeoPoint).filter(GeoPoint.place_id == place_id).first()

    def get_all(self, db: Session):
        return db.query(GeoPoint).all()

    def exists_by_place_id(self, db: Session, place_id: UUID) -> bool:
        return db.query(GeoPoint).filter(GeoPoint.place_id == place_id).first() is not None