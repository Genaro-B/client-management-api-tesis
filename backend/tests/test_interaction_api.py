"""Tests de integración para el endpoint POST /api/v1/interactions.

Usa TestClient de FastAPI para verificar auth, idempotencia y validaciones.
"""
import os
import json

import pytest
from fastapi.testclient import TestClient

from src.main import create_app

# Clave de API que coincide con el default de src.core.auth
TEST_API_KEY = "dev-api-key-123"


@pytest.fixture
def client():
    """Crea una instancia de la aplicación con BD en memoria para cada test."""
    os.environ["API_KEY"] = TEST_API_KEY
    app = create_app()
    # Sobrescribir get_db para usar SQLite en memoria
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from src.database.base import Base
    from src.database.session import get_db

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    test_db = TestSession()

    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Auth tests
# ---------------------------------------------------------------------------


def test_create_interaction_without_api_key(client):
    payload = {
        "source": "telegram",
        "payload": json.dumps({"text": "hello"}),
    }
    resp = client.post("/api/v1/interactions/", json=payload)
    assert resp.status_code == 401
    assert "API key" in resp.json()["detail"]


def test_create_interaction_invalid_api_key(client):
    payload = {
        "source": "telegram",
        "payload": json.dumps({"text": "hello"}),
    }
    resp = client.post(
        "/api/v1/interactions/",
        json=payload,
        headers={"X-Api-Key": "wrong-key"},
    )
    assert resp.status_code == 401
    assert "API key" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Idempotency tests
# ---------------------------------------------------------------------------


def test_create_interaction_with_idempotency(client):
    payload = {
        "source": "telegram",
        "payload": json.dumps({"text": "hello"}),
    }
    resp = client.post(
        "/api/v1/interactions/",
        json=payload,
        headers={
            "X-Api-Key": TEST_API_KEY,
            "X-Idempotency-Key": "tg-99999",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert "timestamp" in data


def test_create_interaction_duplicate_idempotency(client):
    payload = {
        "source": "telegram",
        "payload": json.dumps({"text": "hello"}),
    }
    headers = {
        "X-Api-Key": TEST_API_KEY,
        "X-Idempotency-Key": "tg-88888",
    }

    # First request — should succeed
    resp1 = client.post("/api/v1/interactions/", json=payload, headers=headers)
    assert resp1.status_code == 201

    # Second request with same key — should be 409 Conflict
    resp2 = client.post("/api/v1/interactions/", json=payload, headers=headers)
    assert resp2.status_code == 409
    assert "already exists" in resp2.json()["detail"]


# ---------------------------------------------------------------------------
# Validation tests (auth + idempotency should not break existing validation)
# ---------------------------------------------------------------------------


def test_create_interaction_missing_source(client):
    payload = {
        "source": "",
        "payload": json.dumps({"text": "hello"}),
    }
    resp = client.post(
        "/api/v1/interactions/",
        json=payload,
        headers={"X-Api-Key": TEST_API_KEY},
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET / — Listar interacciones
# ---------------------------------------------------------------------------


def test_list_interactions_empty(client):
    resp = client.get("/api/v1/interactions/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_interactions_returns_newest_first(client):
    """Crea dos interacciones y verifica que vienen ordenadas por id descendente."""
    for i in range(2):
        client.post(
            "/api/v1/interactions/",
            json={
                "source": "api",
                "payload": json.dumps({"msg": f"hello-{i}"}),
            },
            headers={"X-Api-Key": TEST_API_KEY},
        )

    resp = client.get("/api/v1/interactions/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    # La más nueva (id mayor) debe aparecer primera
    assert data["items"][0]["id"] > data["items"][1]["id"]


def test_list_interactions_pagination(client):
    """Crea varias interacciones y verifica limit/offset."""
    for i in range(10):
        client.post(
            "/api/v1/interactions/",
            json={
                "source": "api",
                "payload": json.dumps({"n": i}),
            },
            headers={"X-Api-Key": TEST_API_KEY},
        )

    resp = client.get("/api/v1/interactions/?limit=3&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    assert data["total"] == 10


def test_list_interactions_returns_all_fields(client):
    """Verifica que cada ítem incluya los campos esperados del listado."""
    client.post(
        "/api/v1/interactions/",
        json={
            "source": "telegram",
            "payload": json.dumps({"text": "hola"}),
            "user": "@testuser",
            "intent": "saludo",
            "result": "procesado",
        },
        headers={"X-Api-Key": TEST_API_KEY},
    )

    resp = client.get("/api/v1/interactions/")
    item = resp.json()["items"][0]
    assert "id" in item
    assert "source" in item
    assert "payload" in item
    assert "user" in item
    assert "intent" in item
    assert "result" in item
    assert "timestamp" in item
