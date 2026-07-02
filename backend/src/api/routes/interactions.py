import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from src.schemas.interaction import CreateInteraction, InteractionResponse
from src.models.interaction import Interaction
from src.services.interaction_service import (
    InteractionService,
    ValidationError,
    UnknownSourceError,
    IdempotencyConflict,
)
from src.core.auth import verify_api_key
from src.database.session import get_db

router = APIRouter()


class InteractionListResponse(BaseModel):
    id: int
    source: str
    user: Optional[str]
    payload: str
    intent: Optional[str]
    result: Optional[str]
    clientId: Optional[int]
    idempotency_key: Optional[str]
    timestamp: datetime

    model_config = {"from_attributes": True}


@router.get("/")
def list_interactions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all interactions, newest first."""
    items = (
        db.query(Interaction)
        .order_by(Interaction.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    total = db.query(Interaction).count()
    return {"items": items, "total": total}


@router.post("/", response_model=InteractionResponse, status_code=201)
def create_interaction(
    payload: CreateInteraction,
    db: Session = Depends(get_db),
    _auth_ok: str = Depends(verify_api_key),
    x_idempotency_key: Optional[str] = Header(None),
):
    """Persist an interaction event with optional client linking.

    Requires X-Api-Key header for authentication.
    Supports X-Idempotency-Key header to prevent duplicate processing.
    """
    service = InteractionService(db)
    try:
        client_lookup = payload.clientLookup.model_dump() if payload.clientLookup else None
        interaction = service.create(
            source=payload.source,
            payload=payload.payload,
            user=payload.user,
            intent=payload.intent,
            result=payload.result,
            clientLookup=client_lookup,
            idempotency_key=x_idempotency_key,
        )
        return InteractionResponse(id=interaction.id, timestamp=interaction.timestamp)
    except IdempotencyConflict as e:
        raise HTTPException(status_code=409, detail=str(e))
    except UnknownSourceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
