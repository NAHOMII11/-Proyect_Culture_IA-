from uuid import UUID
from sqlalchemy.orm import Session
from app.infrastructure.orm_models import RouteRequestModel, RouteResultModel, RouteStopModel
from app.domain.models import RouteRequest, RouteResult


class RouteRepository:

    def __init__(self, db: Session):
        self.db = db

    def save_request(self, req: RouteRequest) -> RouteRequestModel:
        db_req = RouteRequestModel(
            user_lat=req.user_lat,
            user_lng=req.user_lng,
            preferred_categories=req.preferred_categories,
            available_time_minutes=req.available_time_minutes,
            max_places=req.max_places,
        )
        self.db.add(db_req)
        self.db.commit()
        self.db.refresh(db_req)
        return db_req

    def save_result(self, result: RouteResult, request_id: UUID) -> RouteResultModel:
        db_result = RouteResultModel(
            route_request_id=request_id,
            estimated_duration_minutes=result.estimated_duration_minutes,
            total_places=result.total_places,
            average_score=result.average_score,
        )
        self.db.add(db_result)
        self.db.flush()

        for stop in result.stops:
            db_stop = RouteStopModel(
                route_result_id=db_result.id,
                place_id=stop.place_id,
                stop_order=stop.stop_order,
                distance_from_previous_km=stop.distance_from_previous_km,
                score_value=stop.score_value,
                name=stop.name,
                arrival_estimated=stop.arrival_estimated,
                departure_estimated=stop.departure_estimated,
            )
            self.db.add(db_stop)

        self.db.commit()
        self.db.refresh(db_result)
        return db_result

    def get_result_by_id(self, route_id: UUID) -> RouteResultModel | None:
        return (
            self.db.query(RouteResultModel)
            .filter(RouteResultModel.id == route_id)
            .first()
        )

    def list_results(self, skip: int = 0, limit: int = 20) -> list[RouteResultModel]:
        return (
            self.db.query(RouteResultModel)
            .order_by(RouteResultModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )