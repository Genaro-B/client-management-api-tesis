import os
from typing import Optional

from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY", "dev-api-key-123")


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """FastAPI dependency that validates the X-Api-Key header.

    Reads the expected key from the API_KEY env var (default: dev-api-key-123).
    Raises 401 if the header is missing or does not match.
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key
