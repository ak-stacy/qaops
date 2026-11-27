import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health_returns_service_status(client, monkeypatch):
    monkeypatch.setenv("QAOPS_ENV", "test")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok", "environment": "test"}


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [(2, 2, 4), (-3, 5, 2), (1.5, 2.25, 3.75)],
)
def test_sum_returns_result(client, left, right, expected):
    response = client.post("/api/sum", json={"a": left, "b": right})

    assert response.status_code == 200
    assert response.json == {"result": expected}


@pytest.mark.parametrize(
    "payload",
    [None, [], {}, {"a": "2", "b": 3}, {"a": True, "b": 3}, {"a": float("inf"), "b": 3}],
)
def test_sum_rejects_invalid_input(client, payload):
    response = client.post("/api/sum", json=payload)

    assert response.status_code == 400
    assert "error" in response.json
