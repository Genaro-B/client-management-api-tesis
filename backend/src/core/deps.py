"""Dependencias FastAPI de autenticación JWT.

- get_current_user: resuelve el header `Authorization: Bearer <token>`
  a un Client activo (401 genérico en cualquier fallo).
- require_admin: exige role="admin" sobre get_current_user (403 si no).

Reusan decode_token de src.core.security — no duplican lógica JWT.
"""
from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.core.security import decode_token
from src.database.session import get_db
from src.models.client import Client


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Client:
    """Valida el Bearer token y devuelve el Client activo autenticado.

    Mismo mensaje 401 genérico para token ausente, inválido, vencido,
    de usuario inexistente o inactivo: no se revela el motivo exacto.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        client_id = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    client = db.query(Client).filter(Client.id == client_id).first()
    if client is None or not client.activo:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return client


def require_admin(user: Client = Depends(get_current_user)) -> Client:
    """Restringe un endpoint a usuarios con role="admin"."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo acceso admin")
    return user