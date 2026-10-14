"""Tests unitarios del RegistrationService (registro de prospecto desde el bot)."""
from src.models.client import Client
from src.repositories.client_repo import ClientRepository
from src.services.registration_service import RegistrationService


def test_registro_nuevo_crea_client_sin_password(db_session):
    service = RegistrationService(db_session)
    client, created = service.register_bot(
        telegram_user_id="12345",
        nombre="Juan Perez",
        apellido="",
        telefono="+541122223333",
    )

    assert created is True
    assert client.id is not None
    assert client.password_hash is None
    assert client.role == "user"
    assert client.activo is True
    assert client.telegram_user_id == "12345"
    assert client.email == "tg12345@telegram.local"
    assert client.telefono == "+541122223333"


def test_segundo_registro_no_duplica(db_session):
    service = RegistrationService(db_session)
    first, created1 = service.register_bot(
        telegram_user_id="12345", nombre="Juan", apellido="Perez", telefono=None
    )
    second, created2 = service.register_bot(
        telegram_user_id="12345", nombre="Juan", apellido="Perez", telefono=None
    )

    assert created1 is True
    assert created2 is False
    assert first.id == second.id
    assert db_session.query(Client).count() == 1


def test_registro_vincula_por_telefono_a_cliente_preexistente(db_session):
    repo = ClientRepository(db_session)
    previo = repo.create(Client(
        nombre="Cliente", apellido="Viejo", email="viejo@x.com",
        telefono="+541155551111",
    ))
    assert previo.telegram_user_id is None

    service = RegistrationService(db_session)
    client, created = service.register_bot(
        telegram_user_id="999", nombre="Cliente", apellido="Viejo",
        telefono="+541155551111",
    )

    assert created is False
    assert client.id == previo.id
    assert client.telegram_user_id == "999"
    assert db_session.query(Client).count() == 1


def test_nombre_una_palabra_deja_apellido_vacio(db_session):
    service = RegistrationService(db_session)
    client, _ = service.register_bot(
        telegram_user_id="777", nombre="Madonna", apellido="", telefono=None
    )
    assert client.apellido == ""
