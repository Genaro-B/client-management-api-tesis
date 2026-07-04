from src.repositories.product_repo import ProductRepository
from src.models.product import Product
from sqlalchemy.orm import Session


class ProductService:
    """Service layer implementing business rules for Product operations."""

    def __init__(self, db: Session):
        self.repo = ProductRepository(db)
        self.db = db

    def create(self, *, nombre, descripcion, precio, stock, categoria) -> Product:
        product = Product(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria=categoria,
        )
        return self.repo.create(product)

    def get(self, product_id: int):
        return self.repo.get_by_id(product_id)

    def list(self, limit=50, offset=0, q=None):
        return self.repo.list(limit=limit, offset=offset, q=q)

    def update(self, product_id: int, **fields):
        product = self.repo.get_by_id(product_id)
        if not product:
            return None
        return self.repo.update(product, **fields)

    def soft_delete(self, product_id: int):
        product = self.repo.get_by_id(product_id)
        if not product:
            return False
        self.repo.soft_delete(product)
        return True
