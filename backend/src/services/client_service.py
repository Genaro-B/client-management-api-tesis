from src.repositories.client_repo import ClientRepository
from src.models.client import Client
from src.core.exceptions import EmailAlreadyExists
from sqlalchemy.orm import Session


class ClientService:
    """Service layer implementing business rules for Client operations.

    Responsibilities:
    - enforce uniqueness of email
    - coordinate repository operations
    - perform higher-level validations
    """

    def __init__(self, db: Session):
        # The service composes a repository instance to perform persistence operations.
        self.repo = ClientRepository(db)
        self.db = db

    def create(self, *, nombre, apellido, telefono, email) -> Client:
        # Business rule: unique email
        existing = self.repo.get_by_email(email)
        if existing:
            raise EmailAlreadyExists("email already exists")
        client = Client(nombre=nombre, apellido=apellido, telefono=telefono, email=email)
        return self.repo.create(client)

    def get(self, client_id: int):
        return self.repo.get_by_id(client_id)

    def list(self, limit=10, offset=0, nombre=None):
        return self.repo.list(limit=limit, offset=offset, nombre=nombre)

    def update(self, client_id: int, **fields):
        client = self.repo.get_by_id(client_id)
        if not client:
            return None
        if 'email' in fields and fields['email'] != client.email:
            if self.repo.get_by_email(fields['email']):
                raise EmailAlreadyExists("email already exists")
        return self.repo.update(client, **fields)

    def soft_delete(self, client_id: int):
        client = self.repo.get_by_id(client_id)
        if not client:
            return False
        self.repo.soft_delete(client)
        return True
