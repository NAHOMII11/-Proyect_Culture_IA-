from sqlalchemy.orm import Session
from .entities import PlaceEntity
from ..domain.models import PlaceCreate
from uuid import UUID

class PlaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_place(self, place: PlaceCreate):
        db_place = PlaceEntity(
            name=place.name,
            description=place.description,
            category=place.category,
            latitude=place.latitude,
            longitude=place.longitude,
            importance_score=place.importance_score,
            tags=place.tags,
            status=place.status
        )
        self.db.add(db_place)
        self.db.commit()
        self.db.refresh(db_place)
        return db_place

    # REQUISITO: Listar lugares con paginación
    def get_all_places(self, skip: int = 0, limit: int = 10):
        return self.db.query(PlaceEntity).offset(skip).limit(limit).all()

    # REQUISITO: Consultar un lugar por ID
    def get_by_id(self, place_id: UUID):
        return self.db.query(PlaceEntity).filter(PlaceEntity.id == place_id).first()

    # REQUISITO: Actualizar (PATCH)
    def update_place(self, place_id: UUID, update_data: dict):
        db_place = self.get_by_id(place_id)
        if db_place:
            for key, value in update_data.items():
                if hasattr(db_place, key):
                    setattr(db_place, key, value)
            self.db.commit()
            self.db.refresh(db_place)
        return db_place

    # REQUISITO: Eliminar (DELETE)
    def delete_place(self, place_id: UUID):
        db_place = self.get_by_id(place_id)
        if db_place:
            self.db.delete(db_place)
            self.db.commit()
            return True
        return False