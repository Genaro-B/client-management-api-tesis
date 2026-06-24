from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import DATABASE_URL

# Crear el engine y la fábrica de sesiones. Los tests pueden sobreescribir DATABASE_URL via variable de entorno.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependencia inyectable que ofrece una sesión de BD para los endpoints de FastAPI.

    Uso en routes:
        db = Depends(get_db)

    Esta función cede una sesión y asegura su cierre al finalizar la petición.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
