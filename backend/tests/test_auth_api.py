"""Tests de integración para POST /api/v1/auth/login.

El login es email-only (sin password). Verifica existencia y estado activo.
"""
import pytest

PREFIX = "/api/v1/auth"


def test_login_success(client, sample_client):
    resp = client.post(f"{PREFIX}/login", json={"email": "ana@test.com"})
    assert resp.status_code == 200


def test_login_returns_user_data(client, sample_client):
    resp = client.post(f"{PREFIX}/login", json={"email": "ana@test.com"})
    data = resp.json()
    assert data["email"] == "ana@test.com"
    assert data["nombre"] == "Ana"
    assert data["apellido"] == "Garcia"
    assert data["role"] == "user"
    assert "id" in data


def test_login_unregistered_email_returns_401(client):
    resp = client.post(f"{PREFIX}/login", json={"email": "noexiste@test.com"})
    assert resp.status_code == 401
    assert "registrado" in resp.json()["detail"].lower()


def test_login_inactive_account_returns_401(client, sample_inactive_client):
    resp = client.post(f"{PREFIX}/login", json={"email": "inactivo@test.com"})
    assert resp.status_code == 401
    assert "desactivada" in resp.json()["detail"].lower()


def test_login_invalid_email_format_returns_422(client):
    resp = client.post(f"{PREFIX}/login", json={"email": "esto-no-es-un-email"})
    assert resp.status_code == 422
