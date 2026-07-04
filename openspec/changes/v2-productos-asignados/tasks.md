## 1. Migración — columna productos_asignados

- [x] 1.1 Crear migración Alembic que agregue columna `productos_asignados` (JSON, default `[]`) a la tabla `clients`
- [x] 1.2 Ejecutar `alembic upgrade head` y verificar

## 2. Backend — modelo y schemas

- [x] 2.1 Actualizar `backend/src/models/client.py` — agregar campo `productos_asignados = Column(JSON, default=[])`
- [x] 2.2 Crear schema `ProductoAsignado` (producto_id: int, nombre: str, precio: float, cantidad: int >= 1) en `schemas/client.py`
- [x] 2.3 Actualizar `ClientResponse` para incluir `productos_asignados: list[ProductoAsignado] = []`

## 3. Backend — repositorio y servicio

- [x] 3.1 Agregar métodos a `ClientRepository`: `get_productos(client)`, `set_productos(client, productos)`, `add_producto(client, producto)`, `remove_producto(client, producto_id)`
- [x] 3.2 Agregar validaciones en `ClientService` para productos asignados (cantidad >= 1, producto_id positivo)

## 4. Backend — API REST

- [x] 4.1 Agregar endpoint `GET /api/v1/clients/{id}/productos` — obtener productos asignados
- [x] 4.2 Agregar endpoint `POST /api/v1/clients/{id}/productos` — agregar producto (o incrementar cantidad si ya existe)
- [x] 4.3 Agregar endpoint `PUT /api/v1/clients/{id}/productos` — reemplazar toda la lista
- [x] 4.4 Agregar endpoint `DELETE /api/v1/clients/{id}/productos/{producto_id}` — quitar producto
- [x] 4.5 Tests: crear `backend/tests/test_client_productos_api.py` con tests para los 4 endpoints

## 5. Frontend — service y hook

- [x] 5.1 Agregar funciones a `frontend/src/services/clientService.js`: `getClientProductos`, `addClientProducto`, `setClientProductos`, `removeClientProducto`
- [x] 5.2 Agregar funciones al hook `useClients` para gestión de productos asignados

## 6. Frontend — modal de detalle con productos

- [x] 6.1 Extender `ClientDetailsModal.jsx` — agregar sección "Productos Asignados" con tabla de productos (nombre, precio unitario, cantidad, subtotal)
- [x] 6.2 Agregar botón "Agregar Producto" que abre selector de productos del catálogo
- [x] 6.3 Agregar botón "Quitar" por cada producto en la tabla
- [x] 6.4 Agregar botón para modificar cantidad de cada producto

## 7. n8n — conectar selección de productos

- [x] 7.1 Modificar Bot Router: agregar opciones 6 (Ver carrito) y 7 (Finalizar compra)
- [x] 7.2 Agregar nodo GET Carrito, Switch Router, Add to Carrito (POST), Clear Carrito (PUT) al flujo n8n
- [x] 7.3 Catálogo numerado: cada producto con número para seleccionar y agregar al carrito
- [x] 7.4 "Finalizar compra" vacía el carrito vía PUT /api/v1/clients/{id}/productos con []

## 8. Verificación final

- [x] 8.1 Correr todos los tests (nuevos + existentes)
- [x] 8.2 Probar endpoints via Swagger
- [x] 8.3 Probar frontend: ver detalle de cliente con productos asignados
