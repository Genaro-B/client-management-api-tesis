from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CreateClient(BaseModel):
    """Schema for incoming client creation requests."""
    nombre: str = Field(...)
    apellido: str = Field(...)
    telefono: Optional[str] = None
    email: EmailStr


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

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Schema for login requests — email only, no password."""
    email: EmailStr


class AuthResponse(BaseModel):
    """Response returned after successful authentication."""
    id: int
    email: EmailStr
    nombre: str
    apellido: str
    role: str
