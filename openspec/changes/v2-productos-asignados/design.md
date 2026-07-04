## Context

Actualmente los clientes tienen una tabla SQL con datos personales y los productos tienen su propia tabla. No existe relación entre ambas. Desde Telegram los clientes pueden ver el catálogo de productos pero no pueden "seleccionar" productos ni tener una lista personal.

Se necesita una asociación liviana (carrito simple) donde cada cliente tenga una lista de productos con cantidades. La solución debe ser simple: sin tabla intermedia, sin módulo de ventas, sin historial de compras.

## Goals / Non-Goals

**Goals:**
- Agregar columna JSON `productos_asignados` a la tabla `clients`
- Proveer endpoints REST para CRUD de productos asignados por cliente
- Mostrar productos asignados en el modal de detalle del cliente (frontend)
- Permitir agregar/quitar productos desde el frontend
- Conectar el bot de Telegram para guardar productos seleccionados

**Non-Goals:**
- No se crea módulo de ventas/pedidos
- No hay historial de compras
- No hay tabla intermedia `client_products`
- No hay carrito con checkout ni pagos
- No se registran transacciones ni facturas

## Decisions

### 1. JSON column vs tabla intermedia
**Decisión**: Columna JSON directamente en `clients`.
- **Pros**: Migración simple, sin joins, fácil de leer/escribir desde n8n, el bot Telegram puede mandar el JSON directo
- **Contras**: No permite consultas SQL sobre productos asignados, no hay integridad referencial
- **Alternativa**: Tabla `client_products` con FK — más normalizado pero sobreingeniería para el alcance "carrito simple"

### 2. Endpoints REST vs update genérico de client
**Decisión**: Endpoints dedicados `/api/v1/clients/{id}/productos`.
- **Pros**: Semántica clara, validación específica, independiente del update general de cliente
- **Contras**: Un par de endpoints más

### 3. Al agregar producto existente → incrementar cantidad
**Decisión**: Si el `producto_id` ya existe en la lista, se incrementa `cantidad` en vez de duplicar.
- **Razón**: Comportamiento natural de carrito

### 4. Reemplazo total vía PUT
**Decisión**: PUT reemplaza TODO el array para que n8n pueda sincronizar el estado completo sin lógica diff.
- **POST**: Agrega un producto (o incrementa cantidad si ya existe)
- **DELETE**: Quita un producto específico
- **PUT**: Reemplaza toda la lista

## Risks / Trade-offs

- **Sin integridad referencial**: Si se elimina un producto del catálogo, los productos asignados a clientes pueden quedar huérfanos. Mitigación: El frontend muestra el nombre/precio guardados en el JSON al momento de asignación (no hace falta que el producto siga existiendo)
- **JSON column no es consultable vía SQL**: No se puede hacer "qué clientes tienen el producto X". Mitigación: Si se necesita en el futuro, se migra a tabla intermedia
- **Tamaño de fila crece**: Clientes con muchos productos pueden tener filas grandes. Riesgo bajo para el uso esperado
