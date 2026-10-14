from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from src.models.sale import Sale

# Base contable: única fuente de verdad de qué estados de venta cuentan en
# métricas, reportes y tickets (antifraude). PENDIENTE y CANCELADO NO cuentan.
BASE_CONTABLE = ("CONFIRMADO", "COMPLETADO")


class SaleRepository:
    """Repository responsible for CRUD operations against the sales table.

    El filtro de base contable vive acá (BASE_CONTABLE) para que ningún
    consumidor de métricas tenga que recordarlo y lo pueda olvidar.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, sale: Sale) -> Sale:
        """Persist a new sale (with its items) and return the attached object."""
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        """Return a sale by primary key or None if not found."""
        return self.db.query(Sale).filter(Sale.id == sale_id).first()

    def get_by_idempotency_key(self, key: str) -> Optional[Sale]:
        """Return the sale matching the given idempotency key, or None."""
        return self.db.query(Sale).filter(Sale.idempotency_key == key).first()

    def update(self, sale: Sale, **fields) -> Sale:
        """Apply field updates to a sale instance and persist changes."""
        for k, v in fields.items():
            setattr(sale, k, v)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
        estado: Optional[str] = None,
        cliente_id: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> Tuple[List[Sale], int]:
        """List sales (newest first) with optional filters and pagination."""
        q = self.db.query(Sale)
        if estado:
            q = q.filter(Sale.estado == estado)
        if cliente_id is not None:
            q = q.filter(Sale.cliente_id == cliente_id)
        if fecha_desde is not None:
            q = q.filter(Sale.fecha >= fecha_desde)
        if fecha_hasta is not None:
            q = q.filter(Sale.fecha <= fecha_hasta)
        total = q.count()
        items = (
            q.order_by(Sale.fecha.desc(), Sale.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def list_contables(
        self,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
    ) -> List[Sale]:
        """Return only sales of the contable base, optionally within a range."""
        q = self.db.query(Sale).filter(Sale.estado.in_(BASE_CONTABLE))
        if desde is not None:
            q = q.filter(Sale.fecha >= desde)
        if hasta is not None:
            q = q.filter(Sale.fecha <= hasta)
        return q.order_by(Sale.fecha.asc(), Sale.id.asc()).all()
