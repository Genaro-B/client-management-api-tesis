"""Abstracción de almacenamiento de imágenes de productos.

El punto pedagógico del cambio: la API y el servicio dependen SOLO de la
interfaz `ImageStorage`; `LocalImageStorage` es una implementación concreta
sobre filesystem local. Un proveedor externo (p. ej. Cloudinary) podría
sumarse después como otra implementación sin tocar la API ni el frontend.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

from src.core.config import ALLOWED_IMAGE_TYPES, MAX_IMAGE_SIZE, UPLOAD_DIR
from src.core.exceptions import ImageTooLargeError, UnsupportedImageTypeError

# Extensión de archivo según content-type permitido.
_EXTENSION_BY_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def detect_image_type(image_bytes: bytes):
    """Detectar el content-type de una imagen por sus magic bytes.

    Devuelve 'image/jpeg', 'image/png' o 'image/webp', o None si los bytes
    no corresponden a un formato soportado. Función pura: ideal para tests.
    """
    if image_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if image_bytes[:4] == b"\x89PNG":
        return "image/png"
    if (
        len(image_bytes) >= 12
        and image_bytes[:4] == b"RIFF"
        and image_bytes[8:12] == b"WEBP"
    ):
        return "image/webp"
    return None


class ImageStorage(ABC):
    """Contrato común de almacenamiento de imágenes de producto."""

    @abstractmethod
    def save(self, image_bytes: bytes, content_type: str, product_id: int) -> str:
        """Guardar una imagen y devolver su URL pública."""

    @abstractmethod
    def delete(self, url: str) -> None:
        """Eliminar el archivo de una URL pública. No falla si no existe."""

    @abstractmethod
    def validate(self, image_bytes: bytes, content_type: str) -> None:
        """Validar tipo y tamaño de la imagen. Lanza error si es inválida."""


class LocalImageStorage(ImageStorage):
    """Implementación sobre filesystem local dentro de UPLOAD_DIR.

    Genera nombres `{uuid4().hex}.{ext}` en la carpeta `{product_id}/` y
    devuelve la URL pública `/static/uploads/{product_id}/{uuid}.{ext}`.
    """

    def __init__(self, base_dir: str = UPLOAD_DIR):
        self.base_dir = Path(base_dir)

    def validate(self, image_bytes: bytes, content_type: str) -> None:
        """Rechazar por tamaño (>2MB) o por tipo (content-type + magic bytes)."""
        if len(image_bytes) > MAX_IMAGE_SIZE:
            raise ImageTooLargeError("La imagen supera el tamaño máximo de 2MB")
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise UnsupportedImageTypeError("Tipo de imagen no soportado")
        detected = detect_image_type(image_bytes)
        if detected is None or detected != content_type:
            raise UnsupportedImageTypeError("Tipo de imagen no soportado")

    def save(self, image_bytes: bytes, content_type: str, product_id: int) -> str:
        """Validar, persistir y devolver la URL pública de la imagen."""
        self.validate(image_bytes, content_type)
        extension = _EXTENSION_BY_TYPE[content_type]
        folder = self.base_dir / str(product_id)
        folder.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}{extension}"
        (folder / filename).write_bytes(image_bytes)
        return f"/static/uploads/{product_id}/{filename}"

    def delete(self, url: str) -> None:
        """Resolver la URL pública a un path local y borrar el archivo.

        Incluye guard de path traversal: cualquier ruta que escape de
        UPLOAD_DIR se rechaza, no se borra nada.
        """
        if not url:
            return
        relative = url.replace("/static/uploads/", "", 1)
        file_path = (self.base_dir / relative).resolve()
        base_resolved = self.base_dir.resolve()
        if not file_path.is_relative_to(base_resolved):
            raise ValueError("La URL de imagen escapa del directorio de uploads")
        if file_path.exists():
            file_path.unlink()