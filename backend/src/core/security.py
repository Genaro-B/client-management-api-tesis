"""Seguridad: hash bcrypt y emisión/validación de tokens JWT (HS256).

Aislado de FastAPI a propósito: estas funciones son lógica pura y
testeable sin HTTP. Las dependencias de FastAPI (get_current_user,
require_admin) viven en src.core.deps y reusan estas funciones.
"""
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# Clave para firmar tokens JWT. En desarrollo tiene un default explícito;
# en producción DEBE setearse JWT_SECRET_KEY (ver README → Seguridad).
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-me")

# Expiración del token en minutos (default 480 = 8 horas).
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
    """Hashear una password con bcrypt (salt aleatorio por llamada)."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verificar una password contra su hash bcrypt.

    Devuelve False (nunca levanta) si el hash es inválido o falta:
    el caller trata el fallo como credenciales inválidas.
    """
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(client_id: int) -> str:
    """Emitir un JWT HS256 con sub=client_id, iat y exp (env ACCESS_TOKEN_EXPIRE_MINUTES).

    Sin refresh token: al expirar hay que volver a loguear.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(client_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> int:
    """Validar y decodificar un JWT. Devuelve el client_id (sub).

    Levanta jwt.PyJWTError si el token es inválido, está vencido o fue
    firmado con otra clave — el caller (core.deps) lo traduce a 401.
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload["sub"])