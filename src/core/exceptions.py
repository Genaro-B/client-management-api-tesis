from fastapi import HTTPException


# Application-specific exceptions and helpers to convert them to HTTP responses.

class EmailAlreadyExists(Exception):
    """Raised when an attempt is made to create or update a client with an email that already exists."""


def to_http_exception(exc: Exception) -> HTTPException:
    """Map domain exceptions to HTTPException for FastAPI error handling."""
    if isinstance(exc, EmailAlreadyExists):
        return HTTPException(status_code=400, detail=str(exc) or "Email already exists")
    # Fallback
    return HTTPException(status_code=500, detail="Internal server error")
