from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, func, Index
from src.database.base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(50), nullable=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    activo = Column(Boolean, nullable=False, server_default="1")
    role = Column(String(20), nullable=False, server_default="user")
    # Autenticación del panel: solo cuentas con role="admin" loguean.
    # password_hash es NULL para clientes/prospectos (no son usuarios del panel).
    password_hash = Column(String(255), nullable=True)
    # True obliga al cambio de password en el primer login (migración default).
    password_change_required = Column(Boolean, nullable=False, server_default="1", default=True)
    productos_asignados = Column(JSON, default=list, server_default="[]")

    __table_args__ = (
        Index("ix_clients_email_unique", "email", unique=True),
    )
