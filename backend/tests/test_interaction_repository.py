"""Tests unitarios para InteractionRepository."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database.base import Base
from src.models.interaction import Interaction
from src.models.client import Client
from src.repositories.interaction_repo import InteractionRepository
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


def test_save_interaction_happy_path(session):
    repo = InteractionRepository(session)
    interaction = Interaction(source="webhook", payload='{"event": "user.created"}')
    saved = repo.save(interaction)
    assert saved.id is not None
    assert saved.source == "webhook"
    assert saved.payload == '{"event": "user.created"}'
    assert saved.timestamp is not None


def test_save_interaction_with_client_link(session):
    client_repo = ClientRepository(session)
    client = client_repo.create(Client(nombre="Juan", apellido="Perez", email="cliente@x.com"))

    repo = InteractionRepository(session)
    interaction = Interaction(
        source="telegram",
        payload='{"message": "hola"}',
        clientId=client.id,
    )
    saved = repo.save(interaction)
    assert saved.id is not None
    assert saved.clientId == client.id


def test_save_interaction_with_all_fields(session):
    repo = InteractionRepository(session)
    interaction = Interaction(
        source="n8n",
        payload='{"data": "test"}',
        user="bot-123",
        intent="saludo",
        result="ok",
    )
    saved = repo.save(interaction)
    assert saved.user == "bot-123"
    assert saved.intent == "saludo"
    assert saved.result == "ok"
