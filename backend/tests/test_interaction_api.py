"""Tests de integración para el endpoint POST /api/v1/interactions.

Usa las fixtures compartidas del conftest:
- `client` con BD en memoria + API_KEY configurada.
- `admin_headers_bearer` para el GET (protegido con JWT).
- El POST conserva `X-Api-Key` (n8n) — NO exige JWT.

Cubre auth (X-Api-Key), idempotencia, validaciones y listado con JWT.
"""
import json

import pytest

from src.main import create_app  # noqa: F401 (mantiene la importación explícita)

# Clave de API que coincide con el default de src.core.auth
TEST_API_KEY = "dev-api-key-123"


# ---------------------------------------------------------------------------
# Auth tests (POST con X-Api-Key)
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


def test_create_interaction_post_sin_jwt_pero_con_api_key(client):
    """El POST no exige Bearer JWT: solo X-Api-Key (flujo n8n intacto)."""
    payload = {
        "source": "api",
        "payload": json.dumps({"text": "n8n"}),
    }
    resp = client.post(
        "/api/v1/interactions/",
        json=payload,
        headers={"X-Api-Key": TEST_API_KEY},
    )
    assert resp.status_code == 201


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
# GET / — Listar interacciones (protegido con JWT)
# ---------------------------------------------------------------------------


def test_list_interactions_without_token_returns_401(client):
    resp = client.get("/api/v1/interactions/")
    assert resp.status_code == 401


def test_list_interactions_empty(client, admin_headers_bearer):
    resp = client.get("/api/v1/interactions/", headers=admin_headers_bearer)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_interactions_returns_newest_first(client, admin_headers_bearer):
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

    resp = client.get("/api/v1/interactions/", headers=admin_headers_bearer)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    # La más nueva (id mayor) debe aparecer primera
    assert data["items"][0]["id"] > data["items"][1]["id"]


def test_list_interactions_pagination(client, admin_headers_bearer):
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

    resp = client.get("/api/v1/interactions/?limit=3&offset=0", headers=admin_headers_bearer)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    assert data["total"] == 10


def test_list_interactions_returns_all_fields(client, admin_headers_bearer):
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

    resp = client.get("/api/v1/interactions/", headers=admin_headers_bearer)
    item = resp.json()["items"][0]
    assert "id" in item
    assert "source" in item
    assert "payload" in item
    assert "user" in item
    assert "intent" in item
    assert "result" in item
    assert "timestamp" in item


# ---------------------------------------------------------------------------
# GET / — Filtro por cliente (client_id)
# ---------------------------------------------------------------------------


def _crear_cliente(client, email, admin_headers_bearer):
    resp = client.post(
        "/api/v1/clients/",
        json={"nombre": "Cliente", "apellido": "Test", "email": email},
        headers=admin_headers_bearer,
    )
    assert resp.status_code in (200, 201)
    return resp.json()["id"]


def _crear_interaccion(client, email, n):
    client.post(
        "/api/v1/interactions/",
        json={
            "source": "api",
            "payload": json.dumps({"n": n}),
            "clientLookup": {"email": email},
        },
        headers={"X-Api-Key": TEST_API_KEY},
    )


def test_list_interactions_filter_by_client(client, admin_headers_bearer):
    """Filtro por client_id devuelve solo sus interacciones con total correcto."""
    c1 = _crear_cliente(client, "filter1@x.com", admin_headers_bearer)
    _crear_cliente(client, "filter2@x.com", admin_headers_bearer)

    _crear_interaccion(client, "filter1@x.com", 1)
    _crear_interaccion(client, "filter1@x.com", 2)
    _crear_interaccion(client, "filter2@x.com", 3)

    resp = client.get(f"/api/v1/interactions/?client_id={c1}", headers=admin_headers_bearer)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert all(item["clientId"] == c1 for item in data["items"])


def test_list_interactions_without_filter_returns_all(client, admin_headers_bearer):
    """Sin filtro mantiene el comportamiento actual (todas las interacciones)."""
    c1 = _crear_cliente(client, "nofilter1@x.com", admin_headers_bearer)
    c2 = _crear_cliente(client, "nofilter2@x.com", admin_headers_bearer)

    _crear_interaccion(client, "nofilter1@x.com", 1)
    _crear_interaccion(client, "nofilter1@x.com", 2)
    _crear_interaccion(client, "nofilter2@x.com", 3)

    resp = client.get("/api/v1/interactions/", headers=admin_headers_bearer)
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_list_interactions_filter_client_without_interactions(client, admin_headers_bearer):
    """Cliente sin interacciones devuelve items vacío y total 0."""
    c1 = _crear_cliente(client, "empty@x.com", admin_headers_bearer)

    resp = client.get(f"/api/v1/interactions/?client_id={c1}", headers=admin_headers_bearer)
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_interactions_filter_nonexistent_client(client, admin_headers_bearer):
    """client_id inexistente devuelve items vacío y total 0."""
    resp = client.get("/api/v1/interactions/?client_id=99999", headers=admin_headers_bearer)
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_interactions_filter_with_pagination(client, admin_headers_bearer):
    """El filtro se combina con limit/offset y el total respeta el filtro."""
    c1 = _crear_cliente(client, "page@x.com", admin_headers_bearer)
    _crear_cliente(client, "page2@x.com", admin_headers_bearer)

    for i in range(25):
        _crear_interaccion(client, "page@x.com", i)
    _crear_interaccion(client, "page2@x.com", 999)

    resp = client.get(f"/api/v1/interactions/?client_id={c1}&limit=10&offset=10", headers=admin_headers_bearer)
    data = resp.json()
    assert len(data["items"]) == 10
    assert data["total"] == 25
    assert all(item["clientId"] == c1 for item in data["items"])