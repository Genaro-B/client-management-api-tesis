from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateProduct(BaseModel):
    """Schema for incoming product creation requests."""
    nombre: str = Field(..., min_length=1)
    descripcion: Optional[str] = None
    precio: float = Field(..., ge=0)
    stock: int = Field(default=0, ge=0)
    categoria: Optional[str] = None


class UpdateProduct(BaseModel):
    """Schema for partial updates to a product record."""
    nombre: Optional[str] = Field(None, min_length=1)
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    categoria: Optional[str] = None


class ProductResponse(BaseModel):
    """Response schema returned by API endpoints representing a product."""
    id: int
    nombre: str
    descripcion: Optional[str]
    precio: float
    stock: int
    categoria: Optional[str]
    activo: bool
    fecha_registro: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
