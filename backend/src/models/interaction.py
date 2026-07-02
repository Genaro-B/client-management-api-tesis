from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index, func
from src.database.base import Base


class Interaction(Base):
    """Model representing a persisted interaction event.

    Stores incoming webhook events, user messages, external system callbacks
    with optional linkage to a client record for auditing and analytics.
    """

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    clientId = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    user = Column(String(255), nullable=True)
    source = Column(String(50), nullable=False)
    payload = Column(Text, nullable=False)
    intent = Column(String(255), nullable=True)
    result = Column(String(255), nullable=True)
    idempotency_key = Column(String(255), nullable=True, unique=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_interactions_client_id", "clientId"),
        Index("ix_interactions_timestamp", "timestamp"),
    )
