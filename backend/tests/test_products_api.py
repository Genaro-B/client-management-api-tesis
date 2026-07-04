"""Tests de API para el módulo de productos.

Sigue el mismo patrón que test_clients_api.py:
- Usa las fixtures compartidas de conftest.py
- Cada test arranca con BD limpia
- Los tests de API usan el TestClient de FastAPI
"""
import pytest
from fastapi.testclient import TestClient
from src.models.product import Product


def test_create_product_happy_path(client):
    payload = {
        "nombre": "Producto Test",
        "descripcion": "Descripción del producto",
        "precio": 1500.50,
        "stock": 10,
        "categoria": "Limpieza",
    }
    response = client.post("/api/v1/products/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Producto Test"
    assert data["precio"] == 1500.50
    assert data["stock"] == 10
    assert data["categoria"] == "Limpieza"
    assert data["activo"] is True
    assert "id" in data
    assert "fecha_registro" in data


def test_create_product_minimal(client):
    """Crear producto solo con campos obligatorios."""
    payload = {"nombre": "Mínimo", "precio": 0, "stock": 0}
    response = client.post("/api/v1/products/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Mínimo"
    assert data["precio"] == 0
    assert data["stock"] == 0
    assert data["descripcion"] is None
    assert data["categoria"] is None


def test_create_product_missing_nombre_returns_422(client):
    payload = {"precio": 100, "stock": 5}
    response = client.post("/api/v1/products/", json=payload)
    assert response.status_code == 422


def test_create_product_negative_price_returns_422(client):
    payload = {"nombre": "Test", "precio": -10, "stock": 5}
    response = client.post("/api/v1/products/", json=payload)
    assert response.status_code == 422


def test_create_product_negative_stock_returns_422(client):
    payload = {"nombre": "Test", "precio": 100, "stock": -5}
    response = client.post("/api/v1/products/", json=payload)
    assert response.status_code == 422


def test_list_products_empty(client):
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_products_returns_active_only(client, db_session):
    """Crear un activo y un inactivo, listar solo activos."""
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    repo.create(Product(nombre="Activo", precio=10, stock=1))
    repo.create(Product(nombre="Inactivo", precio=20, stock=2, activo=False))

    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nombre"] == "Activo"


def test_list_products_pagination(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    for i in range(15):
        repo.create(Product(nombre=f"Producto {i}", precio=float(i), stock=i))

    response = client.get("/api/v1/products/?limit=5&offset=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["total"] == 15


def test_list_products_search_by_name(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    repo.create(Product(nombre="Limpieza", precio=10, stock=5))
    repo.create(Product(nombre="Alimento", precio=20, stock=10))

    response = client.get("/api/v1/products/?q=Limpieza")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nombre"] == "Limpieza"


def test_get_product_by_id(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Test", precio=100, stock=5))

    response = client.get(f"/api/v1/products/{p.id}")
    assert response.status_code == 200
    assert response.json()["nombre"] == "Test"


def test_get_product_not_found_returns_404(client):
    response = client.get("/api/v1/products/9999")
    assert response.status_code == 404


def test_get_inactive_product_returns_404(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Inactivo", precio=10, stock=1, activo=False))

    response = client.get(f"/api/v1/products/{p.id}")
    assert response.status_code == 404


def test_update_product_partial(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Original", precio=100, stock=10))

    response = client.patch(f"/api/v1/products/{p.id}", json={"precio": 200, "stock": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["precio"] == 200
    assert data["stock"] == 5
    assert data["nombre"] == "Original"  # unchanged


def test_update_product_all_fields(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Original", precio=100, stock=10))

    response = client.patch(f"/api/v1/products/{p.id}", json={
        "nombre": "Nuevo", "precio": 300, "stock": 20,
        "descripcion": "Nueva desc", "categoria": "Nueva",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Nuevo"
    assert data["precio"] == 300
    assert data["stock"] == 20
    assert data["descripcion"] == "Nueva desc"
    assert data["categoria"] == "Nueva"


def test_update_product_not_found_returns_404(client):
    response = client.patch("/api/v1/products/9999", json={"precio": 100})
    assert response.status_code == 404


def test_delete_product_returns_204(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Borrar", precio=10, stock=1))

    response = client.delete(f"/api/v1/products/{p.id}")
    assert response.status_code == 204


def test_delete_product_not_found_returns_404(client):
    response = client.delete("/api/v1/products/9999")
    assert response.status_code == 404


def test_delete_product_then_list_excluded(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Borrar", precio=10, stock=1))

    client.delete(f"/api/v1/products/{p.id}")
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


def test_list_inactive_after_delete(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Borrar", precio=10, stock=1))

    client.delete(f"/api/v1/products/{p.id}")

    response = client.get("/api/v1/products/inactive")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["nombre"] == "Borrar"


def test_restore_product(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Restaurar", precio=10, stock=1, activo=False))

    response = client.patch(f"/api/v1/products/{p.id}/restore")
    assert response.status_code == 200
    data = response.json()
    assert data["activo"] is True


def test_restore_already_active_returns_400(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    p = repo.create(Product(nombre="Activo", precio=10, stock=1))

    response = client.patch(f"/api/v1/products/{p.id}/restore")
    assert response.status_code == 400


def test_restore_not_found_returns_404(client):
    response = client.patch("/api/v1/products/9999/restore")
    assert response.status_code == 404


def test_export_excel_returns_xlsx(client, db_session):
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    repo.create(Product(nombre="Exportable", precio=100, stock=5))

    response = client.get("/api/v1/products/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def test_export_excel_has_content_disposition(client):
    response = client.get("/api/v1/products/export")
    assert response.status_code == 200
    assert "filename=productos.xlsx" in response.headers.get("content-disposition", "")
