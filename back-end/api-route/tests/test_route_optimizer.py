import pytest
from app.domain.route_optimizer import (
    haversine_km,
    combined_score,
    build_route,
    estimate_total_duration,
    MINUTES_PER_STOP,
)

CANDIDATES = [
    {"place_id": "p1", "name": "Museo A",   "latitude": 4.611, "longitude": -74.081, "score_value": 90.0},
    {"place_id": "p2", "name": "Teatro B",  "latitude": 4.615, "longitude": -74.075, "score_value": 70.0},
    {"place_id": "p3", "name": "Plaza C",   "latitude": 4.620, "longitude": -74.070, "score_value": 85.0},
    {"place_id": "p4", "name": "Iglesia D", "latitude": 4.630, "longitude": -74.060, "score_value": 60.0},
]
USER_LAT, USER_LNG = 4.6097, -74.0817


def test_haversine_mismo_punto():
    assert haversine_km(4.6097, -74.0817, 4.6097, -74.0817) == pytest.approx(0.0, abs=0.001)

def test_haversine_bogota_medellin():
    dist = haversine_km(4.7110, -74.0721, 6.2442, -75.5812)
    assert 230 < dist < 260

def test_haversine_positivo():
    dist = haversine_km(4.636, -74.063, 4.650, -74.050)
    assert dist > 0

def test_combined_score_maximo():
    cs = combined_score(100.0, 0.0)
    assert cs == pytest.approx(1.0, abs=0.01)

def test_combined_score_minimo():
    cs = combined_score(0.0, 15.0)
    assert cs == pytest.approx(0.0, abs=0.01)

def test_combined_score_ponderacion():
    cs = combined_score(100.0, 5.0)
    assert cs == pytest.approx(0.8, abs=0.01)

def test_build_route_max_places():
    stops = build_route(CANDIDATES, USER_LAT, USER_LNG, available_time_minutes=300, max_places=2)
    assert len(stops) <= 2

def test_build_route_respeta_tiempo():
    stops = build_route(CANDIDATES, USER_LAT, USER_LNG, available_time_minutes=30, max_places=4)
    assert len(stops) <= 1

def test_build_route_orden_secuencial():
    stops = build_route(CANDIDATES, USER_LAT, USER_LNG, available_time_minutes=300, max_places=4)
    orders = [s.stop_order for s in stops]
    assert orders == list(range(1, len(stops) + 1))

def test_build_route_sin_candidatos():
    stops = build_route([], USER_LAT, USER_LNG, available_time_minutes=300, max_places=4)
    assert stops == []

def test_build_route_no_repite_lugares():
    stops = build_route(CANDIDATES, USER_LAT, USER_LNG, available_time_minutes=300, max_places=4)
    place_ids = [s.place_id for s in stops]
    assert len(place_ids) == len(set(place_ids))

def test_estimate_duration_cero_paradas():
    assert estimate_total_duration([]) == 0

def test_estimate_duration_incluye_visita():
    stops = build_route(CANDIDATES[:1], USER_LAT, USER_LNG, available_time_minutes=300, max_places=1)
    assert estimate_total_duration(stops) >= MINUTES_PER_STOP