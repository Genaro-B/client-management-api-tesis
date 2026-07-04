## Why

El bot de Telegram tiene opciones como "Ver catálogo", "Consultar precios" y "Comprar productos" que hoy responden con mensajes genéricos. No hay una base de datos de productos que permita consultar stock, precios reales, o hacer catálogo dinámico. Agregar un módulo de productos permite que el bot responda con información real y actualizada, y le da al admin un panel completo para gestionar el inventario desde la API.

## What Changes

- **Nuevo modelo Product**: nombre, descripción, precio, stock, categoría, activo, timestamps
- **Nuevos endpoints CRUD** bajo `/api/v1/products/`: crear, listar, obtener, editar, eliminar (soft-delete), restaurar, exportar
- **Nuevos tests**: repository, service, API (siguiendo el patrón de clients)
- **Actualización del flujo n8n**: el Bot Router ahora consulta `GET /api/v1/products/` para mostrar catálogo y precios reales cuando el usuario selecciona opciones 2 (Ver catálogo) y 3 (Consultar precios)
- **Actualización del Frontend React** (si aplica): sección de productos en el panel admin

## Capabilities

### New Capabilities
- `product-catalog`: CRUD completo de productos con stock, categorización, soft-delete, y exportación. Incluye endpoints REST, validaciones, y tests.

### Modified Capabilities
- *(ninguna — es funcionalidad nueva, no modifico specs existentes)*

## Impact

- `backend/src/models/product.py` — nuevo modelo SQLAlchemy
- `backend/src/schemas/product.py` — nuevos schemas Pydantic
- `backend/src/repositories/product_repository.py` — nuevo repositorio
- `backend/src/services/product_service.py` — nuevo servicio con validaciones
- `backend/src/api/routes/products.py` — nuevo router con endpoints
- `backend/src/main.py` — registrar router
- `backend/alembic/versions/` — nueva migración
- `backend/tests/test_product_repository.py` — tests de repo
- `backend/tests/test_product_service.py` — tests de servicio
- `backend/tests/test_products_api.py` — tests de API
- `Docs/flujos/Actual/v2-flujo-mejorado.json` — actualizar Bot Router + agregar nodo GET products
