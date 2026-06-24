from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CreateClient(BaseModel):
    nombre: str = Field(...)
    apellido: str = Field(...)
    telefono: Optional[str] = None
    email: EmailStr


class UpdateClient(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None


class ClientResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    telefono: Optional[str]
    email: EmailStr
    fecha_registro: datetime
    activo: bool

    class Config:
        orm_mode = True
