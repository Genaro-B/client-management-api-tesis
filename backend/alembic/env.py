"""Configuración de Alembic para migraciones.

Lee DATABASE_URL del entorno. Si no está definida, usa SQLite por defecto.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from alembic import context
import os
import sys

# Agregar la raíz del proyecto al path para poder importar src.*
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

config = context.config

# Leer DATABASE_URL del entorno o usar default
database_url = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Configurar la URL en la configuración de alembic
config.set_main_option("sqlalchemy.url", database_url)

# Logging (si existe alembic.ini lo usa)
if config.config_file_name:
    fileConfig(config.config_file_name)

# Importar los modelos para que Base.metadata los conozca
from src.database.base import Base
from src.models.client import Client

target_metadata = Base.metadata


def run_migrations_offline():
    """Ejecutar migraciones en modo offline (solo genera SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Ejecutar migraciones conectándose a la base de datos."""
    connectable = create_engine(database_url)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
