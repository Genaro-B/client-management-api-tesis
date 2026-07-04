"""Tests unitarios para ProductRepository."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database.base import Base
from src.models.product import Product
from src.repositories.product_repo import ProductRepository


@pytest.fixture
def session():
    """Crea una sesión SQLite en memoria para cada test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def test_create_and_get_by_id(session):
    repo = ProductRepository(session)
    p = Product(nombre="Producto A", precio=100.0, stock=10)
    repo.create(p)
    found = repo.get_by_id(p.id)
    assert found is not None
    assert found.nombre == "Producto A"
    assert found.precio == 100.0
    assert found.stock == 10


def test_list_pagination(session):
    repo = ProductRepository(session)
    for i in range(15):
        repo.create(Product(nombre=f"Producto {i}", precio=float(i), stock=i))
    items, total = repo.list(limit=10, offset=0)
    assert total == 15
    assert len(items) == 10


def test_list_search_by_name(session):
    repo = ProductRepository(session)
    repo.create(Product(nombre="Limpieza", precio=50, stock=5))
    repo.create(Product(nombre="Alimento", precio=30, stock=10))
    items, total = repo.list(q="Limpieza")
    assert total == 1
    assert items[0].nombre == "Limpieza"


def test_list_search_by_categoria(session):
    repo = ProductRepository(session)
    repo.create(Product(nombre="Jabón", precio=10, stock=100, categoria="Limpieza"))
    repo.create(Product(nombre="Shampoo", precio=20, stock=50, categoria="Limpieza"))
    repo.create(Product(nombre="Arroz", precio=15, stock=200, categoria="Alimentos"))
    items, total = repo.list(q="Limpieza")
    assert total == 2


def test_soft_delete_and_list_inactive(session):
    repo = ProductRepository(session)
    p = Product(nombre="Borrar", precio=10, stock=1)
    repo.create(p)
    repo.soft_delete(p)
    items, total = repo.list_inactive()
    assert total == 1
    assert items[0].id == p.id
    # No aparece en listado activo
    active_items, active_total = repo.list()
    assert active_total == 0


def test_list_inactive_only_returns_inactive(session):
    repo = ProductRepository(session)
    active = Product(nombre="Activo", precio=10, stock=1)
    inactive = Product(nombre="Inactivo", precio=20, stock=2, activo=False)
    repo.create(active)
    repo.create(inactive)
    items, total = repo.list_inactive()
    assert total == 1
    assert items[0].nombre == "Inactivo"


def test_restore_reactivates_product(session):
    repo = ProductRepository(session)
    p = Product(nombre="Restaurar", precio=10, stock=1, activo=False)
    repo.create(p)
    restored = repo.restore(p)
    assert restored.activo is True
    refetched = repo.get_by_id(p.id)
    assert refetched.activo is True


def test_update_product(session):
    repo = ProductRepository(session)
    p = Product(nombre="Original", precio=100, stock=10)
    repo.create(p)
    updated = repo.update(p, precio=150.0, stock=5)
    assert updated.precio == 150.0
    assert updated.stock == 5
    assert updated.nombre == "Original"  # unchanged
