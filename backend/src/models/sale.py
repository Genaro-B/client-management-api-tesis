from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from src.database.base import Base


class Sale(Base):
    """Venta con máquina de estados (antifraude por estado de orden).

    Nace en PENDIENTE desde el bot; solo un humano (JWT admin) la confirma.
    Toda métrica/ticket cuenta únicamente CONFIRMADO y COMPLETADO
    (ver SaleRepository.BASE_CONTABLE).
    """

    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # total calculado SIEMPRE en el servidor (Σ cantidad × precio_unitario).
    total = Column(Float, nullable=False, default=0.0)
    estado = Column(String(20), nullable=False, server_default="PENDIENTE")
    # Idempotencia del flujo n8n (reintentos): una clave única = una venta.
    idempotency_key = Column(String(255), nullable=True, unique=True, index=True)
    confirmado_por = Column(Integer, ForeignKey("clients.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    items = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_sales_estado", "estado"),
        Index("ix_sales_fecha", "fecha"),
    )


class SaleItem(Base):
    """Ítem de una venta con snapshot del precio al momento de la compra."""

    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(
        Integer,
        ForeignKey("sales.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)
    # Snapshot de Product.precio: cambios posteriores no alteran la venta.
    precio_unitario = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
