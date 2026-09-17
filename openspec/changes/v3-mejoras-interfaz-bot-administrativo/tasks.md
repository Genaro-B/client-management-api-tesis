## 1. Backend — Asistente administrativo (router determinístico + endpoint)

- [x] 1.1 Crear `backend/src/services/admin_bot/__init__.py` y `admin_intent_router.py` con la clase `AdminIntentRouter`: mapa de intenciones (`clientes-nuevos-mes`, `stock-bajo`, `interacciones-hoy`, `producto-top`, `metricas-generales`, `no-entendido`) → lista de patrones (keywords/regex en español), método `match(texto) -> intent` con fallback a `no-entendido`
- [x] 1.2 Agregar `LOW_STOCK_THRESHOLD = 5` a `backend/src/core/config.py`
- [x] 1.3 Crear `backend/src/services/admin_bot/admin_bot_service.py` con la composición de respuestas por intención usando `ClientRepository`, `ProductRepository` y queries a `Interaction`: clientes nuevos del mes (role != admin, `fecha_registro` >= primer día del mes), stock bajo (`stock <= threshold`), interacciones de hoy (count), producto top (agregación del JSON `productos_asignados` — suma de cantidades por `producto_id`, top 5), métricas generales (mismos cálculos de summary que `/metrics/dashboard`)
- [x] 1.4 Agregar `"admin-bot"` a `VALID_SOURCES` en `backend/src/services/interaction_service.py`
- [x] 1.5 Crear `backend/src/api/routes/admin_bot.py` con `POST /admin-bot/consult` que valida `mensaje` (422 si vacío), llama al router + servicio, registra la interacción con `source="admin-bot"` e `intent` detectado, y devuelve `{"intent", "respuesta"}`; montar el router en `backend/src/main.py` con prefix `/api/v1/admin-bot`
- [x] 1.6 Escribir tests en `backend/tests/test_admin_bot_api.py`: consulta real por cada intención con datos sembrados (nuevos del mes, stock bajo, interacciones hoy, top producto, métricas), fallback `no-entendido`, y validación 422 de mensaje vacío — TODOS verdes con `pytest`

## 2. Backend — Filtro por cliente en interacciones

- [x] 2.1 Agregar query param opcional `client_id` a `GET /api/v1/interactions/` en `backend/src/api/routes/interactions.py` (filtro sobre `Interaction.client_id`, combinable con `limit`/`offset`, `total` filtrado)
- [x] 2.2 Escribir tests en `backend/tests/test_interaction_api.py`: filtro por cliente devuelve solo sus interacciones con `total` correcto, sin filtro mantiene comportamiento actual, cliente sin interacciones devuelve vacío — TODOS verdes con `pytest`

## 3. Frontend — Paginación en tabla de Clientes

- [x] 3.1 Agregar estado `page` (1-based) y `totalPages` al hook `useClients.js`; enviar `limit=20` y `offset=(page-1)*20` a `getClients`; derivar `totalPages = ceil(total/20)`; resetear `page` a 1 cuando cambian los filtros
- [x] 3.2 Crear componente reutilizable `Pagination.jsx` (botones ←/→ deshabilitados en extremos, página actual y total, texto "Mostrando X–Y de Z")
- [x] 3.3 Integrar `Pagination` en `ClientsPage.jsx`/`ClientTable.jsx` y mostrar estado de carga al cambiar de página

## 4. Frontend — Paginación en tabla de Productos

- [x] 4.1 Agregar estado `page` y `totalPages` al hook `useProducts.js`; enviar `limit=20` y `offset` a `getProducts`; resetear `page` a 1 cuando cambian los filtros
- [x] 4.2 Integrar `Pagination` en `ProductsPage.jsx`/`ProductTable.jsx` con estado de carga al cambiar de página

## 5. Frontend — Timeline del cliente en el modal de detalle

- [x] 5.1 En `interactionService.js`, `getInteractions` ya acepta `params` — verificar que soporta `client_id` (no requiere cambios salvo que se use explícitamente)
- [x] 5.2 Agregar a `ClientDetailsModal.jsx` la sección "Historial de interacciones": carga `getInteractions({ client_id: client.id })` al abrir el modal, estados de carga/vacío/error (con reintentar), lista ordenada de más reciente a más antigua con fecha/hora es-AR, fuente, intent y resumen del payload
- [x] 5.3 Verificar en `ClientsPage.jsx` que el modal recibe el cliente con `id` disponible para el timeline

## 6. Frontend — Exportación a Excel y toasts (verificación y cierre)

- [x] 6.1 Verificar que el botón "Exportar Excel" del `Topbar` funciona en Clientes (fallback `exportClientsToExcel`) y en Productos (`onExport={exportProductsToExcel}`) — descarga `.xlsx` en ambos casos
- [x] 6.2 Agregar `toast.success('Archivo exportado correctamente')` al flujo exitoso de `exportClientsToExcel` y `exportProductsToExcel`
- [x] 6.3 Revisar cobertura de toasts: restaurar cliente inactivo (`InactiveClientsPage`/hook correspondiente), restaurar producto inactivo y operaciones de productos asignados — completar toasts faltantes con `sonner`

## 7. Frontend — Widget de chat flotante (asistente administrativo)

- [x] 7.1 Crear `frontend/src/services/adminBotService.js` con `consultAdminBot(mensaje)` → `POST /api/v1/admin-bot/consult`
- [x] 7.2 Crear `frontend/src/components/AdminBotWidget.jsx`: botón flotante (esquina inferior derecha, icono de bot/chat) que abre/cierra panel; burbujas de mensajes; input + botón de envío; chips de consultas rápidas ("Clientes nuevos del mes", "Productos con stock bajo", "Interacciones de hoy", "Producto más vendido", "Resumen de métricas"); indicador "escribiendo…"; manejo de error de red con reintento; estilos con variables de tema existentes (claro/oscuro)
- [x] 7.3 Montar `AdminBotWidget` en `App.jsx` dentro de `ProtectedRoute`, renderizándolo únicamente cuando `isAdmin` es true (visible en todas las páginas autenticadas para administradores)

## 8. Verificación final

- [x] 8.1 Correr toda la suite de tests del backend (`pytest`) — todos verdes
- [x] 8.2 Correr `npm run build` en `frontend/` — build sin errores
- [ ] 8.3 Smoke test manual: exportar Excel, paginar clientes/productos, abrir timeline en modal de detalle, y probar cada chip del asistente respondiendo con datos reales