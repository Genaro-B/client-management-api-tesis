"""Servicio de imágenes de producto.

Compone validación → storage → repositorio siguiendo el patrón de
`ProductService`. El storage se inyecta (dependency inversion): la API usa
`LocalImageStorage` y los tests un fake.
"""
from sqlalchemy.orm import Session

from src.models.product import Product
from src.repositories.product_repo import ProductRepository
from src.storage.image_storage import ImageStorage


class ProductImageService:
    """Coordina la subida, reemplazo y remoción de imágenes de producto.

    Recibe `db` y `storage: ImageStorage` inyectado. Devuelve None cuando el
    producto no existe (el router lo traduce a 404), igual que `ProductService.update`.
    """

    def __init__(self, db: Session, storage: ImageStorage):
        self.repo = ProductRepository(db)
        self.db = db
        self.storage = storage

    def upload(self, product_id: int, image_bytes: bytes, content_type: str):
        """Asociar (o reemplazar) la imagen de un producto existente.

        Valida contra el contrato común del storage, guarda el archivo nuevo y
        solo entonces borra el anterior: si algo falla, el producto conserva
        su imagen vigente.
        """
        product = self.repo.get_by_id(product_id)
        if product is None or not product.activo:
            return None
        self.storage.validate(image_bytes, content_type)
        url = self.storage.save(image_bytes, content_type, product_id)
        if product.image_url:
            self.storage.delete(product.image_url)
        return self.repo.update(product, image_url=url)

    def remove(self, product_id: int):
        """Quitar la imagen de un producto (idempotente) y setear image_url en None."""
        product = self.repo.get_by_id(product_id)
        if product is None or not product.activo:
            return None
        if product.image_url:
            self.storage.delete(product.image_url)
        return self.repo.update(product, image_url=None)