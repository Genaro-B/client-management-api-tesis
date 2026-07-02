"""Database connection module for the Streamlit dashboard.

Creates a SQLAlchemy engine and session factory that connects to the same
database used by the FastAPI backend. Adds the backend/ directory to sys.path
so that `src.models`, `src.database`, and other backend packages are importable.
"""

import os
import sys
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── Add backend/ to sys.path so we can import src.* modules ──

BACKEND_DIR = Path(__file__).parent.parent / "backend"
BACKEND_DIR_str = str(BACKEND_DIR.resolve())

if BACKEND_DIR_str not in sys.path:
    sys.path.insert(0, BACKEND_DIR_str)

# ── Database URL ──
# Default to backend/dev.db (SQLite) for local development.
# Override via DATABASE_URL env var for MySQL/Postgres in production.

_DEFAULT_SQLITE_PATH = BACKEND_DIR / "dev.db"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{_DEFAULT_SQLITE_PATH.as_posix()}",
)

# ── Engine & Session ──

engine = create_engine(
    DATABASE_URL,
    # SQLite needs check_same_thread=False to work across multiple sessions
    connect_args=(
        {"check_same_thread": False}
        if DATABASE_URL.startswith("sqlite")
        else {}
    ),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session():
    """Context manager that provides a DB session with auto-commit/rollback.

    Usage:
        with get_session() as session:
            clients = session.query(Client).all()
        # session is committed on success, rolled back on error, closed after
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
