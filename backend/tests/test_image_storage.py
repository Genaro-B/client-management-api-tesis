"""Tests unitarios del módulo de storage de imágenes (TDD).

Cubre:
- detect_image_type: detección de tipo por magic bytes (función pura)
- LocalImageStorage.validate: validación de tipo y tamaño
- LocalImageStorage.save: generación de uuid, carpeta por product_id, URL pública
- LocalImageStorage.delete: borrado, idempotencia y guard de path traversal
"""
import pytest

from src.core.config import MAX_IMAGE_SIZE
from src.core.exceptions import ImageTooLargeError, UnsupportedImageTypeError
from src.storage.image_storage import LocalImageStorage, detect_image_type


# --- detect_image_type (magic bytes) ---

def test_detect_image_type_jpeg():
    """Los bytes FF D8 FF corresponden a image/jpeg."""
    assert detect_image_type(b"\xff\xd8\xff\xe0\x00\x10JFIF") == "image/jpeg"


def test_detect_image_type_png():
    """Los bytes 89 50 4E 47 corresponden a image/png."""
    assert detect_image_type(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR") == "image/png"


def test_detect_image_type_webp():
    """El header RIFF....WEBP corresponde a image/webp."""
    assert detect_image_type(b"RIFF\x1c\x00\x00\x00WEBPVP8 ") == "image/webp"


def test_detect_image_type_unknown_bytes_returns_none():
    """Bytes desconocidos (GIF, texto, vacío) devuelven None."""
    assert detect_image_type(b"GIF89a") is None
    assert detect_image_type(b"") is None
    assert detect_image_type(b"\x00\x01\x02\x03") is None


def test_detect_image_type_webp_requires_full_header():
    """Un RIFF sin el chunk WEBP no es webp."""
    assert detect_image_type(b"RIFF\x1c\x00\x00\x00AVI ") is None


# --- LocalImageStorage.validate ---

def test_validate_accepts_valid_image(tmp_path):
    """Un JPEG válido dentro del tamaño máximo pasa la validación."""
    storage = LocalImageStorage(base_dir=str(tmp_path))
    storage.validate(b"\xff\xd8\xff\xe0datos", "image/jpeg")


def test_validate_rejects_unsupported_content_type(tmp_path):
    """Un content-type fuera de la lista permitida se rechaza."""
    storage = LocalImageStorage(base_dir=str(tmp_path))
    with pytest.raises(UnsupportedImageTypeError):
        storage.validate(b"\x89PNG\r\n\x1a\n", "application/pdf")


def test_validate_rejects_mismatched_magic_bytes(tmp_path):
    """Content-type permitido pero magic bytes de otro formato se rechaza."""
    storage = LocalImageStorage(base_dir=str(tmp_path))
    with pytest.raises(UnsupportedImageTypeError):
        storage.validate(b"\x89PNG\r\n\x1a\n", "image/jpeg")


def test_validate_rejects_oversized_image(tmp_path):
    """Una imagen de más de 2MB se rechaza por tamaño."""
    storage = LocalImageStorage(base_dir=str(tmp_path))
    big = b"\xff\xd8\xff" + b"0" * (MAX_IMAGE_SIZE + 1)
    with pytest.raises(ImageTooLargeError):
        storage.validate(big, "image/jpeg")


# --- LocalImageStorage.save ---

def test_save_returns_public_url_and_writes_file(tmp_path):
    """save() genera una URL pública y persiste el archivo en la carpeta del producto."""
    storage = LocalImageStorage(base_dir=str(tmp_path))
    image_bytes = b"\xff\xd8\xff\xe0datos"
    url = storage.save(image_bytes, "image/jpeg", product_id=42)

    assert url.startswith("/static/uploads/42/")
    assert url.endswith(".jpg")
    rel = url.replace("/static/uploads/", "", 1)
    assert (tmp_path / rel).exists()
    assert (tmp_path / rel).read_bytes() == image_bytes


def test_save_png_and_webp_use_correct_extension(tmp_path):
    """La extensión se deriva del content-type validado."""
    storage = LocalImageStorage(base_dir=str(tmp_path))
    png_url = storage.save(b"\x89PNG\r\n\x1a\n", "image/png", product_id=1)
    webp_url = storage.save(b"RIFF\x1c\x00\x00\x00WEBPVP8 ", "image/webp", product_id=1)
    assert png_url.endswith(".png")
    assert webp_url.endswith(".webp")


def test_save_generates_unique_names(tmp_path):
    """Dos subidas del mismo archivo al mismo producto generan nombres distintos."""
    storage = LocalImageStorage(base_dir=str(tmp_path))
    image_bytes = b"RIFF\x1c\x00\x00\x00WEBPVP8 "
    url1 = storage.save(image_bytes, "image/webp", product_id=1)
    url2 = storage.save(image_bytes, "image/webp", product_id=1)
    assert url1 != url2


def test_save_rejects_invalid_image_without_writing(tmp_path):
    """Un archivo inválido no deja basura en el filesystem."""
    storage = LocalImageStorage(base_dir=str(tmp_path))
    with pytest.raises(UnsupportedImageTypeError):
        storage.save(b"no soy una imagen", "image/gif", product_id=1)
    assert list(tmp_path.iterdir()) == []


# --- LocalImageStorage.delete ---

def test_delete_removes_file(tmp_path):
    """delete() elimina el archivo correspondiente a la URL pública."""
    storage = LocalImageStorage(base_dir=str(tmp_path))
    url = storage.save(b"\x89PNG\r\n\x1a\n", "image/png", product_id=3)
    rel = url.replace("/static/uploads/", "", 1)
    assert (tmp_path / rel).exists()

    storage.delete(url)
    assert not (tmp_path / rel).exists()


def test_delete_nonexistent_url_does_not_raise(tmp_path):
    """delete() de una URL inexistente no explota (idempotente)."""
    storage = LocalImageStorage(base_dir=str(tmp_path))
    storage.delete("/static/uploads/999/no-existe.jpg")


def test_delete_guards_against_path_traversal(tmp_path):
    """Una URL con ../ no puede borrar archivos fuera de UPLOAD_DIR."""
    outside = tmp_path.parent / "archivo-secreto.txt"
    outside.write_text("secreto")

    storage = LocalImageStorage(base_dir=str(tmp_path))
    with pytest.raises(ValueError):
        storage.delete("/static/uploads/../../archivo-secreto.txt")
    assert outside.exists()