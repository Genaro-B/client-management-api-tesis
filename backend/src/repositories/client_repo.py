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

    def get_by_telefono(self, telefono: str) -> Optional[Client]:
        """Return a client matching the given phone number or None."""
        return self.db.query(Client).filter(Client.telefono == telefono).first()

    def list(self, limit: int = 10, offset: int = 0, nombre: Optional[str] = None) -> Tuple[List[Client], int]:
        """List active non-admin clients with optional text query over nombre."""
        q = self.db.query(Client).filter(Client.activo == True, Client.role != 'admin')
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

    def list_all(self) -> List[Client]:
        """Return ALL non-admin clients (activos e inactivos), sin paginación."""
        return self.db.query(Client).filter(Client.role != 'admin').order_by(Client.id).all()

    def list_inactive(self, limit: int = 50, offset: int = 0, nombre: Optional[str] = None) -> Tuple[List[Client], int]:
        """List inactive non-admin clients with optional text query."""
        q = self.db.query(Client).filter(Client.activo == False, Client.role != 'admin')
        if nombre:
            q = q.filter(Client.nombre.ilike(f"%{nombre}%"))
        total = q.count()
        items = q.offset(offset).limit(limit).all()
        return items, total

    def restore(self, client: Client) -> Client:
        """Re-activate a soft-deleted client."""
        client.activo = True
        self.db.commit()
        self.db.refresh(client)
        return client

    def soft_delete(self, client: Client) -> None:
        """Perform a logical delete by setting activo=False."""
        client.activo = False
        self.db.commit()

    # ------------------------------------------------------------------
    # Productos Asignados
    # ------------------------------------------------------------------

    def get_productos(self, client: Client) -> list:
        """Return the list of assigned products for a client."""
        return client.productos_asignados if client.productos_asignados is not None else []

    def set_productos(self, client: Client, productos: list) -> list:
        """Replace all assigned products, commit, refresh, return the list."""
        client.productos_asignados = productos
        self.db.commit()
        self.db.refresh(client)
        return client.productos_asignados if client.productos_asignados is not None else []

    def add_producto(self, client: Client, producto: dict) -> list:
        """Append a product (or increment quantity if producto_id exists), commit, refresh, return list.

        NOTE: We build a completely new list of NEW dicts to ensure SQLAlchemy's
        JSON column change tracking detects the mutation — mutating dicts in-place
        on a JSON column does NOT trigger a flush for SQLite (the underlying
        object identity comparison does not detect in-place mutations).
        """
        actual = client.productos_asignados if client.productos_asignados is not None else []
        found = False
        productos = []
        for p in actual:
            if p["producto_id"] == producto["producto_id"]:
                productos.append({
                    "producto_id": p["producto_id"],
                    "nombre": p["nombre"],
                    "precio": p["precio"],
                    "cantidad": p["cantidad"] + producto["cantidad"],
                })
                found = True
            else:
                productos.append(dict(p))
        if not found:
            productos.append(producto)
        client.productos_asignados = productos
        self.db.commit()
        self.db.refresh(client)
        return client.productos_asignados if client.productos_asignados is not None else []

    def remove_producto(self, client: Client, producto_id: int) -> list:
        """Filter out a producto_id, commit, refresh, return the list."""
        actual = client.productos_asignados if client.productos_asignados is not None else []
        client.productos_asignados = [p for p in actual if p["producto_id"] != producto_id]
        self.db.commit()
        self.db.refresh(client)
        return client.productos_asignados if client.productos_asignados is not None else []
