from fastapi import HTTPException


# Excepciones específicas de la aplicación y ayudantes para convertirlas a respuestas HTTP.

class EmailAlreadyExists(Exception):
    """Se lanza cuando se intenta crear o actualizar un cliente con un email que ya existe."""


def to_http_exception(exc: Exception) -> HTTPException:
    """Mapear excepciones del dominio a HTTPException para el manejo en FastAPI."""
    if isinstance(exc, EmailAlreadyExists):
        return HTTPException(status_code=400, detail=str(exc) or "El email ya existe")
    # Caso por defecto
    return HTTPException(status_code=500, detail="Error interno del servidor")
