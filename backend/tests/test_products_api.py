"""Tests de API para el módulo de productos.

Sigue el mismo patrón que test_clients_api.py:
- Usa las fixtures compartidas de conftest.py
- Cada test arranca con BD limpia
- Los tests de API usan el TestClient de FastAPI
- Todos los endpoints exigen Bearer JWT (401 sin token)
"""
import pytest
from fastapi.testclient import TestClient
from src.models.product import Product
from src.database.session import get_db
from src.main import create_app
from src.core.config import MAX_IMAGE_SIZE


# ---------------------------------------------------------------------------
# Protección JWT
# ---------------------------------------------------------------------------

def test_list_products_without_token_returns_401(client):
    response = client.get("/api/v1/products/")
    assert response.status_code == 401


def test_create_product_without_token_returns_401(client):
    response = client.post("/api/v1/products/", json={"nombre": "X", "precio": 10, "stock": 1})
    assert response.status_code == 401


def test_create_product_happy_path(client, admin_headers_bearer):
    payload = {
        "nombre": "Producto Test",
        "descripcion": "Descripción del producto",
        "precio": 1500.50,
        "stock": 10,
        "categoria": "Limpieza",
    }
    response = client.post("/api/v1/products/", json=payload, headers=admin_headers_bearer)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Producto Test"
    assert data["precio"] == 1500.50
    assert data["stock"] == 10
    assert data["categoria"] == "Limpieza"
    assert data["activo"] is True
    assert "id" in data
    assert "fecha_registro" in data


def test_create_product_minimal(client, admin_headers_bearer):
    """Crear producto solo con campos obligatorios."""
    payload = {"nombre": "Mínimo", "precio": 0, "stock": 0}
    response = client.post("/api/v1/products/", json=payload, headers=admin_headers_bearer)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Mínimo"
    assert data["precio"] == 0
    assert data["stock"] == 0
    assert data["descripcion"] is None
    assert data["categoria"] is None


def test_create_product_missing_nombre_returns_422(client, admin_headers_bearer):
    payload = {"precio": 100, "stock": 5}
    response = client.post("/api/v1/products/", json=payload, headers=admin_headers_bearer)
    assert response.status_code == 422


def test_create_product_negative_price_returns_422(client, admin_headers_bearer):
    payload = {"nombre": "Test", "precio": -10, "stock": 5}
    response = client.post("/api/v1/products/", json=payload, headers=admin_headers_bearer)
    assert response.status_code == 422


def test_create_product_negative_stock_returns_422(client, admin_headers_bearer):
    payload = {"nombre": "Test", "precio": 100, "stock": -5}
    response = client.post("/api/v1/products/", json=payload, headers=admin_headers_bearer)
    assert response.status_code == 422


