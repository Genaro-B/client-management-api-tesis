from typing import Optional

from sqlalchemy.orm import Session

from src.models.interaction import Interaction


class InteractionRepository:
    """Repository responsible for CRUD operations against the interactions table."""

    def __init__(self, db: Session):
        self.db = db

    def save(self, interaction: Interaction) -> Interaction:
        """Persist a new interaction and return the attached object."""
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def get_by_idempotency_key(self, key: str) -> Optional[Interaction]:
        """Return the interaction matching the given idempotency key, or None."""
        return self.db.query(Interaction).filter(Interaction.idempotency_key == key).first()
