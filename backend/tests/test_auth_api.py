"""Tests de integración para POST /api/v1/auth/login y /change-password.

Cubre los escenarios de la spec auth-jwt:
- Login exige {email, password}: exitoso devuelve access_token + user
- Password incorrecta / email no registrado / cuenta inactiva / role user -> 401 genérico
- Payload inválido -> 422
- Change-password: exige JWT, valida current_password, resetea flag, login con nueva
"""
import pytest

from src.core.security import hash_password, verify_password
from src.models.client import Client
from src.repositories.client_repo import ClientRepository

PREFIX = "/api/v1/auth"


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------


def test_login_success_returns_token_and_user(client, sample_admin):
    """Login con password correcta devuelve access_token, token_type y user."""
    resp = client.post(f"{PREFIX}/login", json={
        "email": "admin@test.com",
        "password": "cambiar123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    user = data["user"]
    assert user["id"] == sample_admin.id
    assert user["email"] == "admin@test.com"
    assert user["nombre"] == "Admin"
    assert user["apellido"] == "Test"
    assert user["role"] == "admin"
    assert user["password_change_required"] is False


def test_login_with_password_change_required_flag_true(client, db_session):
    """Si el usuario tiene el flag activo, viaja en UserOut (frontend redirige)."""
    repo = ClientRepository(db_session)
    repo.create(Client(
        nombre="Pendiente",
        apellido="Cambio",
        email="pendiente@test.com",
        role="admin",
        password_hash=hash_password("cambiar123"),
        password_change_required=True,
    ))

    resp = client.post(f"{PREFIX}/login", json={
        "email": "pendiente@test.com",
        "password": "cambiar123",
    })
    assert resp.status_code == 200
    assert resp.json()["user"]["password_change_required"] is True


def test_login_wrong_password_returns_401(client, sample_admin):
    resp = client.post(f"{PREFIX}/login", json={
        "email": "admin@test.com",
        "password": "clave-incorrecta",
    })
    assert resp.status_code == 401
    assert "credenciales" in resp.json()["detail"].lower()


def test_login_unregistered_email_returns_401(client):
    resp = client.post(f"{PREFIX}/login", json={
        "email": "noexiste@test.com",
        "password": "cambiar123",
    })
    assert resp.status_code == 401
    assert "credenciales" in resp.json()["detail"].lower()


def test_login_inactive_account_returns_401(client, sample_inactive_client, db_session):
    """Cuenta inactiva -> 401, aunque las credenciales sean válidas."""
    sample_inactive_client.password_hash = hash_password("cambiar123")
    sample_inactive_client.password_change_required = False
    db_session.commit()

    resp = client.post(f"{PREFIX}/login", json={
        "email": "inactivo@test.com",
        "password": "cambiar123",
    })
    assert resp.status_code == 401
    assert "credenciales" in resp.json()["detail"].lower()


def test_login_role_user_returns_401(client, sample_client, db_session):
    """Un cliente con role 'user' (prospecto) no entra al panel: 401 genérico."""
    sample_client.password_hash = hash_password("cambiar123")
    db_session.commit()

    resp = client.post(f"{PREFIX}/login", json={
        "email": "ana@test.com",
        "password": "cambiar123",
    })
    assert resp.status_code == 401
    assert "credenciales" in resp.json()["detail"].lower()


def test_login_admin_without_hash_returns_401(client, db_session):
    """Un admin sin password_hash seteado (ej. recién creado) no puede loguear."""
    repo = ClientRepository(db_session)
    repo.create(Client(
        nombre="SinHash",
        apellido="Admin",
        email="sinhash@test.com",
        role="admin",
    ))

    resp = client.post(f"{PREFIX}/login", json={
        "email": "sinhash@test.com",
        "password": "cualquiera",
    })
    assert resp.status_code == 401


def test_login_missing_password_returns_422(client):
    """Payload sin password -> 422 (validación de schema)."""
    resp = client.post(f"{PREFIX}/login", json={"email": "admin@test.com"})
    assert resp.status_code == 422


def test_login_invalid_email_format_returns_422(client):
    resp = client.post(f"{PREFIX}/login", json={
        "email": "esto-no-es-un-email",
        "password": "cambiar123",
    })
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /change-password
# ---------------------------------------------------------------------------


def test_change_password_requires_token(client):
    """Sin Bearer token -> 401."""
    resp = client.post(f"{PREFIX}/change-password", json={
        "current_password": "cambiar123",
        "new_password": "nuevaSegura1",
    })
    assert resp.status_code == 401


def test_change_password_valid_resets_flag_and_new_login_works(client, db_session, sample_admin, admin_headers_bearer):
    """Flujo obligatorio: con current correcta -> 200, flag False, login con nueva."""
    resp = client.post(
        f"{PREFIX}/change-password",
        json={"current_password": "cambiar123", "new_password": "nuevaSegura1"},
        headers=admin_headers_bearer,
    )
    assert resp.status_code == 200

    db_session.refresh(sample_admin)
    assert sample_admin.password_change_required is False

    # Login con la NUEVA password funciona
    resp_login = client.post(f"{PREFIX}/login", json={
        "email": "admin@test.com",
        "password": "nuevaSegura1",
    })
    assert resp_login.status_code == 200

    # La password vieja ya no funciona
    resp_old = client.post(f"{PREFIX}/login", json={
        "email": "admin@test.com",
        "password": "cambiar123",
    })
    assert resp_old.status_code == 401


def test_change_password_wrong_current_returns_401(client, sample_admin, admin_headers_bearer):
    """Current password incorrecta -> 401 y el hash NO cambia."""
    resp = client.post(
        f"{PREFIX}/change-password",
        json={"current_password": "mal-password", "new_password": "nuevaSegura1"},
        headers=admin_headers_bearer,
    )
    assert resp.status_code == 401

    # El hash sigue siendo el de cambiar123
    assert verify_password("cambiar123", sample_admin.password_hash)


def test_change_password_new_password_too_short_returns_422(client, sample_admin, admin_headers_bearer):
    """new_password < 6 caracteres -> 422."""
    resp = client.post(
        f"{PREFIX}/change-password",
        json={"current_password": "cambiar123", "new_password": "abc"},
        headers=admin_headers_bearer,
    )
    assert resp.status_code == 422