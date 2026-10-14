"""Tests unitarios del SaleRepository.

Cubren: constante BASE_CONTABLE, creación con items, búsqueda por
idempotency_key, y listado con filtros (estado/cliente/rango de fechas) +
paginación.
"""
from datetime import datetime, timezone

import pytest

from src.models.sale import Sale, SaleItem
from src.repositories.sale_repo import SaleRepository, BASE_CONTABLE


def _sale(cliente_id, estado="PENDIENTE", total=0.0, fecha=None, items=None, idem=None):
    s = Sale(
        cliente_id=cliente_id,
        estado=estado,
        total=total,
        idempotency_key=idem,
        fecha=fecha or datetime.now(timezone.utc),
    )
    for it in (items or []):
        s.items.append(SaleItem(**it))
    return s


def test_base_contable_constante():
    assert BASE_CONTABLE == ("CONFIRMADO", "COMPLETADO")


def test_create_con_items_persiste(db_session, sample_client, sample_product):
    repo = SaleRepository(db_session)
    sale = _sale(
        sample_client.id,
        estado="CONFIRMADO",
        total=200.0,
        items=[{"product_id": sample_product.id, "cantidad": 2, "precio_unitario": 100.0}],
    )
    created = repo.create(sale)

    assert created.id is not None
    assert len(created.items) == 1
    assert created.items[0].precio_unitario == 100.0
    assert created.items[0].cantidad == 2


def test_get_by_idempotency_key(db_session, sample_client):
    repo = SaleRepository(db_session)
    repo.create(_sale(sample_client.id, idem="idem-1"))

    assert repo.get_by_idempotency_key("idem-1") is not None
    assert repo.get_by_idempotency_key("no-existe") is None


def test_list_filtra_por_estado_y_cliente(db_session, sample_client):
    repo = SaleRepository(db_session)
    repo.create(_sale(sample_client.id, estado="PENDIENTE"))
    repo.create(_sale(sample_client.id, estado="CONFIRMADO"))
    repo.create(_sale(sample_client.id, estado="CONFIRMADO"))

    items, total = repo.list(estado="CONFIRMADO")
    assert total == 2
    assert all(s.estado == "CONFIRMADO" for s in items)

    items, total = repo.list(cliente_id=sample_client.id)
    assert total == 3


def test_list_filtra_por_rango_de_fechas(db_session, sample_client):
    repo = SaleRepository(db_session)
    repo.create(_sale(sample_client.id, fecha=datetime(2026, 10, 1, 10, tzinfo=timezone.utc)))
    repo.create(_sale(sample_client.id, fecha=datetime(2026, 10, 5, 10, tzinfo=timezone.utc)))
    repo.create(_sale(sample_client.id, fecha=datetime(2026, 10, 10, 10, tzinfo=timezone.utc)))

    items, total = repo.list(
        fecha_desde=datetime(2026, 10, 2, tzinfo=timezone.utc),
        fecha_hasta=datetime(2026, 10, 6, tzinfo=timezone.utc),
    )
    assert total == 1


def test_list_paginacion(db_session, sample_client):
    repo = SaleRepository(db_session)
    for i in range(5):
        repo.create(_sale(sample_client.id))

    items, total = repo.list(limit=2, offset=0)
    assert total == 5
    assert len(items) == 2

    items2, _ = repo.list(limit=2, offset=2)
    assert len(items2) == 2
    assert {s.id for s in items} & {s.id for s in items2} == set()


def test_list_contables_excluye_pendiente_y_cancelado(db_session, sample_client):
    repo = SaleRepository(db_session)
    repo.create(_sale(sample_client.id, estado="PENDIENTE"))
    repo.create(_sale(sample_client.id, estado="CONFIRMADO"))
    repo.create(_sale(sample_client.id, estado="COMPLETADO"))
    repo.create(_sale(sample_client.id, estado="CANCELADO"))

    contables = repo.list_contables()
    assert {s.estado for s in contables} == {"CONFIRMADO", "COMPLETADO"}
    assert len(contables) == 2
