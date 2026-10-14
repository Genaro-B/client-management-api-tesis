"""Tests API de /api/v1/sales (creación bot, transiciones admin, ticket, listado)."""
import pytest

from src.models.client import Client
from src.models.product import Product
from src.repositories.client_repo import ClientRepository

TEST_API_KEY = "dev-api-key-123"
PREFIX = "/api/v1/sales"


def _cliente(db, tg="12345", nombre="Comprador", apellido="Telegram"):
    return ClientRepository(db).create(Client(
        nombre=nombre, apellido=apellido, email=f"{nombre.lower()}@x.com",
        telegram_user_id=tg,
    ))


def _producto(db, precio=100.0, activo=True):
    p = Product(nombre="Prod", descripcion="d", precio=precio, stock=10, activo=activo)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _payload(items, tg="12345"):
    return {"telegram_user_id": tg, "items": items}


def test_create_sale_api_key_201(client, db_session, auth_headers):
    _cliente(db_session)
    p = _producto(db_session, precio=100.0)
    resp = client.post(
        f"{PREFIX}/",
        json=_payload([{"product_id": p.id, "cantidad": 2}]),
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["total"] == 200.0
    assert data["estado"] == "PENDIENTE"
    assert data["items"][0]["precio_unitario"] == 100.0


def test_create_sale_idempotente_200(client, db_session, auth_headers):
    _cliente(db_session)
    p = _producto(db_session)
    headers = {**auth_headers, "X-Idempotency-Key": "idem-api-1"}
    first = client.post(f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}]), headers=headers)
    assert first.status_code == 201
    second = client.post(f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}]), headers=headers)
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]


def test_create_sale_sin_api_key_401(client, db_session):
    _cliente(db_session)
    p = _producto(db_session)
    resp = client.post(f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}]))
    assert resp.status_code == 401


def test_create_sale_producto_inactivo_400(client, db_session, auth_headers):
    _cliente(db_session)
    p = _producto(db_session, activo=False)
    resp = client.post(
        f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}]),
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_create_sale_telegram_no_resuelve_404(client, db_session, auth_headers):
    p = _producto(db_session)
    resp = client.post(
        f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}], tg="nadie"),
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_confirm_sale_admin(client, db_session, auth_headers, admin_headers_bearer):
    _cliente(db_session)
    p = _producto(db_session)
    created = client.post(
        f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}]),
        headers=auth_headers,
    ).json()

    resp = client.post(f"{PREFIX}/{created['id']}/confirm", headers=admin_headers_bearer)
    assert resp.status_code == 200
    assert resp.json()["estado"] == "CONFIRMADO"
    assert resp.json()["confirmado_por"] is not None


def test_transicion_invalida_409(client, db_session, auth_headers, admin_headers_bearer):
    _cliente(db_session)
    p = _producto(db_session)
    created = client.post(
        f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}]),
        headers=auth_headers,
    ).json()
    # PENDIENTE → COMPLETADO no es válida
    resp = client.post(f"{PREFIX}/{created['id']}/complete", headers=admin_headers_bearer)
    assert resp.status_code == 409


def test_confirm_sale_sin_admin_403(client, db_session, auth_headers):
    _cliente(db_session)
    p = _producto(db_session)
    created = client.post(
        f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}]),
        headers=auth_headers,
    ).json()
    resp = client.post(f"{PREFIX}/{created['id']}/confirm", headers=auth_headers)
    assert resp.status_code == 401


def test_list_sales_filtra_por_estado(client, db_session, auth_headers, admin_headers_bearer):
    _cliente(db_session)
    p = _producto(db_session)
    created = client.post(
        f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}]),
        headers=auth_headers,
    ).json()
    client.post(f"{PREFIX}/{created['id']}/confirm", headers=admin_headers_bearer)

    pendientes = client.get(f"{PREFIX}/?estado=PENDIENTE", headers=admin_headers_bearer).json()
    confirmadas = client.get(f"{PREFIX}/?estado=CONFIRMADO", headers=admin_headers_bearer).json()
    assert pendientes["total"] == 0
    assert confirmadas["total"] == 1


def test_ticket_solo_base_contable(client, db_session, auth_headers, admin_headers_bearer):
    _cliente(db_session, nombre="Maria", apellido="Lopez")
    p = _producto(db_session)
    pendiente = client.post(
        f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}]),
        headers=auth_headers,
    ).json()
    confirmada = client.post(
        f"{PREFIX}/", json=_payload([{"product_id": p.id, "cantidad": 1}]),
        headers={**auth_headers, "X-Idempotency-Key": "otra"},
    ).json()
    client.post(f"{PREFIX}/{confirmada['id']}/confirm", headers=admin_headers_bearer)

    from datetime import datetime, timezone
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    resp = client.get(f"{PREFIX}/ticket?cliente=Maria&fecha={fecha}", headers=admin_headers_bearer)
    assert resp.status_code == 200
    data = resp.json()
    assert data["cliente"] == "Maria"
    ids = {v["id"] for v in data["ventas"]}
    assert confirmada["id"] in ids
    assert pendiente["id"] not in ids


def test_ticket_sin_datos_200_lista_vacia(client, admin_headers_bearer):
    resp = client.get(f"{PREFIX}/ticket?cliente=Nadie&fecha=2020-01-01", headers=admin_headers_bearer)
    assert resp.status_code == 200
    assert resp.json() == {"cliente": None, "ventas": []}
