from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.schemas.client import LoginRequest, AuthResponse, ChangePasswordRequest, UserOut
from src.repositories.client_repo import ClientRepository
from src.database.session import get_db
from src.core.security import verify_password, create_access_token, hash_password
from src.core.deps import get_current_user
from src.models.client import Client

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Autenticar usuario del panel con email + password (bcrypt) y emitir JWT.

    Solo cuentas con role="admin" pueden loguearse (los clients con role
    "user" son prospectos del negocio, no usuarios del panel). Cualquier
    fallo responde 401 con detalle genérico: no se revela si el email
    existe, si la cuenta está inactiva o si la password es incorrecta.
    """
    repo = ClientRepository(db)
    client = repo.get_by_email(payload.email)

    if client is None or not client.activo or client.role != "admin":
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if not verify_password(payload.password, client.password_hash or ""):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token(client.id)
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(client),
    )


@router.post("/change-password", status_code=200)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user),
):
    """Cambiar la password del usuario autenticado (prueba de posesión).

    Exige la password actual: si no coincide -> 401 y el hash no cambia.
    Al éxito actualiza el hash y setea password_change_required=False
    (cierra el flujo de cambio obligatorio post-migración).
    """
    if not verify_password(payload.current_password, current_user.password_hash or ""):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    current_user.password_hash = hash_password(payload.new_password)
    current_user.password_change_required = False
    db.commit()
    return {"status": "ok"}