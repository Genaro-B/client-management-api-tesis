"""Tests unitarios para ClientRepository."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database.base import Base
from src.models.client import Client
from src.repositories.client_repo import ClientRepository


@pytest.fixture
def session():
    """Crea una sesión SQLite en memoria para cada test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def test_create_and_get_by_email(session):
    repo = ClientRepository(session)
    c = Client(nombre="Juan", apellido="Perez", email="a@b.com")
    repo.create(c)
    found = repo.get_by_email("a@b.com")
    assert found is not None
    assert found.email == "a@b.com"


def test_list_pagination(session):
    repo = ClientRepository(session)
    for i in range(15):
        repo.create(Client(nombre=f"n{i}", apellido="a", email=f"{i}@x.com"))
    items, total = repo.list(limit=10, offset=0)
    assert total == 15
    assert len(items) == 10


def test_list_inactive_only_returns_inactive(session):
    repo = ClientRepository(session)
    active = Client(nombre="Activo", apellido="A", email="activo@x.com")
    inactive = Client(nombre="Inactivo", apellido="B", email="inactivo@x.com", activo=False)
    repo.create(active)
    repo.create(inactive)
    items, total = repo.list_inactive()
    assert total == 1
    assert items[0].email == "inactivo@x.com"


def test_list_inactive_with_search(session):
    repo = ClientRepository(session)
    repo.create(Client(nombre="Juan", apellido="A", email="juan@x.com", activo=False))
    repo.create(Client(nombre="Pedro", apellido="B", email="pedro@x.com", activo=False))
    items, total = repo.list_inactive(nombre="Juan")
    assert total == 1
    assert items[0].email == "juan@x.com"


def test_restore_reactivates_client(session):
    repo = ClientRepository(session)
    c = Client(nombre="Test", apellido="R", email="test@x.com", activo=False)
    repo.create(c)
    restored = repo.restore(c)
    assert restored.activo is True
    # Verify it's still true after a fresh query
    refetched = repo.get_by_id(c.id)
    assert refetched.activo is True


def test_soft_delete_and_list_inactive(session):
    repo = ClientRepository(session)
    c = Client(nombre="Borrar", apellido="X", email="borrar@x.com")
    repo.create(c)
    repo.soft_delete(c)
    items, total = repo.list_inactive()
    assert total == 1
    assert items[0].id == c.id


def test_get_by_telefono(session):
    repo = ClientRepository(session)
    c = Client(nombre="Carlos", apellido="Garcia", email="carlos@x.com", telefono="+541155551111")
    repo.create(c)
    found = repo.get_by_telefono("+541155551111")
    assert found is not None
    assert found.email == "carlos@x.com"

    not_found = repo.get_by_telefono("+999999999")
    assert not_found is None
