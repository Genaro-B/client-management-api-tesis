## Why

El dueño del negocio toma decisiones mirando datos que hoy están dispersos en distintas pantallas y tablas que se vuelven largas. Necesita poder descargar las listas, navegarlas cómodamente, ver el historial completo de cada cliente y —sobre todo— una forma rápida de preguntar en lenguaje natural "¿cómo va el negocio?" sin entrar pantalla por pantalla. Este cambio agrega esas mejoras de usabilidad y, como pieza central, un asistente administrativo que responde con datos REALES usando la misma técnica de interpretación determinística de intenciones de la tesis (patrones de texto → intención → acción).

## What Changes

- **Exportar a Excel (verificación y cierre):** los endpoints de exportación (`/api/v1/clients/export` y `/api/v1/products/export`) y el botón "Exportar Excel" en la barra superior YA EXISTEN, y `openpyxl` ya está en los requerimientos del backend. La tarea es verificar que funcionen en las pantallas de Clientes y Productos, y agregar el toast de confirmación al descargar el archivo.
- **Toasts de confirmación (verificación y cierre):** las notificaciones toast YA EXISTEN para crear, editar y eliminar clientes y productos (librería `sonner`, montada en la app). La tarea es revisar que no falte ningún caso (exportación, clientes inactivos, productos asignados) y completar los huecos.
- **Paginación de tablas (NUEVO):** las tablas de Clientes y Productos mostrarán 20 registros por página con controles "← 1 2 3 →". El backend ya soporta `limit`/`offset`; el frontend todavía no los usa.
- **Timeline del cliente (NUEVO):** el modal de detalle del cliente incorporará una sección "Historial de interacciones" con todas las interacciones registradas de ese cliente. Para eso, el endpoint de listado de interacciones deberá aceptar un filtro por cliente.
- **Asistente administrativo (NUEVO):** un widget de chat flotante, visible en todas las páginas de la aplicación (solo para administradores), que entiende consultas de gestión en lenguaje natural y responde con datos reales: clientes nuevos del mes, productos con stock bajo, interacciones de hoy, producto más vendido y resumen de métricas. Usa la MISMA lógica determinística de pattern matching de la tesis (patrones → intención), pero orientada a intenciones administrativas. Es un asistente para el dueño del negocio, NO el bot de ventas de Telegram.

## Capabilities

### New Capabilities
- `admin-bot`: Asistente administrativo determinístico — router de intenciones en el backend (patrones de texto → intención administrativa), endpoint de consulta y widget de chat flotante en el frontend.

### Modified Capabilities
- `interaction-history`: el listado de interacciones pasa a aceptar un filtro opcional por cliente (requerido para el timeline del cliente).
- `client-management-ui`: se agregan paginación de tablas (Clientes y Productos), timeline de interacciones en el modal de detalle del cliente, y se formalizan/verifican la exportación a Excel y los toasts de confirmación.

## Impact

- **Backend** (sin migraciones de base de datos — no se toca el esquema):
  - Nuevo servicio `admin_bot` con el matcher determinístico de intenciones administrativas (misma filosofía que el Bot Router de la tesis).
  - Nueva ruta `POST /api/v1/admin-bot/consult` que recibe texto libre y responde con intención detectada + respuesta armada con datos reales.
  - Filtro `client_id` en `GET /api/v1/interactions/`.
  - Alta de la fuente `admin-bot` en las fuentes válidas de interacción (las consultas del asistente quedan registradas y alimentan las métricas de intenciones).
  - Tests con pytest para el router de intenciones y los endpoints.
- **Frontend**:
  - Nuevo componente `AdminBotWidget` (chat flotante) montado en la aplicación para que aparezca en todas las páginas, con chips de consultas rápidas.
  - Paginación en los hooks `useClients`/`useProducts` y en las tablas correspondientes.
  - Sección "Historial de interacciones" en `ClientDetailsModal`.
  - Verificación/ajuste del botón de exportación y toasts.
- **Dependencias**: ninguna nueva (openpyxl y sonner ya están instalados).