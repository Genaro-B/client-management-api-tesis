"""Tests unitarios de ProductImageService con un FAKE de ImageStorage.

La inyección del storage (dependency inversion) permite probar el servicio
sin tocar el filesystem: el fake registra las llamadas a save/delete.
También cubre que el soft-delete del producto conserva la imagen.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.base import Base
from src.models.product import Product
from src.repositories.product_repo import ProductRepository
from src.services.product_image_service import ProductImageService
from src.services.product_service import ProductService


class FakeImageStorage:
    """Fake de ImageStorage que registra llamadas sin tocar el filesystem."""

    def __init__(self):
        self.saved = []
        self.deleted = []

    def save(self, image_bytes, content_type, product_id):
        self.saved.append((image_bytes, content_type, product_id))
        return f"/static/uploads/{product_id}/fake-uuid.jpg"

    def delete(self, url):
        self.deleted.append(url)

    def validate(self, image_bytes, content_type):
        return None


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def test_upload_success_updates_image_url(session):
    """Subir una imagen a un producto existente actualiza image_url."""
    repo = ProductRepository(session)
    p = repo.create(Product(nombre="Con imagen", precio=10, stock=1))
    storage = FakeImageStorage()
    service = ProductImageService(session, storage)

    updated = service.upload(p.id, b"\x89PNG\r\n\x1a\n", "image/png")

    assert updated.image_url == f"/static/uploads/{p.id}/fake-uuid.jpg"
    assert len(storage.saved) == 1
    assert storage.saved[0][2] == p.id


def test_upload_missing_product_returns_none(session):
    """Subir a un producto inexistente devuelve None (el router responde 404)."""
    storage = FakeImageStorage()
    service = ProductImageService(session, storage)

    assert service.upload(9999, b"datos", "image/png") is None
    assert storage.saved == []


def test_upload_replacement_deletes_previous_file(session):
    """Reemplazar la imagen borra el archivo anterior (una imagen por producto)."""
    repo = ProductRepository(session)
    p = repo.create(Product(nombre="Reemplazo", precio=10, stock=1, image_url=f"/static/uploads/{1}/old.jpg"))
    storage = FakeImageStorage()
    service = ProductImageService(session, storage)

    updated = service.upload(p.id, b"datos", "image/jpeg")

    assert updated.image_url == f"/static/uploads/{p.id}/fake-uuid.jpg"
    assert storage.deleted == [f"/static/uploads/{1}/old.jpg"]


def test_upload_without_previous_image_does_not_delete(session):
    """Si el producto no tenía imagen, no se borra nada."""
    repo = ProductRepository(session)
    p = repo.create(Product(nombre="Nuevo", precio=10, stock=1))
    storage = FakeImageStorage()
    service = ProductImageService(session, storage)

    service.upload(p.id, b"datos", "image/jpeg")

    assert storage.deleted == []


def test_remove_sets_image_url_none_and_deletes_file(session):
    """Quitar la imagen borra el archivo y setea image_url en None."""
    repo = ProductRepository(session)
    p = repo.create(Product(nombre="Con imagen", precio=10, stock=1, image_url="/static/uploads/1/old.jpg"))
    storage = FakeImageStorage()
    service = ProductImageService(session, storage)

    updated = service.remove(p.id)

    assert updated.image_url is None
    assert storage.deleted == ["/static/uploads/1/old.jpg"]


def test_remove_without_image_is_idempotent(session):
    """Quitar imagen de un producto sin imagen no falla ni borra nada."""
    repo = ProductRepository(session)
    p = repo.create(Product(nombre="Sin imagen", precio=10, stock=1))
    storage = FakeImageStorage()
    service = ProductImageService(session, storage)

    updated = service.remove(p.id)

    assert updated.image_url is None
    assert storage.deleted == []


def test_remove_missing_product_returns_none(session):
    """Quitar imagen de un producto inexistente devuelve None."""
    service = ProductImageService(session, FakeImageStorage())

    assert service.remove(9999) is None


def test_soft_delete_conserva_la_imagen(session):
    """Soft-delete conserva archivo e image_url; al restaurar sigue funcional."""
    repo = ProductRepository(session)
    p = repo.create(Product(nombre="Soft", precio=10, stock=1, image_url="/static/uploads/1/img.jpg"))

    ProductService(session).soft_delete(p.id)
    assert p.image_url == "/static/uploads/1/img.jpg"

    repo.restore(p)
    assert p.image_url == "/static/uploads/1/img.jpg"