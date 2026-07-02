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
