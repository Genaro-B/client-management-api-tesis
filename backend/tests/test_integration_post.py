"""Test de integración para endpoint POST /api/v1/clients.

Reescrito sobre las fixtures compartidas de conftest.py:
- `client`: app real + BD SQLite en memoria + X-Api-Key configurada.
- `admin_headers_bearer`: Bearer JWT de un admin (el router ahora lo exige).
"""
from src.models.client import Client


def test_post_creates(client, admin_headers_bearer):
    resp = client.post(
        "/api/v1/clients/",
        json={"nombre": "Juan", "apellido": "Perez", "email": "e@x.com"},
        headers=admin_headers_bearer,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "e@x.com"
    assert data["nombre"] == "Juan"
    assert data["apellido"] == "Perez"
    assert "id" in data
    assert "fecha_registro" in data
    assert data["activo"] is True


def test_post_creates_in_db(client, db_session, admin_headers_bearer):
    """El cliente creado existe en la DB con todos los campos."""
    client.post(
        "/api/v1/clients/",
        json={"nombre": "Maria", "apellido": "Gomez", "email": "maria@x.com"},
        headers=admin_headers_bearer,
    )
    created = db_session.query(Client).filter_by(email="maria@x.com").first()
    assert created is not None
    assert created.nombre == "Maria"
    assert created.apellido == "Gomez"
    assert created.activo is True
    assert created.fecha_registro is not None


def test_post_duplicate_email_es_idempotente(client, admin_headers_bearer):
    """Email duplicado devuelve 200 con el cliente existente (idempotencia)."""
    payload = {"nombre": "Juan", "apellido": "Perez", "email": "dup@x.com"}
    resp1 = client.post("/api/v1/clients/", json=payload, headers=admin_headers_bearer)
    assert resp1.status_code == 201

    resp2 = client.post("/api/v1/clients/", json=payload, headers=admin_headers_bearer)
    assert resp2.status_code == 200
    assert resp2.json()["email"] == "dup@x.com"


def test_post_sin_token_returns_401(client):
    """Sin Bearer JWT el endpoint está protegido (401)."""
    resp = client.post(
        "/api/v1/clients/",
        json={"nombre": "Juan", "apellido": "Perez", "email": "notok@x.com"},
    )
    assert resp.status_code == 401