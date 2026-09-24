"""Script idempotente de migración de passwords para el panel.

Uso:
    python scripts/migrate_passwords.py migrate
        Agrega las columnas password_hash / password_change_required si no
        existen y asigna el hash bcrypt de `cambiar123` + flag True a TODO
        cliente existente con password_hash IS NULL. Idempotente: correr 2×
        no re-hashea lo ya migrado.

    python scripts/migrate_passwords.py set --email <email> --password <pw>
        Crea o actualiza la password de una cuenta del panel (role admin):
        setea el hash de <pw>, pone password_change_required=False. Si el
        email no existe, crea el cliente con role="admin".

Las funciones puras (ensure_columns, run_migrate, run_set) son testeables
desde tests/test_migrate_passwords.py con una BD SQLite temporal.
"""
import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

# Permite `python scripts/migrate_passwords.py` desde backend/ sin instalar
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from src.core.security import hash_password  # noqa: E402

DEFAULT_PASSWORD = "cambiar123"

_COLUMNS = [
    ("password_hash", "VARCHAR(255)"),
    ("password_change_required", "BOOLEAN NOT NULL DEFAULT 1"),
]


def _engine(db_path: str):
    """Engine SQLite apuntando al archivo de BD."""
    return create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})


def ensure_columns(db_path: str) -> None:
    """Agrega las columnas de password si no existen (ALTER TABLE idempotente)."""
    engine = _engine(db_path)
    with engine.begin() as conn:
        existing = {
            row[1] for row in conn.execute(text("PRAGMA table_info(clients)")).fetchall()
        }
        for name, definition in _COLUMNS:
            if name not in existing:
                conn.execute(text(f"ALTER TABLE clients ADD COLUMN {name} {definition}"))
    engine.dispose()


def run_migrate(db_path: str) -> int:
    """Migra clientes sin password: hash de `cambiar123` + flag True.

    Devuelve la cantidad de filas procesadas (0 en una re-corrida).
    """
    ensure_columns(db_path)
    engine = _engine(db_path)
    with engine.begin() as conn:
        result = conn.execute(text(
            "UPDATE clients "
            "SET password_hash = :hash, password_change_required = 1 "
            "WHERE password_hash IS NULL"
        ), {"hash": hash_password(DEFAULT_PASSWORD)})
    engine.dispose()
    return result.rowcount or 0


def run_set(db_path: str, email: str, password: str) -> None:
    """Crea o actualiza la password de una cuenta admin del panel.

    Si el email no existe, crea el cliente con role="admin".
    Siempre deja password_change_required=False.
    """
    ensure_columns(db_path)
    engine = _engine(db_path)
    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT id FROM clients WHERE email = :email"),
            {"email": email},
        ).fetchone()
        if exists is None:
            conn.execute(text(
                "INSERT INTO clients (nombre, apellido, email, role, "
                "password_hash, password_change_required) "
                "VALUES ('Admin', 'Panel', :email, 'admin', :hash, 0)"
            ), {"email": email, "hash": hash_password(password)})
        else:
            conn.execute(text(
                "UPDATE clients SET password_hash = :hash, "
                "password_change_required = 0 WHERE email = :email"
            ), {"email": email, "hash": hash_password(password)})
    engine.dispose()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        default="dev.db",
        help="Path al archivo SQLite (default: dev.db, relativo a backend/)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("migrate", help="Hashear 'cambiar123' a clientes sin password")

    set_parser = subparsers.add_parser("set", help="Crear/actualizar password de una cuenta admin")
    set_parser.add_argument("--email", required=True, help="Email de la cuenta")
    set_parser.add_argument("--password", required=True, help="Nueva password")

    args = parser.parse_args(argv)
    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = BACKEND_DIR / db_path

    if args.command == "migrate":
        procesados = run_migrate(str(db_path))
        print(f"Migración completa. Filas procesadas: {procesados}")
    elif args.command == "set":
        run_set(str(db_path), email=args.email, password=args.password)
        print(f"Password actualizada para {args.email} (password_change_required=False)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())