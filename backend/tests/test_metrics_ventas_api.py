"""Tests API de GET /api/v1/metrics/ventas (base contable, serie, top, horario)."""
from datetime import datetime

from src.models.client import Client
from src.models.product import Product
from src.models.sale import Sale, SaleItem
from src.repositories.client_repo import ClientRepository
from src.repositories.sale_repo import SaleRepository

PREFIX = "/api/v1/metrics"


def _cliente(db, tg="12345"):
    return ClientRepository(db).create(Client(
        nombre="Cliente", apellido="Metricas", email="metric@x.com",
        telegram_user_id=tg,
    ))


def _venta(db, cliente, estado, total, fecha):
    return SaleRepository(db).create(Sale(
        cliente_id=cliente.id, estado=estado, total=total, fecha=fecha,
    ))


def test_summary_base_contable(client, db_session, admin_headers_bearer):
    c = _cliente(db_session)
    d = datetime(2026, 6, 10, 10)
    _venta(db_session, c, "CONFIRMADO", 100, d)
    _venta(db_session, c, "CONFIRMADO", 300, d)
    for _ in range(3):
        _venta(db_session, c, "PENDIENTE", 999, d)

    resp = client.get(
        f"{PREFIX}/ventas?desde=2026-06-10&hasta=2026-06-10",
        headers=admin_headers_bearer,
    )
    assert resp.status_code == 200
    summary = resp.json()["summary"]
    assert summary["ventas"] == 2
    assert summary["ingresos"] == 400
    assert summary["ticketPromedio"] == 200


def test_summary_sin_ventas(client, admin_headers_bearer):
    resp = client.get(
        f"{PREFIX}/ventas?desde=2026-01-01&hasta=2026-01-31",
        headers=admin_headers_bearer,
    )
    summary = resp.json()["summary"]
    assert summary["ventas"] == 0
    assert summary["ingresos"] == 0
    assert summary["ticketPromedio"] == 0


def test_vs_periodo_anterior(client, db_session, admin_headers_bearer):
    c = _cliente(db_session)
    # Periodo actual: 06-08..06-10 → 4 ventas
    for _ in range(4):
        _venta(db_session, c, "CONFIRMADO", 100, datetime(2026, 6, 9, 10))
    # Periodo anterior: 06-05..06-07 → 2 ventas
    for _ in range(2):
        _venta(db_session, c, "CONFIRMADO", 100, datetime(2026, 6, 6, 10))

    resp = client.get(
        f"{PREFIX}/ventas?desde=2026-06-08&hasta=2026-06-10",
        headers=admin_headers_bearer,
    )
    vs = resp.json()["summary"]["vsPeriodoAnterior"]
    assert vs["ventas"] == 100.0


def test_serie_diaria_rellena_ceros(client, db_session, admin_headers_bearer):
    c = _cliente(db_session)
    _venta(db_session, c, "CONFIRMADO", 100, datetime(2026, 6, 1, 10))
    _venta(db_session, c, "CONFIRMADO", 50, datetime(2026, 6, 5, 10))

    resp = client.get(
        f"{PREFIX}/ventas?desde=2026-06-01&hasta=2026-06-07",
        headers=admin_headers_bearer,
    )
    serie = resp.json()["serieDiaria"]
    assert len(serie) == 7
    por_fecha = {d["fecha"]: d for d in serie}
    assert por_fecha["2026-06-01"]["ventas"] == 1
    assert por_fecha["2026-06-01"]["ingresos"] == 100
    assert por_fecha["2026-06-02"]["ventas"] == 0
    assert por_fecha["2026-06-05"]["ingresos"] == 50
    assert [d["fecha"] for d in serie] == sorted(d["fecha"] for d in serie)


def test_top_productos_solo_base_contable(client, db_session, admin_headers_bearer):
    c = _cliente(db_session)
    p = Product(nombre="Widget", descripcion="d", precio=10.0, stock=100, activo=True)
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)

    d = datetime(2026, 6, 10, 10)
    pendiente = Sale(cliente_id=c.id, estado="PENDIENTE", total=100, fecha=d)
    pendiente.items.append(SaleItem(product_id=p.id, cantidad=10, precio_unitario=10))
    SaleRepository(db_session).create(pendiente)

    confirmada = Sale(cliente_id=c.id, estado="CONFIRMADO", total=30, fecha=d)
    confirmada.items.append(SaleItem(product_id=p.id, cantidad=3, precio_unitario=10))
    SaleRepository(db_session).create(confirmada)

    resp = client.get(
        f"{PREFIX}/ventas?desde=2026-06-10&hasta=2026-06-10",
        headers=admin_headers_bearer,
    )
    top = resp.json()["topProductos"]
    assert len(top) == 1
    assert top[0]["producto"] == "Widget"
    assert top[0]["cantidad"] == 3


def test_por_horario_24_entradas(client, admin_headers_bearer):
    resp = client.get(
        f"{PREFIX}/ventas?desde=2026-06-10&hasta=2026-06-10",
        headers=admin_headers_bearer,
    )
    por_horario = resp.json()["porHorario"]
    assert len(por_horario) == 24
    assert {h["hora"] for h in por_horario} == set(range(24))
