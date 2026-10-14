"""Tests unitarios del SaleService (máquina de estados + antifraude)."""
from datetime import datetime, timezone
from itertools import count

import pytest

from src.models.client import Client
from src.models.product import Product
from src.models.sale import Sale, SaleItem
from src.repositories.client_repo import ClientRepository
from src.repositories.sale_repo import SaleRepository
from src.services.sale_service import (
    SaleService,
    ValidationError,
    ClientNotFoundError,
    SaleNotFoundError,
    TransitionError,
)


_ids = count(1)


def _cliente(db, tg=None, nombre="Juan", apellido="Perez"):
    n = next(_ids)
    return ClientRepository(db).create(Client(
        nombre=nombre, apellido=apellido,
        email=f"cli-{n}@x.com",
        telegram_user_id=tg,
    ))


def _producto(db, precio=100.0, activo=True):
    p = Product(nombre="Prod", descripcion="d", precio=precio, stock=10, activo=activo)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# ---------------------------------------------------------------------------
# create_from_bot
# ---------------------------------------------------------------------------


def test_create_calcula_total_server_side(db_session):
    cliente = _cliente(db_session, tg="12345")
    p1 = _producto(db_session, precio=100.0)
    p2 = _producto(db_session, precio=50.0)

    service = SaleService(db_session)
    sale, created = service.create_from_bot(
        items=[{"product_id": p1.id, "cantidad": 2}, {"product_id": p2.id, "cantidad": 1}],
        telegram_user_id="12345",
    )

    assert created is True
    assert sale.total == 250.0
    assert sale.estado == "PENDIENTE"
    assert sale.cliente_id == cliente.id
    assert sale.confirmado_por is None
    assert {i.precio_unitario for i in sale.items} == {100.0, 50.0}


def test_create_snapshot_precio_no_cambia_con_producto(db_session):
    _cliente(db_session, tg="12345")
    p = _producto(db_session, precio=100.0)
    service = SaleService(db_session)
    sale, _ = service.create_from_bot(
        items=[{"product_id": p.id, "cantidad": 1}], telegram_user_id="12345"
    )

    p.precio = 150.0
    db_session.commit()

    assert sale.items[0].precio_unitario == 100.0
    assert sale.total == 100.0


def test_create_es_idempotente(db_session):
    _cliente(db_session, tg="12345")
    p = _producto(db_session)
    service = SaleService(db_session)

    first, created1 = service.create_from_bot(
        items=[{"product_id": p.id, "cantidad": 1}],
        telegram_user_id="12345", idempotency_key="idem-1",
    )
    second, created2 = service.create_from_bot(
        items=[{"product_id": p.id, "cantidad": 1}],
        telegram_user_id="12345", idempotency_key="idem-1",
    )

    assert created1 is True
    assert created2 is False
    assert first.id == second.id
    assert db_session.query(Sale).count() == 1


def test_create_telegram_inexistente_lanza_error(db_session):
    p = _producto(db_session)
    service = SaleService(db_session)
    with pytest.raises(ClientNotFoundError):
        service.create_from_bot(
            items=[{"product_id": p.id, "cantidad": 1}],
            telegram_user_id="no-existe",
        )


def test_create_producto_inexistente_lanza_validation_error(db_session):
    _cliente(db_session, tg="12345")
    service = SaleService(db_session)
    with pytest.raises(ValidationError):
        service.create_from_bot(
            items=[{"product_id": 99999, "cantidad": 1}],
            telegram_user_id="12345",
        )


def test_create_producto_inactivo_lanza_validation_error(db_session):
    _cliente(db_session, tg="12345")
    p = _producto(db_session, activo=False)
    service = SaleService(db_session)
    with pytest.raises(ValidationError):
        service.create_from_bot(
            items=[{"product_id": p.id, "cantidad": 1}],
            telegram_user_id="12345",
        )


