"""Tests unitarios para ProductService."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database.base import Base
from src.models.product import Product
from src.services.product_service import ProductService
from src.repositories.product_repo import ProductRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def test_create_product(session):
    service = ProductService(session)
    p = service.create(nombre="Producto Test", descripcion="Desc", precio=100.0, stock=10, categoria="Test")
    assert p.id is not None
    assert p.nombre == "Producto Test"
    assert p.precio == 100.0
    assert p.stock == 10


def test_create_product_minimal(session):
    """Crear producto solo con campos obligatorios."""
    service = ProductService(session)
    p = service.create(nombre="Minimo", descripcion=None, precio=0.0, stock=0, categoria=None)
    assert p.nombre == "Minimo"
    assert p.precio == 0.0
    assert p.stock == 0


def test_update_product_price(session):
    service = ProductService(session)
    p = service.create(nombre="Test", descripcion=None, precio=50.0, stock=5, categoria=None)
    updated = service.update(p.id, precio=75.0)
    assert updated is not None
    assert updated.precio == 75.0


def test_update_nonexistent_product(session):
    service = ProductService(session)
    result = service.update(9999, nombre="No existe")
    assert result is None


def test_soft_delete_product(session):
    service = ProductService(session)
    p = service.create(nombre="Borrar", descripcion=None, precio=10.0, stock=1, categoria=None)
    result = service.soft_delete(p.id)
    assert result is True
    # Verify it's gone from active list
    items, total = service.list()
    assert total == 0


def test_soft_delete_nonexistent(session):
    service = ProductService(session)
    result = service.soft_delete(9999)
    assert result is False


def test_list_with_search(session):
    service = ProductService(session)
    service.create(nombre="Limpieza", descripcion=None, precio=10, stock=5, categoria="Hogar")
    service.create(nombre="Alimento", descripcion=None, precio=20, stock=10, categoria="Mascotas")
    items, total = service.list(q="Limpieza")
    assert total == 1
    assert items[0].nombre == "Limpieza"
