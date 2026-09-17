from fastapi import HTTPException


# Excepciones específicas de la aplicación y ayudantes para convertirlas a respuestas HTTP.

class EmailAlreadyExists(Exception):
    """Se lanza cuando se intenta crear o actualizar un cliente con un email que ya existe."""


class UnsupportedImageTypeError(Exception):
    """Se lanza cuando el archivo no es una imagen JPG, PNG o WebP válida."""


class ImageTooLargeError(Exception):
    """Se lanza cuando la imagen supera el tamaño máximo permitido (2MB)."""


def to_http_exception(exc: Exception) -> HTTPException:
    """Mapear excepciones del dominio a HTTPException para el manejo en FastAPI."""
    if isinstance(exc, EmailAlreadyExists):
        return HTTPException(status_code=400, detail=str(exc) or "El email ya existe")
    if isinstance(exc, UnsupportedImageTypeError):
        return HTTPException(status_code=415, detail=str(exc) or "Tipo de imagen no soportado")
    if isinstance(exc, ImageTooLargeError):
        return HTTPException(status_code=413, detail=str(exc) or "La imagen supera el tamaño máximo de 2MB")
    # Caso por defecto
    return HTTPException(status_code=500, detail="Error interno del servidor")
