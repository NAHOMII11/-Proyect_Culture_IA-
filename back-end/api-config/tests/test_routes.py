import pytest


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "config"


def test_list_parameters_empty(client):
    r = client.get("/config/parameters")
    assert r.status_code == 200
    assert r.json() == []


def test_create_and_get_by_key(client):
    payload = {
        "config_key": "test.demo",
        "config_value": "42",
        "description": "demo",
    }
    r = client.post("/config/parameters", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["config_key"] == "test.demo"
    assert data["config_value"] == "42"

    r2 = client.get("/config/parameters/by-key/test.demo")
    assert r2.status_code == 200
    assert r2.json()["config_value"] == "42"


def test_create_duplicate_returns_409(client):
    body = {"config_key": "dup.key", "config_value": "1", "description": None}
    assert client.post("/config/parameters", json=body).status_code == 201
    r = client.post("/config/parameters", json=body)
    assert r.status_code == 409
    err = r.json()
    assert err["error"] == "conflict"


def test_get_unknown_key_404(client):
    r = client.get("/config/parameters/by-key/no.existe")
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"


@pytest.mark.parametrize(
    "payload",
    [
        {"config_key": "", "config_value": "x", "description": None},
        {"config_key": "_invalid", "config_value": "x", "description": None},
    ],
)
def test_validation_error_shape(client, payload):
    r = client.post("/config/parameters", json=payload)
    assert r.status_code == 422
    body = r.json()
    assert body["error"] == "validation_error"
    assert "details" in body
