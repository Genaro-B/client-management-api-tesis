"""Tests de las dependencias JWT de src.core.deps.

get_current_user traduce el header Authorization: Bearer <token> a un Client:
- sin header -> 401
- token inválido / vencido / firma ajena -> 401
- usuario inexistente / inactivo -> 401
- token válido -> devuelve el Client (admin o no)
require_admin: role != admin -> 403
"""
import time

import jwt as pyjwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from src.core.deps import get_current_user, require_admin
from src.core.security import JWT_SECRET_KEY, create_access_token
from src.database.session import get_db
from src.models.client import Client
from src.repositories.client_repo import ClientRepository

# ---------------------------------------------------------------------------
# App de prueba: un endpoint echo que devuelve el Client resuelto
# ---------------------------------------------------------------------------


def _build_app(dependency):
    app = FastAPI()

    @app.get("/me")
    def me(user: Client = Depends(dependency)):
        return {"id": user.id, "email": user.email, "role": user.role}

    return app


@pytest.fixture
def deps_client(db_session):
    """TestClient con BD en memoria y el override de get_db."""
    app = _build_app(get_current_user)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def _header(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# get_current_user
# ---------------------------------------------------------------------------


def test_get_current_user_sin_header_401(deps_client):
    resp = deps_client.get("/me")
    assert resp.status_code == 401


def test_get_current_user_token_invalido_401(deps_client, sample_admin):
    resp = deps_client.get("/me", headers=_header("no-es-un-token"))
    assert resp.status_code == 401


def test_get_current_user_token_firma_ajena_401(deps_client, sample_admin):
    forged = pyjwt.encode(
        {"sub": str(sample_admin.id), "exp": time.time() + 3600},
        "clave-de-otro-lado",
        algorithm="HS256",
    )
    resp = deps_client.get("/me", headers=_header(forged))
    assert resp.status_code == 401


def test_get_current_user_token_vencido_401(deps_client, sample_admin):
    expired = pyjwt.encode(
        {"sub": str(sample_admin.id), "exp": time.time() - 600},
        JWT_SECRET_KEY,
        algorithm="HS256",
    )
    resp = deps_client.get("/me", headers=_header(expired))
    assert resp.status_code == 401


def test_get_current_user_usuario_inexistente_401(deps_client):
    """Token válido pero sub de un client que no existe -> 401."""
    token = create_access_token(client_id=99999)
    resp = deps_client.get("/me", headers=_header(token))
    assert resp.status_code == 401


def test_get_current_user_usuario_inactivo_401(deps_client, db_session):
    """Token válido de un client soft-deleted (activo=False) -> 401."""
    repo = ClientRepository(db_session)
    inactivo = repo.create(Client(
        nombre="Inact",
        apellido="User",
        email="inact-dep@test.com",
        activo=False,
    ))
    token = create_access_token(client_id=inactivo.id)
    resp = deps_client.get("/me", headers=_header(token))
    assert resp.status_code == 401


def test_get_current_user_token_valido_devuelve_client(deps_client, sample_admin):
    token = create_access_token(sample_admin.id)
    resp = deps_client.get("/me", headers=_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == sample_admin.id
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"


def test_get_current_user_token_valido_role_user_tambien_pasa(deps_client, sample_client):
    """Un client activo con role user resuelve igual (get_current_user no filtra role)."""
    token = create_access_token(sample_client.id)
    resp = deps_client.get("/me", headers=_header(token))
    assert resp.status_code == 200
    assert resp.json()["role"] == "user"


# ---------------------------------------------------------------------------
# require_admin
# ---------------------------------------------------------------------------


@pytest.fixture
def admin_client_fixture(db_session):
    app = _build_app(require_admin)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def test_require_admin_acepta_admin(admin_client_fixture, sample_admin):
    token = create_access_token(sample_admin.id)
    resp = admin_client_fixture.get("/me", headers=_header(token))
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


def test_require_admin_rechaza_role_user(admin_client_fixture, sample_client):
    token = create_access_token(sample_client.id)
    resp = admin_client_fixture.get("/me", headers=_header(token))
    assert resp.status_code == 403