"""Tests de API para productos asignados a clientes (/api/v1/clients/{id}/productos).

Sigue el mismo patrón que test_clients_api.py:
- Usa las fixtures compartidas de conftest.py
- Cada test arranca con BD limpia
- Los tests de API usan el TestClient de FastAPI
"""
import pytest

PREFIX = "/api/v1/clients"


def _payload(producto_id=1, nombre="Producto Test", precio=1500.50, cantidad=2):
    return {
        "producto_id": producto_id,
        "nombre": nombre,
        "precio": precio,
        "cantidad": cantidad,
    }


# ---------------------------------------------------------------------------
# GET /{client_id}/productos — Lista vacía
# ---------------------------------------------------------------------------


def test_get_productos_empty(client, sample_client):
    """Un cliente nuevo debe tener lista vacía de productos."""
    resp = client.get(f"{PREFIX}/{sample_client.id}/productos")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_productos_client_not_found_returns_404(client):
    """Cliente inexistente debe devolver 404."""
    resp = client.get(f"{PREFIX}/99999/productos")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /{client_id}/productos — Agregar producto
# ---------------------------------------------------------------------------


def test_add_producto_happy_path(client, sample_client, sample_product):
    """Agregar un producto a un cliente."""
    resp = client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=sample_product.id),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 1
    assert data[0]["producto_id"] == sample_product.id
    assert data[0]["nombre"] == "Producto Test"
    assert data[0]["precio"] == 1500.50
    assert data[0]["cantidad"] == 2


def test_add_producto_increment_quantity(client, sample_client, sample_product):
    """Agregar el mismo producto dos veces incrementa la cantidad."""
    pid = sample_product.id
    client.post(f"{PREFIX}/{sample_client.id}/productos", json=_payload(producto_id=pid))
    resp = client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=pid),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 1
    assert data[0]["cantidad"] == 4  # 2 + 2


def test_add_producto_multiple_different(client, sample_client, sample_product, sample_product2):
    """Agregar productos distintos crea entradas separadas."""
    client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=sample_product.id),
    )
    resp = client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(
            producto_id=sample_product2.id,
            nombre="Otro Producto",
            precio=500.00,
            cantidad=1,
        ),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 2
    ids = {p["producto_id"] for p in data}
    assert ids == {sample_product.id, sample_product2.id}


def test_add_producto_client_not_found_returns_404(client):
    """Agregar producto a cliente inexistente devuelve 404."""
    resp = client.post(
        f"{PREFIX}/99999/productos",
        json=_payload(),
    )
    assert resp.status_code == 404


def test_add_producto_cantidad_zero_returns_422(client, sample_client):
    """Cantidad debe ser >= 1."""
    payload = _payload(cantidad=0)
    resp = client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=payload,
    )
    assert resp.status_code == 422


def test_add_producto_producto_id_zero_returns_422(client, sample_client):
    """producto_id debe ser >= 1."""
    payload = _payload(producto_id=0)
    resp = client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=payload,
    )
    assert resp.status_code == 422


def test_add_producto_precio_negativo_returns_422(client, sample_client):
    """precio debe ser >= 0."""
    payload = _payload(precio=-10)
    resp = client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=payload,
    )
    assert resp.status_code == 422


def test_add_producto_insufficient_stock(client, sample_client, sample_product_sin_stock):
    """Producto sin stock debe devolver error 400."""
    resp = client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=sample_product_sin_stock.id),
    )
    assert resp.status_code == 400
    assert "Stock insuficiente" in resp.json()["detail"]


def test_add_producto_not_found_returns_400(client, sample_client):
    """producto_id que no existe en la DB debe devolver 400."""
    resp = client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=9999),
    )
    assert resp.status_code == 400
    assert "Producto no encontrado" in resp.json()["detail"]


def test_add_producto_stock_decrements(client, sample_client, sample_product, db_session):
    """Al agregar un producto al cliente, se descuenta del stock."""
    pid = sample_product.id
    stock_inicial = sample_product.stock  # 10

    client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=pid, cantidad=2),
    )

    # Verificar stock decrementado
    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    product = repo.get_by_id(pid)
    assert product.stock == stock_inicial - 2


# ---------------------------------------------------------------------------
# PUT /{client_id}/productos — Reemplazar toda la lista
# ---------------------------------------------------------------------------


