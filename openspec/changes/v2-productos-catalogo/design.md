## Context

El sistema actual maneja clientes (CRUD completo con soft-delete) e interacciones de Telegram. El bot de Telegram tiene opciones de menú para "Ver catálogo" y "Consultar precios" que responden con mensajes genéricos. No existe un modelo de datos para productos. Se necesita agregar un módulo de catálogo de productos que permita:

- Gestión completa de productos desde la API
- Stock y precios actualizados
- Consulta desde n8n para respuestas dinámicas en Telegram
- Posible integración futura con el frontend React

## Goals / Non-Goals

**Goals:**
- Modelo Product con nombre, descripción, precio, stock, categoría, soft-delete
- CRUD completo via REST: crear, listar, obtener, editar, eliminar, restaurar, exportar
- Validaciones: nombre obligatorio, precio positivo, stock >= 0, email único (ya no aplica — no hay email en producto)
- Tests siguiendo la misma arquitectura hexagonal que Clients (repository → service → API)
- Actualización del flujo n8n: Bot Router consulta productos reales para opciones 2 y 3

**Non-Goals:**
- No se agrega integración con frontend React en este cambio (se puede hacer después)
- No se agregan imágenes de productos
- No hay variantes/talles/colores — stock es un entero único por producto
- No hay carrito de compras ni checkout — solo consulta de catálogo

## Decisions

### 1. Modelo Product — mismo patrón que Client

- `id`: Integer PK, autoincrement
- `nombre`: String(200), NOT NULL (producto siempre tiene nombre)
- `descripcion`: Text, nullable
- `precio`: Float, NOT NULL, default 0.0
- `stock`: Integer, NOT NULL, default 0
- `categoria`: String(100), nullable (texto libre)
- `activo`: Boolean, default true (soft-delete)
- `fecha_registro`: DateTime, server_default=func.now()
- `updated_at`: DateTime, onupdate=func.now()

**Alternativa considerada**: Tabla separada de categorías. Se descarta por ahora porque agrega complejidad innecesaria — una categoría como string alcanza para el filtrado básico.

### 2. Endpoints — mismo patrón que /api/v1/clients/

```
POST   /api/v1/products/          → crear
GET    /api/v1/products/          → listar activos (q, limit, offset)
GET    /api/v1/products/{id}      → obtener por ID
PATCH  /api/v1/products/{id}      → actualizar parcial
DELETE /api/v1/products/{id}      → soft-delete (activo=false)
GET    /api/v1/products/inactive  → listar inactivos
PATCH  /api/v1/products/{id}/restore → restaurar
GET    /api/v1/products/export    → exportar a Excel .xlsx
```

**Alternativa considerada**: Endpoints anidados (`/api/v1/clients/{id}/products/`). Se descarta porque los productos son independientes de los clientes.

### 3. Sin autenticación por ahora

Los endpoints de products NO requieren `X-Api-Key` por ahora, consistente con la mayoría de los endpoints de clients. Si se necesita protección después, se agrega.

### 4. n8n: dos nodos nuevos

- Se agrega un nodo HTTP Request `GET /api/v1/products/` antes del Bot Router
- Bot Router se modifica para, en opciones 2 (Ver catálogo) y 3 (Consultar precios), formatear y devolver los productos
- Si no hay productos o la API falla, muestra mensaje amigable

**Alternativa considerada**: Bot Router hace la llamada HTTP internamente. No es posible — es un Function node, no puede hacer HTTP calls. Se necesita un nodo separado.

### 5. Tests — tres capas

Siguiendo exactamente el mismo patrón de Clients:
- `test_product_repository.py`: CRUD, soft-delete, paginación, búsqueda
- `test_product_service.py`: validaciones de negocio
- `test_products_api.py`: endpoints via TestClient

## Risks / Trade-offs

- **[Riesgo] Migración de DB nueva**: Product es una tabla nueva, corre `alembic upgrade head` y se crea. Sin riesgo de datos existentes.
- **[Trade-off] Stock como entero único**: No soporta variantes (talles, colores). Si se necesita después, habría que migrar a una tabla product_variants. Por ahora alcanza.
- **[Trade-off] Categoría como string libre**: Puede llevar a inconsistencia (ej: "Limpieza" vs "limpieza"). Si crece, migrar a tabla de categorías con FK.
- **[Riesgo] n8n GET products sincrónico**: Si la API está caída, el flujo se traba. Se agrega `continueOnFail: true` y mensaje de fallback.
