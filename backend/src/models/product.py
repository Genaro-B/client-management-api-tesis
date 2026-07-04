from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, func
from src.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=0)
    categoria = Column(String(100), nullable=True)
    activo = Column(Boolean, nullable=False, server_default="1")
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
