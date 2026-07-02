"""Tests unitarios para InteractionService (reglas de negocio)."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database.base import Base
from src.models.client import Client
from src.repositories.client_repo import ClientRepository
from src.services.interaction_service import InteractionService, ValidationError, UnknownSourceError, IdempotencyConflict


@pytest.fixture
def session():
    """Crea una sesión SQLite en memoria para cada test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def test_create_valid_interaction(session):
    svc = InteractionService(session)
    interaction = svc.create(source="webhook", payload='{"event": "test"}')
    assert interaction.id is not None
    assert interaction.timestamp is not None


def test_create_missing_source_raises_error(session):
    svc = InteractionService(session)
    with pytest.raises(ValidationError, match="source is required"):
        svc.create(source="", payload='{"event": "test"}')


def test_create_unknown_source_raises_error(session):
    svc = InteractionService(session)
    with pytest.raises(UnknownSourceError):
        svc.create(source="unknown-source", payload='{"event": "test"}')


def test_create_missing_payload_raises_error(session):
    svc = InteractionService(session)
    with pytest.raises(ValidationError, match="payload is required"):
        svc.create(source="webhook", payload="")


def test_create_links_client_by_email(session):
    client_repo = ClientRepository(session)
    client_repo.create(Client(nombre="Juan", apellido="Perez", email="juan@x.com"))

    svc = InteractionService(session)
    interaction = svc.create(
        source="telegram",
        payload='{"msg": "hola"}',
        clientLookup={"email": "juan@x.com"},
    )
    assert interaction.clientId is not None
    assert interaction.clientId == 1


def test_create_links_client_by_telefono(session):
    client_repo = ClientRepository(session)
    client_repo.create(Client(nombre="Maria", apellido="Lopez", email="maria@x.com", telefono="+54123456789"))

    svc = InteractionService(session)
    interaction = svc.create(
        source="telegram",
        payload='{"msg": "hola"}',
        clientLookup={"telefono": "+54123456789"},
    )
    assert interaction.clientId is not None


def test_create_does_not_link_when_client_not_found(session):
    svc = InteractionService(session)
    interaction = svc.create(
        source="webhook",
        payload='{"msg": "test"}',
        clientLookup={"email": "noexiste@x.com"},
    )
    assert interaction.clientId is None


def test_create_with_all_optional_fields(session):
    svc = InteractionService(session)
    interaction = svc.create(
        source="n8n",
        payload='{"event": "order.created"}',
        user="admin",
        intent="order_creation",
        result="processed",
    )
    assert interaction.user == "admin"
    assert interaction.intent == "order_creation"
    assert interaction.result == "processed"


def test_create_with_idempotency_key(session):
    svc = InteractionService(session)
    interaction = svc.create(
        source="webhook",
        payload='{"event": "test"}',
        idempotency_key="tg-12345",
    )
    assert interaction.id is not None
    assert interaction.idempotency_key == "tg-12345"


def test_create_duplicate_idempotency_key(session):
    svc = InteractionService(session)
    svc.create(
        source="webhook",
        payload='{"event": "first"}',
        idempotency_key="tg-12345",
    )
    with pytest.raises(IdempotencyConflict):
        svc.create(
            source="webhook",
            payload='{"event": "second"}',
            idempotency_key="tg-12345",
        )
