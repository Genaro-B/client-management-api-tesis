from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from src.models.interaction import Interaction
from src.repositories.interaction_repo import InteractionRepository
from src.repositories.client_repo import ClientRepository

# Known interaction sources
VALID_SOURCES = {"telegram", "webhook", "n8n", "api", "system"}


class ValidationError(Exception):
    """Domain exception for invalid interaction input."""

    pass


class UnknownSourceError(ValidationError):
    """Raised when the provided source is not in the allowed set."""

    pass


class IdempotencyConflict(Exception):
    """Raised when an interaction with the same idempotency key already exists."""

    pass


class InteractionService:
    """Service layer implementing business rules for Interaction operations.

    Responsibilities:
    - validate input payload and source
    - resolve optional clientLookup to a clientId
    - enforce idempotency via idempotency_key
    - coordinate repository operations
    """

    def __init__(self, db: Session):
        self.interaction_repo = InteractionRepository(db)
        self.client_repo = ClientRepository(db)
        self.db = db

    def create(
        self,
        *,
        source: str,
        payload: str,
        user: Optional[str] = None,
        intent: Optional[str] = None,
        result: Optional[str] = None,
        clientLookup: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Interaction:
        """Create and persist a new interaction with optional client linking.

        Validates that source and payload are present, resolves clientLookup
        if provided, enforces idempotency when an idempotency_key is given,
        and delegates persistence to the repository.
        """
        # --- validation ---
        if not source:
            raise ValidationError("source is required")
        if source not in VALID_SOURCES:
            raise UnknownSourceError(
                f"unknown source '{source}'. Valid sources: {', '.join(sorted(VALID_SOURCES))}"
            )
        if not payload:
            raise ValidationError("payload is required")

        # --- idempotency check ---
        if idempotency_key:
            existing = self.interaction_repo.get_by_idempotency_key(idempotency_key)
            if existing:
                raise IdempotencyConflict(
                    f"Interaction with idempotency_key '{idempotency_key}' already exists"
                )

        # --- resolve clientLookup ---
        client_id = None
        if clientLookup:
            email = clientLookup.get("email")
            telefono = clientLookup.get("telefono")
            if email:
                client = self.client_repo.get_by_email(email)
                if client:
                    client_id = client.id
            elif telefono:
                client = self.client_repo.get_by_telefono(telefono)
                if client:
                    client_id = client.id

        interaction = Interaction(
            source=source,
            payload=payload,
            user=user,
            intent=intent,
            result=result,
            clientId=client_id,
            idempotency_key=idempotency_key,
        )
        return self.interaction_repo.save(interaction)