def test_set_productos_replace_all(client, sample_client, sample_product):
    """PUT reemplaza toda la lista de productos."""
    client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=sample_product.id),
    )

    nuevos = [
        {"producto_id": 10, "nombre": "Nuevo A", "precio": 100, "cantidad": 1},
        {"producto_id": 20, "nombre": "Nuevo B", "precio": 200, "cantidad": 3},
    ]
    resp = client.put(
        f"{PREFIX}/{sample_client.id}/productos",
        json=nuevos,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["producto_id"] == 10
    assert data[1]["producto_id"] == 20


def test_set_productos_empty_list(client, sample_client, sample_product):
    """PUT con lista vacía limpia los productos."""
    client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=sample_product.id),
    )
    resp = client.put(
        f"{PREFIX}/{sample_client.id}/productos",
        json=[],
    )
    assert resp.status_code == 200
    assert resp.json() == []


def test_set_productos_client_not_found_returns_404(client):
    """PUT en cliente inexistente devuelve 404."""
    resp = client.put(
        f"{PREFIX}/99999/productos",
        json=[{"producto_id": 1, "nombre": "X", "precio": 10, "cantidad": 1}],
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /{client_id}/productos/{producto_id} — Eliminar producto
# ---------------------------------------------------------------------------


def test_remove_producto_happy_path(client, sample_client, sample_product, sample_product2):
    """Eliminar un producto existente de la lista."""
    p1, p2 = sample_product.id, sample_product2.id
    client.post(f"{PREFIX}/{sample_client.id}/productos", json=_payload(producto_id=p1))
    client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=p2, nombre="Otro", precio=500, cantidad=1),
    )

    resp = client.delete(f"{PREFIX}/{sample_client.id}/productos/{p1}")
    assert resp.status_code == 204

    get_resp = client.get(f"{PREFIX}/{sample_client.id}/productos")
    assert len(get_resp.json()) == 1
    assert get_resp.json()[0]["producto_id"] == p2


def test_remove_producto_restores_stock(client, sample_client, sample_product, db_session):
    """Al eliminar un producto, se restaura el stock."""
    pid = sample_product.id
    stock_inicial = sample_product.stock  # 10

    client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=pid, cantidad=3),
    )
    client.delete(f"{PREFIX}/{sample_client.id}/productos/{pid}")

    from src.repositories.product_repo import ProductRepository
    repo = ProductRepository(db_session)
    product = repo.get_by_id(pid)
    assert product.stock == stock_inicial  # Vuelve a 10


def test_remove_producto_client_not_found_returns_404(client):
    """Eliminar producto de cliente inexistente devuelve 404."""
    resp = client.delete(f"{PREFIX}/99999/productos/1")
    assert resp.status_code == 404


def test_remove_producto_not_in_list_returns_404(client, sample_client, sample_product):
    """Eliminar un producto_id que no está en la lista devuelve 404."""
    client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=sample_product.id),
    )
    resp = client.delete(f"{PREFIX}/{sample_client.id}/productos/999")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET después de operaciones — Verificar estado consistente
# ---------------------------------------------------------------------------


def test_get_productos_after_operations(client, sample_client, sample_product, sample_product2):
    """GET después de POST, PUT y DELETE muestra estado correcto."""
    p1, p2 = sample_product.id, sample_product2.id
    client.post(f"{PREFIX}/{sample_client.id}/productos", json=_payload(producto_id=p1))
    client.post(
        f"{PREFIX}/{sample_client.id}/productos",
        json=_payload(producto_id=p2, nombre="Otro", precio=500, cantidad=1),
    )
    assert len(client.get(f"{PREFIX}/{sample_client.id}/productos").json()) == 2

    client.delete(f"{PREFIX}/{sample_client.id}/productos/{p1}")
    assert len(client.get(f"{PREFIX}/{sample_client.id}/productos").json()) == 1

    client.put(
        f"{PREFIX}/{sample_client.id}/productos",
        json=[{"producto_id": 99, "nombre": "Final", "precio": 999, "cantidad": 1}],
    )
    data = client.get(f"{PREFIX}/{sample_client.id}/productos").json()
    assert len(data) == 1
    assert data[0]["producto_id"] == 99
