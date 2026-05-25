import httpx
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.audit_client import send_audit_event
from app.domain.models import RouteRequest, RouteResult
from app.domain.route_optimizer import build_route, estimate_total_duration
from app.infrastructure.repository import RouteRepository
from app.infrastructure.service_clients import (
    get_nearby_places,
    get_place_score,
    get_place_detail,
    get_place_coordinates,
)
from app.schemas.route_schemas import RouteRequestSchema, RouteResponseSchema, StopSchema


class GenerateRouteUseCase:

    def __init__(self, db: Session):
        self.repo = RouteRepository(db)

    async def execute(self, data: RouteRequestSchema) -> RouteResponseSchema:
        req = RouteRequest(
            id=None,
            user_lat=data.user_lat,
            user_lng=data.user_lng,
            preferred_categories=data.preferred_categories,
            available_time_minutes=data.available_time_minutes,
            max_places=data.max_places,
        )
        db_req = self.repo.save_request(req)

        try:
            nearby = await get_nearby_places(data.user_lat, data.user_lng, radius_km=15.0)
        except (httpx.RequestError, httpx.HTTPStatusError):
            nearby = []

        candidates = []
        for place in nearby:
            place_id = place.get("place_id") or place.get("id")
            if not place_id:
                continue

            if data.preferred_categories:
                detail = await get_place_detail(str(place_id))
                if detail:
                    cat = (detail.get("category") or "").lower()
                    if not any(pc.lower() in cat for pc in data.preferred_categories):
                        continue
                    place["name"] = detail.get("name", place.get("name", ""))

            score = await get_place_score(str(place_id))

            candidates.append({
                "place_id": str(place_id),
                "name": place.get("name", ""),
                "latitude": float(place.get("latitude", 0)),
                "longitude": float(place.get("longitude", 0)),
                "score_value": score if score is not None else 50.0,
            })

        stops = build_route(
            candidates=candidates,
            user_lat=data.user_lat,
            user_lng=data.user_lng,
            available_time_minutes=data.available_time_minutes,
            max_places=data.max_places,
        )

        duration = estimate_total_duration(stops)
        avg_score = round(sum(s.score_value for s in stops) / len(stops), 2) if stops else 0.0

        result = RouteResult(
            id=None,
            route_request_id=db_req.id,
            estimated_duration_minutes=duration,
            total_places=len(stops),
            average_score=avg_score,
            stops=stops,
        )

        db_result = self.repo.save_result(result, db_req.id)

        send_audit_event(
            event_type="ruta_generada",
            source_service="route-service",
            reference_id=str(db_result.id),
            payload_summary={
                "total_places": len(stops),
                "estimated_duration_minutes": duration,
                "average_score": avg_score,
            },
        )

        stops_with_coords = []
        for stop in stops:
            coords = await get_place_coordinates(stop.place_id)
            stops_with_coords.append(
                StopSchema(
                    place_id=stop.place_id,
                    order=stop.stop_order,
                    name=stop.name,
                    distance_from_previous_km=stop.distance_from_previous_km,
                    score_value=stop.score_value,
                    arrival_estimated=stop.arrival_estimated,
                    departure_estimated=stop.departure_estimated,
                    latitude=coords["latitude"] if coords else None,
                    longitude=coords["longitude"] if coords else None,
                )
            )

        return RouteResponseSchema(
            route_id=str(db_result.id),
            route_request_id=str(db_req.id),
            estimated_duration_minutes=duration,
            total_places=len(stops),
            average_score=avg_score,
            places=stops_with_coords,
        )


class GetRouteUseCase:

    def __init__(self, db: Session):
        self.repo = RouteRepository(db)

    def execute(self, route_id: UUID) -> RouteResponseSchema | None:
        db_result = self.repo.get_result_by_id(route_id)
        if not db_result:
            return None

        return RouteResponseSchema(
            route_id=str(db_result.id),
            route_request_id=str(db_result.route_request_id),
            estimated_duration_minutes=db_result.estimated_duration_minutes,
            total_places=db_result.total_places,
            average_score=db_result.average_score,
            places=[
                StopSchema(
                    place_id=s.place_id,
                    order=s.stop_order,
                    name=s.name,
                    distance_from_previous_km=s.distance_from_previous_km,
                    score_value=s.score_value,
                    arrival_estimated=s.arrival_estimated,
                    departure_estimated=s.departure_estimated,
                    latitude=None,
                    longitude=None,
                )
                for s in db_result.stops
            ],
        )