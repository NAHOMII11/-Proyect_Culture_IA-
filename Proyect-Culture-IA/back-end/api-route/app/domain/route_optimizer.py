import math
from app.domain.models import RouteStop

MINUTES_PER_STOP = 25
WALKING_SPEED_KMH = 4.5


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def travel_minutes(distance_km: float) -> float:
    return (distance_km / WALKING_SPEED_KMH) * 60


def combined_score(analytic_score: float, distance_km: float) -> float:
    norm_score = min(analytic_score / 100.0, 1.0)
    norm_proximity = max(0.0, 1.0 - (distance_km / 10.0))
    return 0.6 * norm_score + 0.4 * norm_proximity


def build_route(
    candidates: list[dict],
    user_lat: float,
    user_lng: float,
    available_time_minutes: int,
    max_places: int,
) -> list[RouteStop]:
    if not candidates:
        return []

    stops: list[RouteStop] = []
    remaining = list(candidates)
    current_lat, current_lng = user_lat, user_lng
    time_used = 0.0
    order = 1

    while remaining and len(stops) < max_places:
        scored = []
        for c in remaining:
            dist = haversine_km(current_lat, current_lng, c["latitude"], c["longitude"])
            travel = travel_minutes(dist)
            time_if_added = time_used + travel + MINUTES_PER_STOP

            if time_if_added > available_time_minutes:
                continue

            cs = combined_score(c.get("score_value", 50.0), dist)
            scored.append((cs, dist, travel, c))

        if not scored:
            break

        scored.sort(key=lambda x: x[0], reverse=True)
        best_cs, best_dist, best_travel, best = scored[0]

        stop = RouteStop(
            place_id=best["place_id"],
            stop_order=order,
            distance_from_previous_km=round(best_dist, 3),
            score_value=round(best["score_value"], 2),
            name=best.get("name", ""),
            arrival_estimated=f"{int(time_used + best_travel)} min desde inicio",
            departure_estimated=f"{int(time_used + best_travel + MINUTES_PER_STOP)} min desde inicio",
        )
        stops.append(stop)

        time_used += best_travel + MINUTES_PER_STOP
        current_lat = best["latitude"]
        current_lng = best["longitude"]
        remaining.remove(best)
        order += 1

    return stops


def estimate_total_duration(stops: list[RouteStop]) -> int:
    total_travel = sum(travel_minutes(s.distance_from_previous_km) for s in stops)
    total_visit = MINUTES_PER_STOP * len(stops)
    return int(total_travel + total_visit)