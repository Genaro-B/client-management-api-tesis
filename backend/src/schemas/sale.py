"""Schemas de la API de ventas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SaleItemRequest(BaseModel):
    """Ítem entrante desde el bot: SOLO producto y cantidad.

    El precio y el total NO se aceptan desde el cliente: los calcula el
    servidor desde el catálogo (antifraude).
    """
    product_id: int
    cantidad: int = Field(..., gt=0)


class CreateSale(BaseModel):
    """Alta de venta desde el bot (API-Key) o desde el panel (cliente_id)."""
    telegram_user_id: Optional[str] = None
    cliente_id: Optional[int] = None
    items: List[SaleItemRequest] = Field(..., min_length=1)


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    producto_nombre: Optional[str] = None
    cantidad: int
    precio_unitario: float


class SaleResponse(BaseModel):
    id: int
    cliente_id: int
    cliente_nombre: Optional[str] = None
    fecha: datetime
    total: float
    estado: str
    idempotency_key: Optional[str] = None
    confirmado_por: Optional[int] = None
    confirmado_por_nombre: Optional[str] = None
    items: List[SaleItemResponse] = []


class SaleListResponse(BaseModel):
    items: List[SaleResponse]
    total: int


class TicketResponse(BaseModel):
    cliente: Optional[str] = None
    ventas: List[SaleResponse] = []
