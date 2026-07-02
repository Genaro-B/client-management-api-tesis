from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ClientLookup(BaseModel):
    """Optional lookup to link an interaction to an existing client."""
    email: Optional[str] = None
    telefono: Optional[str] = None


class CreateInteraction(BaseModel):
    """Schema for incoming interaction creation requests."""
    source: str = Field(...)
    payload: str = Field(...)
    user: Optional[str] = None
    intent: Optional[str] = None
    result: Optional[str] = None
    clientLookup: Optional[ClientLookup] = None


class InteractionResponse(BaseModel):
    """Response schema returned after persisting an interaction."""
    id: int
    timestamp: datetime

    model_config = {"from_attributes": True}
