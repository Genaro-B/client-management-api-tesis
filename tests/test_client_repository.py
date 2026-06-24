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
