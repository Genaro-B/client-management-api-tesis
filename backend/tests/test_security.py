"""Tests unitarios de src.core.security: bcrypt (hash/verify) y JWT.

Cubren el contrato definido en design.md:
- hash_password / verify_password (bcrypt roundtrip)
- create_access_token / decode_token (HS256, sub=client_id, exp≈480min)
"""
import time

import pytest

from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# ---------------------------------------------------------------------------
# bcrypt
# ---------------------------------------------------------------------------


def test_hash_password_roundtrip():
    """Hash de una password verifica OK contra la misma password."""
    hashed = hash_password("cambiar123")
    assert hashed != "cambiar123"
    assert verify_password("cambiar123", hashed) is True


def test_hash_password_saltea_cada_hash():
    """Mismo input -> hashes distintos (salt aleatorio por hash)."""
    h1 = hash_password("misma-password")
    h2 = hash_password("misma-password")
    assert h1 != h2


def test_verify_password_distinta_falla():
    """Password incorrecta no verifica."""
    hashed = hash_password("correcta")
    assert verify_password("incorrecta", hashed) is False


def test_verify_password_con_hash_invalido_devuelve_false():
    """Un hash corrupto/no-bcrypt no levanta excepción: devuelve False."""
    assert verify_password("cualquiera", "no-es-un-hash") is False
    assert verify_password("cualquiera", None) is False


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------


def test_create_access_token_decodifica_con_sub_y_exp():
    """Token decodificable con sub = client_id y exp futuro acotado por env."""
    token = create_access_token(client_id=42)
    payload = decode_token(token)
    assert payload == 42


def test_token_expira_segun_access_token_expire_minutes():
    """exp está entre 1 y ACCESS_TOKEN_EXPIRE_MINUTES minutos en el futuro."""
    import jwt as pyjwt

    token = create_access_token(client_id=7)
    payload = pyjwt.decode(token, options={"verify_signature": False})
    exp = payload["exp"]
    now = time.time()
    min_exp = now + 60            # >= 1 min
    max_exp = now + ACCESS_TOKEN_EXPIRE_MINUTES * 60 + 60  # tolerancia de reloj
    assert min_exp <= exp <= max_exp


def test_token_vencido_levanta_error():
    """Un token con exp en el pasado es rechazado por decode_token."""
    token = create_access_token(client_id=1)
    # Re-firmar el mismo token con exp vencida (-10 min) usando la key real
    import jwt as pyjwt
    from src.core.security import JWT_SECRET_KEY

    expired = pyjwt.encode(
        {"sub": "1", "exp": time.time() - 600, "iat": time.time() - 3600},
        JWT_SECRET_KEY,
        algorithm="HS256",
    )
    with pytest.raises(pyjwt.PyJWTError):
        decode_token(expired)


def test_token_tamperead_levanta_error():
    """Un token firmado con otra clave es rechazado (InvalidSignatureError)."""
    import jwt as pyjwt

    forged = pyjwt.encode(
        {"sub": "1", "exp": time.time() + 3600},
        "otra-clave-secreta",
        algorithm="HS256",
    )
    with pytest.raises(pyjwt.PyJWTError):
        decode_token(forged)


def test_token_malformado_levanta_error():
    """Un string que no es JWT es rechazado."""
    with pytest.raises(pyjwt := __import__("jwt").PyJWTError):
        decode_token("esto-no-es-un-token")


def test_token_incluye_iat():
    """El payload incluye iat (momento de emisión)."""
    import jwt as pyjwt

    token = create_access_token(client_id=9)
    payload = pyjwt.decode(token, options={"verify_signature": False})
    assert "iat" in payload
    assert decode_token(token) == 9