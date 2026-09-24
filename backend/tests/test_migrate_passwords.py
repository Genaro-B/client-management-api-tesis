"""Tests del script backend/scripts/migrate_passwords.py.

Cubre (spec auth-jwt, Requirement: Migración de usuarios existentes):
- `migrate` agrega las columnas si no existen (idempotente) y hashea
  `cambiar123` + flag True SOLO a filas con password_hash IS NULL.
- Correr 2× es seguro: no re-hashea lo migrado.
- `set --email --password` actualiza hash + flag False; crea un admin
  si el email no existe.
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from scripts.migrate_passwords import (
    ensure_columns,
    run_migrate,
    run_set,
)
from src.core.security import verify_password

DEFAULT_PASSWORD = "cambiar123"


@pytest.fixture
def db_path(tmp_path):
    """Path a un archivo SQLite temporal para cada test."""
    return str(tmp_path / "test_migrate.db")


def _engine(db_path):
    return create_engine(f"sqlite:///{db_path}")


def _crear_tabla_vieja(db_path):
    """Crea la tabla clients SIN las columnas de password (estado pre-migración)."""
    engine = _engine(db_path)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                telefono VARCHAR(50),
                email VARCHAR(255) NOT NULL UNIQUE,
                fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN NOT NULL DEFAULT 1,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                productos_asignados JSON DEFAULT '[]'
            )
        """))
    engine.dispose()


def _insertar_cliente(db_path, email, role="user"):
    engine = _engine(db_path)
    with engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO clients (nombre, apellido, email, role) "
            "VALUES (:n, :a, :e, :r)"
        ), {"n": "Cliente", "a": "Test", "e": email, "r": role})
    engine.dispose()


def _get_rows(db_path):
    engine = _engine(db_path)
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT email, password_hash, password_change_required "
            "FROM clients ORDER BY email"
        )).fetchall()
    engine.dispose()
    return rows


# ---------------------------------------------------------------------------
# migrate — agregar columnas + hash default
# ---------------------------------------------------------------------------


def test_migrate_agrega_columnas_y_hashea_solo_null(db_path):
    """Tabla vieja: migrate crea las columnas y hashea 'cambiar123' + flag True."""
    _crear_tabla_vieja(db_path)
    _insertar_cliente(db_path, "a@x.com")
    _insertar_cliente(db_path, "b@x.com")

    procesados = run_migrate(db_path)

    assert procesados == 2
    rows = _get_rows(db_path)
    assert len(rows) == 2
    for _, password_hash, flag in rows:
        assert password_hash is not None
        assert verify_password(DEFAULT_PASSWORD, password_hash), "hash debe ser de cambiar123"
        assert flag == 1


def test_migrate_es_idempotente(db_path):
    """Correr migrate 2× no re-hashea: segunda corrida procesa 0 filas."""
    _crear_tabla_vieja(db_path)
    _insertar_cliente(db_path, "a@x.com")
    _insertar_cliente(db_path, "b@x.com")

    assert run_migrate(db_path) == 2

    hashes_primera = _get_rows(db_path)

    assert run_migrate(db_path) == 0

    hashes_segunda = _get_rows(db_path)
    assert hashes_segunda == hashes_primera, "el hash no debe cambiar en la 2ª corrida"


def test_migrate_no_toca_cliente_ya_migrado(db_path):
    """Si un cliente ya tiene password_hash, no se re-procesa."""
    _crear_tabla_vieja(db_path)
    _insertar_cliente(db_path, "a@x.com")
    _insertar_cliente(db_path, "b@x.com")
    # Marcar 'a@x.com' como ya migrado en forma directa
    engine = _engine(db_path)
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE clients ADD COLUMN password_hash VARCHAR(255)"))
        conn.execute(text("ALTER TABLE clients ADD COLUMN password_change_required BOOLEAN NOT NULL DEFAULT 1"))
        conn.execute(text(
            "UPDATE clients SET password_hash = 'hash-previo' WHERE email = 'a@x.com'"
        ))
    engine.dispose()

    procesados = run_migrate(db_path)

    assert procesados == 1  # solo el que tenía NULL
    rows = {email: password_hash for email, password_hash, _ in _get_rows(db_path)}
    assert rows["a@x.com"] == "hash-previo", "el ya migrado no se toca"
    assert rows["b@x.com"] != "hash-previo"


def test_ensure_columns_idempotente(db_path):
    """ensure_columns puede correrse 2× sin error."""
    _crear_tabla_vieja(db_path)
    ensure_columns(db_path)
    ensure_columns(db_path)  # no debe fallar

    engine = _engine(db_path)
    with engine.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(clients)")).fetchall()}
    engine.dispose()
    assert "password_hash" in cols
    assert "password_change_required" in cols


# ---------------------------------------------------------------------------
# set — crear/actualizar password de un admin
# ---------------------------------------------------------------------------


def test_set_actualiza_hash_y_flag(db_path):
    """Cliente admin existente: set cambia el hash y pone flag False."""
    _crear_tabla_vieja(db_path)
    _insertar_cliente(db_path, "admin@x.com", role="admin")

    run_set(db_path, email="admin@x.com", password="secreta123")

    rows = _get_rows(db_path)
    assert len(rows) == 1
    email, password_hash, flag = rows[0]
    assert email == "admin@x.com"
    assert verify_password("secreta123", password_hash)
    assert flag == 0


def test_set_crea_admin_si_no_existe(db_path):
    """Email inexistente: set crea la cuenta con role admin + flag False."""
    _crear_tabla_vieja(db_path)

    run_set(db_path, email="nuevo@x.com", password="secreta123")

    engine = _engine(db_path)
    with engine.connect() as conn:
        row = conn.execute(text(
            "SELECT email, role, password_hash, password_change_required "
            "FROM clients WHERE email = 'nuevo@x.com'"
        )).fetchone()
    engine.dispose()
    assert row is not None
    assert row.role == "admin"
    assert verify_password("secreta123", row.password_hash)
    assert row.password_change_required == 0