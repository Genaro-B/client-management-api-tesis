from sqlalchemy.orm import Session
from src.models.client import Client
from typing import List, Optional, Tuple


class ClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, client: Client) -> Client:
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def get_by_id(self, client_id: int) -> Optional[Client]:
        return self.db.query(Client).filter(Client.id == client_id, Client.activo == True).first()

    def get_by_email(self, email: str) -> Optional[Client]:
        return self.db.query(Client).filter(Client.email == email, Client.activo == True).first()

    def list(self, limit: int = 10, offset: int = 0, nombre: Optional[str] = None) -> Tuple[List[Client], int]:
        q = self.db.query(Client).filter(Client.activo == True)
        if nombre:
            q = q.filter(Client.nombre.ilike(f"%{nombre}%"))
        total = q.count()
        items = q.offset(offset).limit(limit).all()
        return items, total

    def update(self, client: Client, **fields) -> Client:
        for k, v in fields.items():
            setattr(client, k, v)
        self.db.commit()
        self.db.refresh(client)
        return client

    def soft_delete(self, client: Client) -> None:
        client.activo = False
        self.db.commit()
