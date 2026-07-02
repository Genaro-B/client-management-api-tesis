"""Tests de integración para el CRUD completo de /api/v1/clients.

Cubre: crear, listar, obtener, actualizar, eliminar (soft-delete),
restaurar, listar inactivos, y exportar Excel.
"""
import pytest
from src.models.client import Client
from src.repositories.client_repo import ClientRepository

PREFIX = "/api/v1/clients"


# ---------------------------------------------------------------------------
# POST / — Crear cliente
# ---------------------------------------------------------------------------

def test_create_client_happy_path(client):
    payload = {
        "nombre": "Carlos",
        "apellido": "Lopez",
        "email": "carlos@example.com",
    }
    resp = client.post(f"{PREFIX}/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["nombre"] == "Carlos"
    assert data["apellido"] == "Lopez"
    assert data["email"] == "carlos@example.com"
    assert data["activo"] is True
    assert "id" in data
    assert "fecha_registro" in data


def test_create_client_with_telefono(client):
    payload = {
        "nombre": "Maria",
        "apellido": "Gomez",
        "email": "maria@example.com",
        "telefono": "+5491122223333",
    }
    resp = client.post(f"{PREFIX}/", json=payload)
    assert resp.status_code == 201
    assert resp.json()["telefono"] == "+5491122223333"


def test_create_client_duplicate_email_returns_400(client):
    payload = {
        "nombre": "Uno",
        "apellido": "A",
        "email": "dup@example.com",
    }
    resp1 = client.post(f"{PREFIX}/", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post(f"{PREFIX}/", json=payload)
    assert resp2.status_code == 400
    assert "email" in resp2.json()["detail"].lower()


def test_create_client_missing_nombre_returns_422(client):
    resp = client.post(f"{PREFIX}/", json={"apellido": "X", "email": "x@x.com"})
    assert resp.status_code == 422


def test_create_client_missing_apellido_returns_422(client):
    resp = client.post(f"{PREFIX}/", json={"nombre": "X", "email": "x@x.com"})
    assert resp.status_code == 422


def test_create_client_invalid_email_returns_422(client):
    resp = client.post(
        f"{PREFIX}/",
        json={"nombre": "X", "apellido": "Y", "email": "not-an-email"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET / — Listar clientes activos
# ---------------------------------------------------------------------------

def test_list_clients_empty(client):
    resp = client.get(f"{PREFIX}/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_clients_returns_active_only(client, db_session):
    """Crea un cliente activo y uno inactivo; solo el activo aparece en list."""
    repo = ClientRepository(db_session)
    repo.create(Client(nombre="Activo", apellido="A", email="activo@x.com"))
    repo.create(Client(nombre="Inact", apellido="I", email="inact@x.com", activo=False))

    resp = client.get(f"{PREFIX}/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["email"] == "activo@x.com"


def test_list_clients_pagination(client, db_session):
    repo = ClientRepository(db_session)
    for i in range(15):
        repo.create(Client(nombre=f"User{i}", apellido="T", email=f"u{i}@x.com"))

    resp_page = client.get(f"{PREFIX}/?limit=5&offset=0")
    assert resp_page.status_code == 200
    data = resp_page.json()
    assert len(data["items"]) == 5
    assert data["total"] == 15


def test_list_clients_search_by_name(client, db_session):
    repo = ClientRepository(db_session)
    repo.create(Client(nombre="Roberto", apellido="X", email="r@x.com"))
    repo.create(Client(nombre="Romina", apellido="Y", email="romi@x.com"))
    repo.create(Client(nombre="Pedro", apellido="Z", email="p@x.com"))

    resp = client.get(f"{PREFIX}/?q=Roberto")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["email"] == "r@x.com"


# ---------------------------------------------------------------------------
# GET /{id} — Obtener cliente por ID
# ---------------------------------------------------------------------------

def test_get_client_by_id(client, sample_client):
    resp = client.get(f"{PREFIX}/{sample_client.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == sample_client.id
    assert data["email"] == sample_client.email


def test_get_client_not_found_returns_404(client):
    resp = client.get(f"{PREFIX}/99999")
    assert resp.status_code == 404


def test_get_inactive_client_returns_404(client, db_session):
    repo = ClientRepository(db_session)
    c = repo.create(Client(nombre="Inact", apellido="I", email="i@x.com", activo=False))
    resp = client.get(f"{PREFIX}/{c.id}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /{id} — Actualizar cliente
# ---------------------------------------------------------------------------

def test_update_client_partial(client, sample_client):
    resp = client.patch(f"{PREFIX}/{sample_client.id}", json={"nombre": "Ana Maria"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["nombre"] == "Ana Maria"
    # Los campos no enviados NO se modifican
    assert data["apellido"] == sample_client.apellido
    assert data["email"] == sample_client.email


def test_update_client_all_fields(client, sample_client):
    resp = client.patch(
        f"{PREFIX}/{sample_client.id}",
        json={
            "nombre": "Nuevo",
            "apellido": "Nombre",
            "email": "nuevo@test.com",
            "telefono": "+541234567890",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["nombre"] == "Nuevo"
    assert data["apellido"] == "Nombre"
    assert data["email"] == "nuevo@test.com"
    assert data["telefono"] == "+541234567890"


def test_update_client_email_conflict_returns_400(client, db_session):
    repo = ClientRepository(db_session)
    repo.create(Client(nombre="Existente", apellido="E", email="existente@x.com"))
    target = repo.create(Client(nombre="Target", apellido="T", email="target@x.com"))

    # Intentar cambiar al email que ya usa otro cliente
    resp = client.patch(
        f"{PREFIX}/{target.id}",
        json={"email": "existente@x.com"},
    )
    assert resp.status_code == 400
    assert "email" in resp.json()["detail"].lower()


def test_update_client_not_found_returns_404(client):
    resp = client.patch(f"{PREFIX}/99999", json={"nombre": "Ghost"})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /{id} — Soft delete
# ---------------------------------------------------------------------------

def test_delete_client_returns_204(client, sample_client):
    resp = client.delete(f"{PREFIX}/{sample_client.id}")
    assert resp.status_code == 204


def test_delete_client_not_found_returns_404(client):
    resp = client.delete(f"{PREFIX}/99999")
    assert resp.status_code == 404


def test_delete_client_then_list_excluded(client, sample_client):
    """Después de soft-delete, el cliente no aparece en GET / activos."""
    client.delete(f"{PREFIX}/{sample_client.id}")
    resp = client.get(f"{PREFIX}/")
    assert resp.json()["total"] == 0


# ---------------------------------------------------------------------------
# GET /inactive — Listar inactivos
# ---------------------------------------------------------------------------

def test_list_inactive_after_delete(client, sample_client):
    client.delete(f"{PREFIX}/{sample_client.id}")
    resp = client.get(f"{PREFIX}/inactive")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == sample_client.id


def test_list_inactive_search(client, db_session):
    repo = ClientRepository(db_session)
    repo.create(Client(nombre="Pedro", apellido="X", email="pedro@x.com", activo=False))
    repo.create(Client(nombre="Pablo", apellido="Y", email="pablo@x.com", activo=False))
    repo.create(Client(nombre="Juan", apellido="Z", email="juan@x.com", activo=False))

    resp = client.get(f"{PREFIX}/inactive?q=Pedro")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["email"] == "pedro@x.com"


# ---------------------------------------------------------------------------
# PATCH /{id}/restore — Restaurar cliente eliminado
# ---------------------------------------------------------------------------

def test_restore_client(client, sample_client):
    client.delete(f"{PREFIX}/{sample_client.id}")

    resp = client.patch(f"{PREFIX}/{sample_client.id}/restore")
    assert resp.status_code == 200
    assert resp.json()["activo"] is True


def test_restore_client_appears_in_active_list(client, sample_client):
    client.delete(f"{PREFIX}/{sample_client.id}")
    client.patch(f"{PREFIX}/{sample_client.id}/restore")

    resp = client.get(f"{PREFIX}/")
    assert resp.json()["total"] == 1


def test_restore_already_active_returns_400(client, sample_client):
    resp = client.patch(f"{PREFIX}/{sample_client.id}/restore")
    assert resp.status_code == 400
    assert "activo" in resp.json()["detail"].lower()


def test_restore_not_found_returns_404(client):
    resp = client.patch(f"{PREFIX}/99999/restore")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /export — Exportar Excel
# ---------------------------------------------------------------------------

def test_export_excel_returns_xlsx(client, sample_client):
    resp = client.get(f"{PREFIX}/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def test_export_excel_has_content_disposition(client, sample_client):
    resp = client.get(f"{PREFIX}/export")
    assert "Content-Disposition" in resp.headers
    assert resp.headers["content-disposition"].startswith("attachment")
    assert "clientes.xlsx" in resp.headers["content-disposition"]
