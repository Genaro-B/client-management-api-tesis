from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from src.schemas.client import CreateClient, UpdateClient, ClientResponse
from src.db import SessionLocal
from src.services.client_service import ClientService, EmailAlreadyExists

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(payload: CreateClient, db=Depends(get_db)):
    service = ClientService(db)
    try:
        client = service.create(**payload.dict())
    except EmailAlreadyExists:
        raise HTTPException(status_code=400, detail="Email already exists")
    return client


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db=Depends(get_db)):
    service = ClientService(db)
    client = service.get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("/", response_model=List[ClientResponse])
def list_clients(limit: int = Query(10, ge=1, le=100), offset: int = 0, nombre: str = None, db=Depends(get_db)):
    service = ClientService(db)
    items, total = service.list(limit=limit, offset=offset, nombre=nombre)
    return items


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, payload: UpdateClient, db=Depends(get_db)):
    service = ClientService(db)
    try:
        client = service.update(client_id, **{k: v for k, v in payload.dict().items() if v is not None})
    except EmailAlreadyExists:
        raise HTTPException(status_code=400, detail="Email already exists")
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.delete("/{client_id}")
def delete_client(client_id: int, db=Depends(get_db)):
    service = ClientService(db)
    ok = service.soft_delete(client_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"ok": True}
