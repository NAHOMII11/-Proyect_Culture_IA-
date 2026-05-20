from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..infrastructure.database import get_db
from ..infrastructure.repository import PlaceRepository
from ..domain.models import Place, PlaceCreate, PlaceUpdate

router = APIRouter(prefix="/places", tags=["Places"])

@router.post("/")
def create_place(place: PlaceCreate, db: Session = Depends(get_db)):
    repo = PlaceRepository(db)
    return repo.create_place(place)

# REQUISITO: GET /places (Paginado)
@router.get("/")
def list_places(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    repo = PlaceRepository(db)
    return repo.get_all_places(skip=skip, limit=limit)

# REQUISITO: GET /places/{id}
@router.get("/{place_id}")
def get_place(place_id: UUID, db: Session = Depends(get_db)):
    repo = PlaceRepository(db)
    place = repo.get_by_id(place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Lugar no encontrado")
    return place

# REQUISITO: PATCH /places/{id}
@router.patch("/{place_id}")
def update_place(place_id: UUID, place_data: PlaceUpdate, db: Session = Depends(get_db)):
    repo = PlaceRepository(db)
    update_dict = place_data.model_dump(exclude_unset=True)
    updated_place = repo.update_place(place_id, update_dict)
    if not updated_place:
        raise HTTPException(status_code=404, detail="No se pudo actualizar, ID no existe")
    return updated_place

@router.delete("/{place_id}")
def delete_place(place_id: UUID, db: Session = Depends(get_db)):
    repo = PlaceRepository(db)
    success = repo.delete_place(place_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lugar no encontrado para borrar")
    return {"detail": "Lugar eliminado correctamente"}