def test_create_sin_items_lanza_validation_error(db_session):
    _cliente(db_session, tg="12345")
    service = SaleService(db_session)
    with pytest.raises(ValidationError):
        service.create_from_bot(items=[], telegram_user_id="12345")


# ---------------------------------------------------------------------------
# Transiciones de estado
# ---------------------------------------------------------------------------


def _venta(db_session, estado="PENDIENTE"):
    cliente = _cliente(db_session)
    repo = SaleRepository(db_session)
    return repo.create(Sale(cliente_id=cliente.id, estado=estado, total=100.0))


def test_confirmar_setea_confirmado_por(db_session):
    sale = _venta(db_session)
    admin_id = _cliente(db_session, tg="admin-tg", nombre="Admin").id

    service = SaleService(db_session)
    result = service.transition(sale.id, "CONFIRMADO", confirmado_por=admin_id)

    assert result.estado == "CONFIRMADO"
    assert result.confirmado_por == admin_id


def test_completar_desde_confirmado(db_session):
    sale = _venta(db_session, estado="CONFIRMADO")
    service = SaleService(db_session)
    result = service.transition(sale.id, "COMPLETADO")
    assert result.estado == "COMPLETADO"


def test_cancelar_desde_pendiente_y_confirmado(db_session):
    s1 = _venta(db_session, estado="PENDIENTE")
    s2 = _venta(db_session, estado="CONFIRMADO")
    service = SaleService(db_session)
    assert service.transition(s1.id, "CANCELADO").estado == "CANCELADO"
    assert service.transition(s2.id, "CANCELADO").estado == "CANCELADO"


@pytest.mark.parametrize("estado,objetivo", [
    ("COMPLETADO", "CONFIRMADO"),
    ("COMPLETADO", "CANCELADO"),
    ("CANCELADO", "CONFIRMADO"),
    ("PENDIENTE", "COMPLETADO"),
])
def test_transicion_invalida_lanza_error(db_session, estado, objetivo):
    sale = _venta(db_session, estado=estado)
    service = SaleService(db_session)
    with pytest.raises(TransitionError):
        service.transition(sale.id, objetivo)


def test_transition_venta_inexistente(db_session):
    service = SaleService(db_session)
    with pytest.raises(SaleNotFoundError):
        service.transition(99999, "CONFIRMADO")


# ---------------------------------------------------------------------------
# Consultas contables (ticket)
# ---------------------------------------------------------------------------


def test_ticket_excluye_pendiente_y_cancelado(db_session):
    cliente = _cliente(db_session, tg="999", nombre="Maria", apellido="Lopez")
    repo = SaleRepository(db_session)
    fecha = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)

    for estado in ("CONFIRMADO", "COMPLETADO", "PENDIENTE", "CANCELADO"):
        repo.create(Sale(cliente_id=cliente.id, estado=estado, total=10.0, fecha=fecha))

    service = SaleService(db_session)
    cliente_name, ventas = service.ticket("maria", "2026-10-01")

    assert cliente_name is not None
    assert {v.estado for v in ventas} == {"CONFIRMADO", "COMPLETADO"}
    assert len(ventas) == 2


def test_ticket_cliente_inexistente_devuelve_vacio(db_session):
    service = SaleService(db_session)
    cliente_name, ventas = service.ticket("nadie", "2026-10-01")
    assert cliente_name is None
    assert ventas == []


def test_ventas_hoy_solo_base_contable(db_session):
    cliente = _cliente(db_session)
    repo = SaleRepository(db_session)
    ahora = datetime.now(timezone.utc)
    repo.create(Sale(cliente_id=cliente.id, estado="CONFIRMADO", total=1.0, fecha=ahora))
    repo.create(Sale(cliente_id=cliente.id, estado="PENDIENTE", total=1.0, fecha=ahora))
    repo.create(Sale(cliente_id=cliente.id, estado="CANCELADO", total=1.0, fecha=ahora))

    service = SaleService(db_session)
    assert service.ventas_hoy() == 1
