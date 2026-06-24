from sqlalchemy.orm import Session
from src.models.client import Client
from typing import List, Optional, Tuple


class ClientRepository:
    """Repository responsible for CRUD operations against the clients table.

    This class is intentionally thin: it translates high-level repository
    calls into SQLAlchemy ORM operations. Business rules remain in the service layer.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, client: Client) -> Client:
        """Persist a new client instance and return the attached object."""
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def get_by_id(self, client_id: int) -> Optional[Client]:
        """Return a client by primary key or None if not found."""
        return self.db.query(Client).filter(Client.id == client_id).first()

    def get_by_email(self, email: str) -> Optional[Client]:
        """Return a client matching the given email or None."""
        return self.db.query(Client).filter(Client.email == email).first()

    def list(self, limit: int = 10, offset: int = 0, nombre: Optional[str] = None) -> Tuple[List[Client], int]:
        """List active clients with optional text query over nombre."""
        q = self.db.query(Client).filter(Client.activo == True)
        if nombre:
            q = q.filter(Client.nombre.ilike(f"%{nombre}%"))
        total = q.count()
        items = q.offset(offset).limit(limit).all()
        return items, total

    def update(self, client: Client, **fields) -> Client:
        """Apply field updates to a client instance and persist changes."""
        for k, v in fields.items():
            setattr(client, k, v)
        self.db.commit()
        self.db.refresh(client)
        return client

    def soft_delete(self, client: Client) -> None:
        """Perform a logical delete by setting activo=False."""
        client.activo = False
        self.db.commit()
