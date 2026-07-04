## Why

Los clientes pueden seleccionar productos desde el catálogo de Telegram y acumularlos en una lista personal (carrito simple). Actualmente no existe forma de asociar productos a un cliente, lo que limita el flujo del bot: el cliente ve el catálogo pero no puede "llevarse" productos. Con este cambio cada cliente tendrá una lista de productos asignados, visible desde el frontend y modificable desde Telegram y la web.

## What Changes

- Agregar columna `productos_asignados` (JSON) a la tabla `clients` para almacenar los productos que cada cliente tiene asignados con cantidad
- Crear endpoints REST para gestionar productos asignados desde el frontend y el bot
- Mostrar los productos asignados en el detalle del cliente en el frontend React
- Permitir agregar/quitar productos desde el frontend
- Conectar el bot de Telegram para que guarde los productos seleccionados por el cliente en su perfil

## Capabilities

### New Capabilities
- `productos-asignados`: Gestión de productos asignados a clientes — alta, baja, modificación de cantidades, consulta

### Modified Capabilities
- `clientes`: el response del cliente incluye `productos_asignados`; el detalle en frontend muestra la lista

## Impact

- **Backend**: migración Alembic a `clients` (+1 columna JSON), nuevos endpoints REST
- **Schemas**: nuevo schema `ProductoAsignado`, actualización de `ClientResponse`
- **Repositorio**: extensión con métodos para productos asignados
- **Frontend**: ClientDetailsModal extendido con tabla de productos + botón agregar
- **n8n**: Bot Router modificado para guardar productos asignados via PATCH
- **Tests**: nuevos tests para endpoints y lógica de productos asignados