def test_list_products_empty(client, admin_headers_bearer):
    response = client.get("/api/v1/products/", headers=admin_headers_bearer)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_products_returns_active_only(client, db_session, admin_headers_bearer):
    """Crear un activo y un inactivo, listar solo activos."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    repo.create(Product(nombre="Activo", precio=10, stock=1))
    repo.create(Product(nombre="Inactivo", precio=20, stock=2, activo=False))

    response = client.get("/api/v1/products/", headers=admin_headers_bearer)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nombre"] == "Activo"


def test_list_products_pagination(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    for i in range(15):
        repo.create(Product(nombre=f"Producto {i}", precio=float(i), stock=i))

    response = client.get("/api/v1/products/?limit=5&offset=10", headers=admin_headers_bearer)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["total"] == 15


def test_list_products_search_by_name(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    repo.create(Product(nombre="Limpieza", precio=10, stock=5))
    repo.create(Product(nombre="Alimento", precio=20, stock=10))

    response = client.get("/api/v1/products/?q=Limpieza", headers=admin_headers_bearer)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nombre"] == "Limpieza"


def test_get_product_by_id(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Test", precio=100, stock=5))

    response = client.get(f"/api/v1/products/{p.id}", headers=admin_headers_bearer)
    assert response.status_code == 200
    assert response.json()["nombre"] == "Test"


def test_get_product_not_found_returns_404(client, admin_headers_bearer):
    response = client.get("/api/v1/products/9999", headers=admin_headers_bearer)
    assert response.status_code == 404


def test_get_inactive_product_returns_404(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Inactivo", precio=10, stock=1, activo=False))

    response = client.get(f"/api/v1/products/{p.id}", headers=admin_headers_bearer)
    assert response.status_code == 404


def test_update_product_partial(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Original", precio=100, stock=10))

    response = client.patch(f"/api/v1/products/{p.id}", json={"precio": 200, "stock": 5}, headers=admin_headers_bearer)
    assert response.status_code == 200
    data = response.json()
    assert data["precio"] == 200
    assert data["stock"] == 5
    assert data["nombre"] == "Original"  # unchanged


def test_update_product_all_fields(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Original", precio=100, stock=10))

    response = client.patch(f"/api/v1/products/{p.id}", json={
        "nombre": "Nuevo", "precio": 300, "stock": 20,
        "descripcion": "Nueva desc", "categoria": "Nueva",
    }, headers=admin_headers_bearer)
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Nuevo"
    assert data["precio"] == 300
    assert data["stock"] == 20
    assert data["descripcion"] == "Nueva desc"
    assert data["categoria"] == "Nueva"


def test_update_product_not_found_returns_404(client, admin_headers_bearer):
    response = client.patch("/api/v1/products/9999", json={"precio": 100}, headers=admin_headers_bearer)
    assert response.status_code == 404


def test_delete_product_returns_204(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Borrar", precio=10, stock=1))

    response = client.delete(f"/api/v1/products/{p.id}", headers=admin_headers_bearer)
    assert response.status_code == 204


def test_delete_product_not_found_returns_404(client, admin_headers_bearer):
    response = client.delete("/api/v1/products/9999", headers=admin_headers_bearer)
    assert response.status_code == 404


def test_delete_product_then_list_excluded(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Borrar", precio=10, stock=1))

    client.delete(f"/api/v1/products/{p.id}", headers=admin_headers_bearer)
    response = client.get("/api/v1/products/", headers=admin_headers_bearer)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


def test_list_inactive_after_delete(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Borrar", precio=10, stock=1))

    client.delete(f"/api/v1/products/{p.id}", headers=admin_headers_bearer)

    response = client.get("/api/v1/products/inactive", headers=admin_headers_bearer)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nombre"] == "Borrar"


def test_restore_product(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Restaurar", precio=10, stock=1, activo=False))

    response = client.patch(f"/api/v1/products/{p.id}/restore", headers=admin_headers_bearer)
    assert response.status_code == 200
    data = response.json()
    assert data["activo"] is True


def test_restore_already_active_returns_400(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Activo", precio=10, stock=1))

    response = client.patch(f"/api/v1/products/{p.id}/restore", headers=admin_headers_bearer)
    assert response.status_code == 400


def test_restore_not_found_returns_404(client, admin_headers_bearer):
    response = client.patch("/api/v1/products/9999/restore", headers=admin_headers_bearer)
    assert response.status_code == 404


def test_export_excel_returns_xlsx(client, db_session, admin_headers_bearer):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    repo.create(Product(nombre="Exportable", precio=100, stock=5))

    response = client.get("/api/v1/products/export", headers=admin_headers_bearer)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def test_export_excel_has_content_disposition(client, admin_headers_bearer):
    response = client.get("/api/v1/products/export", headers=admin_headers_bearer)
    assert response.status_code == 200
    assert "filename=productos.xlsx" in response.headers.get("content-disposition", "")


# --- Imágenes de producto ---

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"0" * 512
JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"0" * 512


@pytest.fixture
def image_client(db_session, tmp_path, monkeypatch, sample_admin):
    """TestClient con UPLOAD_DIR apuntando a un directorio temporal.

    Aísla los uploads del directorio real del proyecto: las imágenes se
    guardan en tmp_path y se sirven desde el mismo mount /static/uploads.
    """
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def image_headers(image_client, sample_admin):
    """Headers Bearer para los tests de imagen (mismo admin de db_session)."""
    from src.core.security import create_access_token
    return {"Authorization": f"Bearer {create_access_token(sample_admin.id)}"}


def test_upload_product_image_success(image_client, db_session, image_headers):
    """Subir un PNG válido devuelve el producto con image_url poblado."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Con imagen", precio=10, stock=1))

    response = image_client.post(
        f"/api/v1/products/{p.id}/image",
        files={"file": ("foto.png", PNG_BYTES, "image/png")},
        headers=image_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["image_url"].startswith(f"/static/uploads/{p.id}/")
    assert data["image_url"].endswith(".png")


def test_uploaded_image_is_served_as_static(image_client, db_session, image_headers):
    """GET a la URL pública devuelve la imagen con su content-type."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Servida", precio=10, stock=1))

    upload = image_client.post(
        f"/api/v1/products/{p.id}/image",
        files={"file": ("foto.png", PNG_BYTES, "image/png")},
        headers=image_headers,
    )
    url = upload.json()["image_url"]

    response = image_client.get(url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == PNG_BYTES


def test_static_missing_file_returns_404(image_client):
    """GET a una URL de imagen inexistente responde 404."""
    response = image_client.get("/static/uploads/999/no-existe.jpg")
    assert response.status_code == 404


def test_upload_invalid_content_type_returns_415(image_client, db_session, image_headers):
    """Un archivo que no es JPG/PNG/WebP responde 415 y no cambia image_url."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Rechazado", precio=10, stock=1))

    response = image_client.post(
        f"/api/v1/products/{p.id}/image",
        files={"file": ("nota.txt", b"hola mundo", "text/plain")},
        headers=image_headers,
    )
    assert response.status_code == 415
    assert repo.get_by_id(p.id).image_url is None


