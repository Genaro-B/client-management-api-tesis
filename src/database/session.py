from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import DATABASE_URL

# Create engine and session factory. Tests can override DATABASE_URL via env var.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency-injectable database session for FastAPI endpoints.

    Usage in routes:
        db = Depends(get_db)

    This yields a session and ensures it is closed after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
