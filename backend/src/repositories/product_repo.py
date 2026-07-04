from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models.product import Product
from typing import List, Optional, Tuple


class ProductRepository:
    """Repository responsible for CRUD operations against the products table."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        """Persist a new product instance and return the attached object."""
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Return a product by primary key or None if not found."""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def list(
        self, limit: int = 50, offset: int = 0, q: Optional[str] = None
    ) -> Tuple[List[Product], int]:
        """List active products with optional text query over nombre or categoria."""
        query = self.db.query(Product).filter(Product.activo == True)
        if q:
            query = query.filter(
                or_(
                    Product.nombre.ilike(f"%{q}%"),
                    Product.categoria.ilike(f"%{q}%"),
                )
            )
        total = query.count()
        items = query.order_by(Product.id).offset(offset).limit(limit).all()
        return items, total

    def update(self, product: Product, **fields) -> Product:
        """Apply field updates to a product instance and persist changes."""
        for k, v in fields.items():
            setattr(product, k, v)
        self.db.commit()
        self.db.refresh(product)
        return product

    def list_all(self) -> List[Product]:
        """Return ALL products (active and inactive), no pagination."""
        return self.db.query(Product).order_by(Product.id).all()

    def list_inactive(
        self, limit: int = 50, offset: int = 0, q: Optional[str] = None
    ) -> Tuple[List[Product], int]:
        """List inactive products with optional text query."""
        query = self.db.query(Product).filter(Product.activo == False)
        if q:
            query = query.filter(
                or_(
                    Product.nombre.ilike(f"%{q}%"),
                    Product.categoria.ilike(f"%{q}%"),
                )
            )
        total = query.count()
        items = query.order_by(Product.id).offset(offset).limit(limit).all()
        return items, total

    def restore(self, product: Product) -> Product:
        """Re-activate a soft-deleted product."""
        product.activo = True
        self.db.commit()
        self.db.refresh(product)
        return product

    def soft_delete(self, product: Product) -> None:
        """Perform a logical delete by setting activo=False."""
        product.activo = False
        self.db.commit()