def test_upload_mismatched_magic_bytes_returns_415(image_client, db_session, image_headers):
    """Content-type permitido pero magic bytes de otro formato responde 415."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Falso png", precio=10, stock=1))

    response = image_client.post(
        f"/api/v1/products/{p.id}/image",
        files={"file": ("foto.gif", b"GIF89a........", "image/png")},
        headers=image_headers,
    )
    assert response.status_code == 415


def test_upload_oversized_image_returns_413(image_client, db_session, image_headers):
    """Una imagen de más de 2MB responde 413 y no cambia image_url."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Grande", precio=10, stock=1))
    big = b"\xff\xd8\xff" + b"0" * (MAX_IMAGE_SIZE + 1)

    response = image_client.post(
        f"/api/v1/products/{p.id}/image",
        files={"file": ("grande.jpg", big, "image/jpeg")},
        headers=image_headers,
    )
    assert response.status_code == 413
    assert repo.get_by_id(p.id).image_url is None


def test_upload_missing_product_returns_404(image_client, image_headers):
    """Subir a un producto inexistente responde 404."""
    response = image_client.post(
        "/api/v1/products/9999/image",
        files={"file": ("foto.png", PNG_BYTES, "image/png")},
        headers=image_headers,
    )
    assert response.status_code == 404


def test_upload_replaces_image_and_deletes_previous_file(image_client, db_session, tmp_path, image_headers):
    """Reemplazar la imagen apunta a la nueva y borra el archivo anterior del disco."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    old_folder = tmp_path / "1"
    old_folder.mkdir(exist_ok=True)
    (old_folder / "old.jpg").write_bytes(JPEG_BYTES)
    p = repo.create(Product(nombre="Reemplazo", precio=10, stock=1, image_url="/static/uploads/1/old.jpg"))

    response = image_client.post(
        f"/api/v1/products/{p.id}/image",
        files={"file": ("nueva.png", PNG_BYTES, "image/png")},
        headers=image_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["image_url"] != "/static/uploads/1/old.jpg"
    assert data["image_url"].endswith(".png")
    assert not (old_folder / "old.jpg").exists()


def test_delete_product_image(image_client, db_session, tmp_path, image_headers):
    """Quitar la imagen borra el archivo y setea image_url en null."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    folder = tmp_path / "1"
    folder.mkdir(exist_ok=True)
    (folder / "img.jpg").write_bytes(JPEG_BYTES)
    p = repo.create(Product(nombre="Con imagen", precio=10, stock=1, image_url="/static/uploads/1/img.jpg"))

    response = image_client.delete(f"/api/v1/products/{p.id}/image", headers=image_headers)
    assert response.status_code == 200
    assert response.json()["image_url"] is None
    assert not (folder / "img.jpg").exists()


def test_delete_product_image_without_image_is_idempotent(image_client, db_session, image_headers):
    """Quitar imagen de un producto sin imagen responde 200 con image_url null."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Sin imagen", precio=10, stock=1))

    response = image_client.delete(f"/api/v1/products/{p.id}/image", headers=image_headers)
    assert response.status_code == 200
    assert response.json()["image_url"] is None


def test_delete_product_image_missing_product_returns_404(image_client, image_headers):
    """Quitar imagen de un producto inexistente responde 404."""
    response = image_client.delete("/api/v1/products/9999/image", headers=image_headers)
    assert response.status_code == 404


def test_soft_delete_conserva_la_imagen(image_client, db_session, image_headers):
    """Soft-delete conserva el archivo e image_url; al restaurar sigue expuesta."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Soft", precio=10, stock=1, image_url="/static/uploads/1/img.jpg"))

    image_client.delete(f"/api/v1/products/{p.id}", headers=image_headers)
    assert repo.get_by_id(p.id).image_url == "/static/uploads/1/img.jpg"

    response = image_client.patch(f"/api/v1/products/{p.id}/restore", headers=image_headers)
    assert response.status_code == 200
    assert response.json()["image_url"] == "/static/uploads/1/img.jpg"


def test_update_product_partial_keeps_image(image_client, db_session, image_headers):
    """Un update parcial que no toca image_url la conserva intacta."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Original", precio=100, stock=10, image_url="/static/uploads/1/img.jpg"))

    response = image_client.patch(f"/api/v1/products/{p.id}", json={"precio": 200}, headers=image_headers)
    assert response.status_code == 200
    assert response.json()["image_url"] == "/static/uploads/1/img.jpg"