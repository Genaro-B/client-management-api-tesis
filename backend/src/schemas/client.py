from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class ProductoAsignado(BaseModel):
    """Schema for a product assigned to a client."""
    producto_id: int = Field(..., ge=1)
    nombre: str
    precio: float = Field(..., ge=0)
    cantidad: int = Field(..., ge=1)


class CreateClient(BaseModel):
    """Schema for incoming client creation requests."""
    nombre: str = Field(...)
    apellido: str = Field(...)
    telefono: Optional[str] = None
    email: EmailStr


class RegisterBotRequest(BaseModel):
    """Registro de prospecto desde el bot (sin password ni email del usuario)."""
    telegram_user_id: str = Field(..., min_length=1)
    nombre: str = Field(..., min_length=1)
    # El bot separa "nombre y apellido" en el primer espacio; si hay una sola
    # palabra, envía apellido "" (la columna NOT NULL lo admite).
    apellido: str = ""
    telefono: Optional[str] = None


class RegisterBotResponse(BaseModel):
    """Respuesta del registro de prospecto.

    `email` es `str` (no EmailStr) a propósito: el placeholder
    `tg{id}@telegram.local` usa un dominio reservado que email-validator
    rechazaría, pero es válido para el `NOT NULL + UNIQUE` de la columna.
    """
    id: int
    nombre: str
    apellido: str
    telefono: Optional[str]
    email: str
    telegram_user_id: Optional[str]
    role: str
    activo: bool

    model_config = {"from_attributes": True}


class UpdateClient(BaseModel):
    """Schema for partial updates to a client record."""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None


class ClientResponse(BaseModel):
    """Response schema returned by API endpoints representing a client."""
    id: int
    nombre: str
    apellido: str
    telefono: Optional[str]
    email: EmailStr
    fecha_registro: datetime
    activo: bool
    role: str = "user"
    productos_asignados: List[ProductoAsignado] = []

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Schema for login requests — email + password obligatorios."""
    email: EmailStr
    password: str = Field(min_length=1)


class ChangePasswordRequest(BaseModel):
    """Schema para POST /auth/change-password — exige password actual + nueva."""
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6)


class UserOut(BaseModel):
    """Usuario del panel expuesto en la respuesta de login."""
    id: int
    email: EmailStr
    nombre: str
    apellido: str
    role: str
    password_change_required: bool

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Response returned after successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut
