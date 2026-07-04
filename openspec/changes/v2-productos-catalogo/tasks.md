# Tasks: v2-productos-catalogo

## 1. Modelo y migración

- [x] 1.1 Crear `backend/src/models/product.py` — modelo SQLAlchemy con campos: id, nombre, descripcion, precio, stock, categoria, activo, fecha_registro, updated_at
- [x] 1.2 Crear migración Alembic para la tabla `products`
- [x] 1.3 Ejecutar `alembic upgrade head` y verificar que la tabla se crea

## 2. Schemas Pydantic

- [x] 2.1 Crear `backend/src/schemas/product.py` con CreateProduct, UpdateProduct, ProductResponse

## 3. Repositorio

- [x] 3.1 Crear `backend/src/repositories/product_repo.py` — CRUD, soft-delete, paginación, búsqueda por nombre/categoria
- [x] 3.2 Tests: `backend/tests/test_product_repository.py` (8 tests: crear, listar, search, soft-delete, inactive, restore, update)

## 4. Servicio

- [x] 4.1 Crear `backend/src/services/product_service.py` — validaciones de negocio (precio positivo, stock >= 0, nombre obligatorio)
- [x] 4.2 Tests: `backend/tests/test_product_service.py` (7 tests: creación, update, delete, search)

## 5. API REST

- [x] 5.1 Crear `backend/src/api/routes/products.py` — router con endpoints: POST, GET list, GET by id, PATCH, DELETE, GET inactive, PATCH restore, GET export
- [x] 5.2 Registrar el router en `backend/src/main.py`
- [x] 5.3 Tests: `backend/tests/test_products_api.py` (24 tests: CRUD completo, validaciones, exportación, 404s)

## 6. Actualización flujo n8n

- [x] 6.1 Agregar nodo HTTP Request `GET /api/v1/products/` conectado en serie con Combine Products
- [x] 6.2 Modificar Bot Router: opción 2 (Ver catálogo) muestra productos con nombre, precio y stock
- [x] 6.3 Modificar Bot Router: opción 3 (Consultar precios) muestra nombres y precios
- [x] 6.4 Manejar caso sin productos: mensaje "No hay productos disponibles"
- [x] 6.5 Manejar error de API: mensaje "No pude consultar los productos. Intentalo de nuevo más tarde."
- [x] 6.6 Agregar `continueOnFail: true` al nodo GET products

## 7. Frontend React — sección productos

- [x] 7.1 Crear `frontend/src/services/productService.js` — CRUD + export (mismo patrón que clientService)
- [x] 7.2 Crear `frontend/src/hooks/useProducts.js` — hook con list, create, update, delete, search
- [x] 7.3 Crear `frontend/src/pages/ProductsPage.jsx` — página completa con tabla, modales, estados
- [x] 7.4 Crear `frontend/src/components/ProductTable.jsx` — tabla con precio, stock, categoría, acciones
- [x] 7.5 Crear `frontend/src/components/ProductFormModal.jsx` — modal crear/editar con validaciones
- [x] 7.6 Crear `frontend/src/components/DeleteProductModal.jsx` — confirmación de eliminación
- [x] 7.7 Crear `frontend/src/components/ProductDetailsModal.jsx` — detalle del producto
- [x] 7.8 Crear `frontend/src/components/ProductFilters.jsx` — buscador por nombre/categoría
- [x] 7.9 Modificar `frontend/src/components/Topbar.jsx` — soporte para onNewProduct y onExport custom
- [x] 7.10 Modificar `frontend/src/components/Sidebar.jsx` — agregar item "Productos" con icono Package
- [x] 7.11 Modificar `frontend/src/App.jsx` — agregar ruta /products → ProductsPage

## 8. Verificación final

- [x] 8.1 Correr todos los tests: 108/108 PASSED (69 existentes + 39 nuevos de productos)
- [ ] 8.2 Probar endpoints via Swagger en `/docs`
- [ ] 8.3 Probar frontend: levantar back + front, crear/editar/eliminar productos
- [ ] 8.4 Probar flujo completo en Telegram: crear producto → consultar en bot
