from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.schemas.client import CreateClient, UpdateClient, ClientResponse
from src.repositories.client_repo import ClientRepository
from src.services.client_service import ClientService, EmailAlreadyExists
from src.database.session import get_db
from src.core.exceptions import to_http_exception

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(payload: CreateClient, db: Session = Depends(get_db)):
    """Crear un nuevo cliente. Las reglas de negocio se validan en la capa de servicio."""
    service = ClientService(db)
    try:
        # Nota: ClientService espera parámetros primitivos. Desempaquetamos el payload.
        client = service.create(
            nombre=payload.nombre,
            apellido=payload.apellido,
            telefono=payload.telefono,
            email=payload.email,
        )
        return client
    except EmailAlreadyExists as e:
        raise to_http_exception(e)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    repo = ClientRepository(db)
    client = repo.get_by_id(client_id)
    if client is None or not client.activo:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client


@router.get("/")
def list_clients(q: str = None, limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """Listar clientes activos. Soporta búsqueda por nombre y paginación."""
    repo = ClientRepository(db)
    items, total = repo.list(limit=limit, offset=offset, nombre=q)
    return {"items": items, "total": total}


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, payload: UpdateClient, db: Session = Depends(get_db)):
    service = ClientService(db)
    try:
        return service.update(client_id, **payload.dict(exclude_unset=True))
    except EmailAlreadyExists as e:
        raise to_http_exception(e)


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    repo = ClientRepository(db)
    client = repo.get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    repo.soft_delete(client)
    return None
