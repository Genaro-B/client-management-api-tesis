from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.schemas.client import LoginRequest, AuthResponse
from src.repositories.client_repo import ClientRepository
from src.database.session import get_db

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Autenticar por email. No usa password — el cliente existe? entra."""
    repo = ClientRepository(db)
    client = repo.get_by_email(payload.email)
    if client is None:
        raise HTTPException(status_code=401, detail="Email no registrado")
    if not client.activo:
        raise HTTPException(status_code=401, detail="Cuenta desactivada")
    return AuthResponse(
        id=client.id,
        email=client.email,
        nombre=client.nombre,
        apellido=client.apellido,
        role=client.role,
    )
