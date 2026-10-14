"""Servicio de ventas: creación desde el bot, máquina de estados y consultas.

Reglas duras (antifraude):
- El total SIEMPRE lo calcula el servidor (Σ cantidad × precio_unitario).
- `precio_unitario` es snapshot de `Product.precio` al crear la venta.
- Toda métrica/ticket cuenta solo la base contable (CONFIRMADO/COMPLETADO).
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from src.models.client import Client
from src.models.sale import Sale, SaleItem
from src.repositories.client_repo import ClientRepository
from src.repositories.product_repo import ProductRepository
from src.repositories.sale_repo import SaleRepository, BASE_CONTABLE


class ValidationError(Exception):
    """Entrada inválida (items vacíos, producto inexistente/inactivo)."""


class ClientNotFoundError(Exception):
    """No hay cliente resoluble para atribuir la venta (HTTP 404)."""


class SaleNotFoundError(Exception):
    """La venta no existe (HTTP 404)."""


class TransitionError(Exception):
    """Transición de estado inválida (HTTP 409)."""


class IdempotencyConflict(Exception):
    """Reservado para conflictos de idempotencia (no usado: se devuelve la previa)."""


# Grafo de transiciones válidas. COMPLETADO y CANCELADO son terminales.
VALID_TRANSITIONS = {
    "PENDIENTE": {"CONFIRMADO", "CANCELADO"},
    "CONFIRMADO": {"COMPLETADO", "CANCELADO"},
    "COMPLETADO": set(),
    "CANCELADO": set(),
}


class SaleService:
    """Servicio de ventas (repository + reglas de negocio)."""

    def __init__(self, db: Session):
        self.db = db
        self.sale_repo = SaleRepository(db)
        self.client_repo = ClientRepository(db)
        self.product_repo = ProductRepository(db)

    # ------------------------------------------------------------------
    # Escritura
    # ------------------------------------------------------------------

    def create_from_bot(
        self,
        *,
        items: List[dict],
        telegram_user_id: Optional[str] = None,
        cliente_id: Optional[int] = None,
        idempotency_key: Optional[str] = None,
    ) -> Tuple[Sale, bool]:
        """Crea una venta PENDIENTE desde el bot. Devuelve `(sale, created)`.

        - Idempotente por `idempotency_key`: si existe, devuelve la previa.
        - El payload solo aporta `product_id` + `cantidad`; el total y los
          precios se resuelven server-side desde el catálogo.
        - 404 (ClientNotFoundError) si no resuelve cliente.
        - 400 (ValidationError) si un producto es inexistente/inactivo.
        """
        if idempotency_key:
            existing = self.sale_repo.get_by_idempotency_key(idempotency_key)
            if existing:
                return existing, False

        client = None
        if telegram_user_id:
            client = self.client_repo.get_by_telegram_user_id(telegram_user_id)
        if client is None and cliente_id is not None:
            client = self.client_repo.get_by_id(cliente_id)
        if client is None:
            raise ClientNotFoundError("No se encontró un cliente para la venta")

        if not items:
            raise ValidationError("La venta debe tener al menos un ítem")

        sale = Sale(
            cliente_id=client.id,
            estado="PENDIENTE",
            idempotency_key=idempotency_key,
            total=0.0,
        )
        total = 0.0
        for item in items:
            product_id = item["product_id"]
            cantidad = int(item["cantidad"])
            if cantidad <= 0:
                raise ValidationError("La cantidad debe ser mayor a 0")
            product = self.product_repo.get_by_id(product_id)
            if product is None or not product.activo:
                raise ValidationError(
                    f"Producto {product_id} inexistente o inactivo"
                )
            precio = float(product.precio)
            sale.items.append(
                SaleItem(product_id=product.id, cantidad=cantidad, precio_unitario=precio)
            )
            total += cantidad * precio

        sale.total = total
        return self.sale_repo.create(sale), True

    def transition(
        self,
        sale_id: int,
        target: str,
        confirmado_por: Optional[int] = None,
    ) -> Sale:
        """Aplica una transición de estado válida o lanza TransitionError."""
        sale = self.sale_repo.get_by_id(sale_id)
        if sale is None:
            raise SaleNotFoundError("Venta no encontrada")
        if target not in VALID_TRANSITIONS.get(sale.estado, set()):
            raise TransitionError(
                f"Transición inválida: {sale.estado} → {target}"
            )
        sale.estado = target
        if confirmado_por is not None and target in ("CONFIRMADO", "COMPLETADO"):
            sale.confirmado_por = confirmado_por
        return self.sale_repo.update(sale)

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def get(self, sale_id: int) -> Optional[Sale]:
        return self.sale_repo.get_by_id(sale_id)

    def list(self, **kwargs) -> Tuple[List[Sale], int]:
        return self.sale_repo.list(**kwargs)

    def ticket(self, cliente_texto: str, fecha: str) -> Tuple[Optional[Client], List[Sale]]:
        """Resuelve el cliente por ILIKE y devuelve sus ventas contables del día."""
        if not cliente_texto:
            return None, []
        clientes = (
            self.db.query(Client)
            .filter(
                or_(
                    Client.nombre.ilike(f"%{cliente_texto}%"),
                    Client.apellido.ilike(f"%{cliente_texto}%"),
                )
            )
            .order_by(Client.id)
            .all()
        )
        if not clientes:
            return None, []
        ids = [c.id for c in clientes]
        ventas = (
            self.db.query(Sale)
            .filter(
                Sale.estado.in_(BASE_CONTABLE),
                Sale.cliente_id.in_(ids),
                func.date(Sale.fecha) == fecha,
            )
            .order_by(Sale.fecha.asc(), Sale.id.asc())
            .all()
        )
        return clientes[0], ventas

    def ventas_hoy(self) -> int:
        """Conteo de ventas de la base contable creadas hoy."""
        hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return (
            self.db.query(Sale)
            .filter(Sale.estado.in_(BASE_CONTABLE), func.date(Sale.fecha) == hoy)
            .count()
        )

    def ventas_del_dia(self, fecha: str) -> List[Sale]:
        """Ventas contables de una fecha YYYY-MM-DD (para el asistente)."""
        return (
            self.db.query(Sale)
            .filter(Sale.estado.in_(BASE_CONTABLE), func.date(Sale.fecha) == fecha)
            .order_by(Sale.fecha.asc(), Sale.id.asc())
            .all()
        )

    def list_contables(
        self, desde: Optional[datetime] = None, hasta: Optional[datetime] = None
    ) -> List[Sale]:
        return self.sale_repo.list_contables(desde=desde, hasta=hasta)
