from sqlalchemy.orm import Session

from src.models.client import Client
from src.repositories.client_repo import ClientRepository


class RegistrationService:
    """Alta/vinculación de un prospecto de Telegram (sin login).

    Reglas:
    - Idempotente por `telegram_user_id`: si ya está vinculado, devuelve el
      cliente existente (no crea otro).
    - Si no está vinculado pero el teléfono coincide con un cliente previo
      (creado antes de la migración 0008), lo linkea en lugar de duplicar.
    - Email placeholder `tg{telegram_user_id}@telegram.local` para cumplir el
      `NOT NULL + UNIQUE` de `Client.email` sin migrar la columna.
    """

    def __init__(self, db: Session):
        self.repo = ClientRepository(db)
        self.db = db

    def register_bot(
        self,
        *,
        telegram_user_id: str,
        nombre: str,
        apellido: str = "",
        telefono: str = None,
    ):
        """Devuelve `(client, created)`. `created` es False si ya existía."""
        if not telegram_user_id:
            raise ValueError("telegram_user_id es requerido")
        if not nombre:
            raise ValueError("nombre es requerido")

        # 1. Ya vinculado por identidad de Telegram -> idempotente.
        existing = self.repo.get_by_telegram_user_id(telegram_user_id)
        if existing:
            return existing, False

        # 2. Cliente previo (sin columna) con el mismo teléfono -> link.
        if telefono:
            by_phone = self.repo.get_by_telefono(telefono)
            if by_phone:
                self.repo.update(by_phone, telegram_user_id=telegram_user_id)
                return by_phone, False

        # 3. Alta nueva de prospecto (password_hash NULL: nunca loguea).
        client = Client(
            nombre=nombre,
            apellido=apellido if apellido is not None else "",
            telefono=telefono,
            email=f"tg{telegram_user_id}@telegram.local",
            role="user",
            activo=True,
            telegram_user_id=telegram_user_id,
        )
        return self.repo.create(client), True
