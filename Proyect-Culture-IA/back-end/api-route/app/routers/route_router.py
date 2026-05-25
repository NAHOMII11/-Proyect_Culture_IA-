from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.application.use_cases import GenerateRouteUseCase, GetRouteUseCase
from app.infrastructure.repository import RouteRepository
from app.schemas.route_schemas import RouteRequestSchema, RouteResponseSchema, StopSchema

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post("", response_model=RouteResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_route(payload: RouteRequestSchema, db: Session = Depends(get_db)):
    use_case = GenerateRouteUseCase(db)
    return await use_case.execute(payload)


@router.get("/{route_id}", response_model=RouteResponseSchema)
def get_route(route_id: UUID, db: Session = Depends(get_db)):
    use_case = GetRouteUseCase(db)
    result = use_case.execute(route_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ruta con ID {route_id} no encontrada",
        )
    return result


@router.get("", response_model=list[RouteResponseSchema])
def list_routes(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    repo = RouteRepository(db)
    results = repo.list_results(skip=skip, limit=limit)

    return [
        RouteResponseSchema(
            route_id=str(r.id),
            route_request_id=str(r.route_request_id),
            estimated_duration_minutes=r.estimated_duration_minutes,
            total_places=r.total_places,
            average_score=r.average_score,
            places=[
                StopSchema(
                    place_id=s.place_id,
                    order=s.stop_order,
                    name=s.name,
                    distance_from_previous_km=s.distance_from_previous_km,
                    score_value=s.score_value,
                    arrival_estimated=s.arrival_estimated,
                    departure_estimated=s.departure_estimated,
                )
                for s in r.stops
            ],
        )
        for r in results
    ]