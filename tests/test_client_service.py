import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base
from src.services.client_service import ClientService, EmailAlreadyExists
from src.models.client import Client


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def test_create_duplicate_email(session):
    svc = ClientService(session)
    svc.create(nombre="A", apellido="B", telefono=None, email="dup@x.com")
    with pytest.raises(EmailAlreadyExists):
        svc.create(nombre="C", apellido="D", telefono=None, email="dup@x.com")


def test_update_email_conflict(session):
    svc = ClientService(session)
    a = svc.create(nombre="A", apellido="B", telefono=None, email="a@x.com")
    b = svc.create(nombre="C", apellido="D", telefono=None, email="b@x.com")
    with pytest.raises(EmailAlreadyExists):
        svc.update(b.id, email="a@x.com")
