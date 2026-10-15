# Design: v3-mejoras-interfaz-bot-administrativo

## Context

- **Estado actual verificado en código**: la exportación a Excel (endpoints `/api/v1/clients/export` y `/api/v1/products/export` + botón en `Topbar`) y los toasts de CRUD (librería `sonner`, hooks `useClients`/`useProducts`) YA EXISTEN. Lo que falta es paginación, timeline del cliente y el asistente administrativo.
- **Backend**: FastAPI + SQLAlchemy, rutas en `src/api/routes/` (`clients`, `products`, `metrics`, `interactions`, `auth`), repos en `src/repositories/`, servicios en `src/services/`. Los endpoints de listado ya aceptan `limit`/`offset` y devuelven `{items, total}`. `GET /api/v1/interactions/` NO filtra por cliente. `POST /api/v1/interactions/` exige `X-Api-Key` y valida `source` contra `VALID_SOURCES`.
- **Modelo de datos**: `productos_asignados` es una columna JSON en la tabla `clients` (no una tabla aparte). `Product` tiene `stock`, `precio`, `activo`. `Interaction` tiene `clientId`, `intent`, `source`, `timestamp`.
- **Bot de la tesis**: el bot de ventas de Telegram corre en n8n con pattern matching determinístico (Switch nodes por intención) y loguea cada mensaje a la API con `intent`. El asistente administrativo de este cambio es OTRA cosa: atiende al dueño del negocio en la web, sobre datos de gestión.
- **Auth actual**: login por email (sin password), sin JWT. Los GETs del sistema no tienen autenticación. El widget corre en el navegador, donde no se pueden guardar secretos.

## Goals / Non-Goals

**Goals:**
- Paginación server-side de 20 registros con controles "← 1 2 3 →" en las tablas de Clientes y Productos.
- Timeline completo de interacciones por cliente dentro de su modal de detalle.
- Asistente administrativo determinístico: router de intenciones en Python (misma filosofía que el Bot Router de la tesis) + endpoint de consulta + widget de chat flotante en todas las páginas, admin-only, con datos reales.
- Verificar/cerrar exportación a Excel y cobertura completa de toasts.
- Sin migraciones de base de datos y sin dependencias nuevas.

**Non-Goals:**
- NO tocar el bot de ventas de Telegram ni el flujo n8n.
- NO integrar IA/LLM — la interpretación es 100% determinística (pattern matching), como exige la tesis.
- NO cambiar el modelo de autenticación del sistema (queda para otro change).
- NO modificar el payload de `GET /api/v1/metrics/dashboard` (el asistente compone sus propios datos).
- NO migrar a MySQL (sigue en SQLite para este change).

## Decisions

### Decision 1: El pattern matching del asistente vive en el BACKEND (Python), no en el frontend

**Choice**: nuevo servicio `AdminIntentRouter` en `backend/src/services/admin_bot/` con un mapa `intención → patrones` (keywords/regex en español). Se expone vía `POST /api/v1/admin-bot/consult`. El widget del frontend es un cliente fino: manda el texto y renderiza la respuesta.

**Rationale**: (1) el pattern matching determinístico es el NÚCLEO de la tesis — debe vivir donde se pueda testear con pytest, documentar y reutilizar; (2) evita implementar el matcher dos veces (Python + JS); (3) de todos modos dos intenciones clave ("producto más vendido" y "clientes nuevos del mes") NO son computables con los endpoints existentes desde el navegador, así que un endpoint nuevo es necesario igual.

**Alternativa considerada**: matcher en JS dentro del frontend llamando a los endpoints existentes. Rechazada: matcher duplicado sin tests, y "top producto"/"nuevos del mes" requerirían igual endpoints o N+1 llamadas.

### Decision 2: Endpoint propio `POST /api/v1/admin-bot/consult`; los datos salen de la misma capa de repositories que alimenta los endpoints existentes

El asistente NO inventa datos: usa `ClientRepository`, `ProductRepository` y queries a `Interaction` — exactamente la misma capa que usan `GET /clients/`, `GET /products/` y `GET /metrics/dashboard`. Garantía de "datos reales" por construcción (misma ruta de código).

Mapeo intención → query:
| Intención | Fuente de datos |
|---|---|
| `clientes-nuevos-mes` | `Client` con `role != "admin"` y `fecha_registro >= primer día del mes` (count y detalle) |
| `stock-bajo` | `Product` activos con `stock <= LOW_STOCK_THRESHOLD` (constante en `src/core/config.py`, default 5) |
| `interacciones-hoy` | `Interaction` con `timestamp >= inicio del día` (count) |
| `producto-top` | Agregación en Python de la columna JSON `productos_asignados`: suma de `cantidad` por `producto_id` entre todos los clientes, top 5. SQLite no ofrece agregación JSON confiable — un único pasada en Python es simple y suficiente a escala tesis |
| `metricas-generales` | Mismos cálculos de `summary` que `/metrics/dashboard` (total/activos/inactivos/interacciones/hoy/semana) |
| `no-entendido` | Fallback con mensaje amigable que lista las consultas soportadas |

### Decision 3: Cada consulta se registra como interacción con `source="admin-bot"`

Se agrega `"admin-bot"` a `VALID_SOURCES` en `interaction_service.py`. Cada consulta al asistente se persiste con el `intent` detectado. Beneficios: (a) alimenta `topIntents` del dashboard de métricas; (b) demuestra el ciclo completo de la tesis (interpretación determinística → acción → registro); (c) el dueño tiene trazabilidad de qué preguntó.

**Riesgo**: el endpoint genera escrituras sin idempotency key → un usuario podría spamear el registro. Aceptable para demo/tesis; el log es append-only y liviano.

### Decision 4: El endpoint de consulta NO usa API key (consistente con la postura actual del sistema)

**Rationale**: los GETs del sistema no tienen auth (solo `POST /interactions` exige `X-Api-Key`, y el frontend no la posee — exponerla en el bundle del navegador sería peor). El widget corre en el navegador → cualquier secreto sería visible. La consulta es de lectura de datos que los GETs ya exponen abiertamente.

**Riesgo documentado**: un tercero podría consultar datos de gestión si conoce el endpoint. Mitigación futura (fuera de alcance): autenticación real con JWT cuando se endurezca el sistema.

### Decision 5: Widget visible solo para administradores, montado en todas las páginas autenticadas

Se monta en `App.jsx` dentro de `ProtectedRoute` (una sola vez, no por página) y se renderiza únicamente si `isAdmin` es true. **Rationale**: los datos que expone (clientes nuevos, stock, métricas) son información de gestión sensible; el "modo solo lectura" de usuarios estándar no debería incluirlos.

### Decision 6: Paginación server-side reutilizando `limit`/`offset` que YA soporta el backend

Los hooks `useClients`/`useProducts` agregan estado `page` (1-based) y envían `limit=20, offset=(page-1)*20`; el total de páginas sale de `res.total` (`ceil(total/limit)`). Los filtros existentes ya resetean la búsqueda; se suma reset de `page` a 1. Los controles ("←", números abreviados, "→") y el texto "Mostrando X–Y de Z" viven en un componente reutilizable `Pagination`.

### Decision 7: Timeline vía filtro `client_id` en el endpoint existente de interacciones

Se agrega el query param opcional `client_id` a `GET /api/v1/interactions/` (combinable con `limit`/`offset`, `total` filtrado). **Rationale**: es un cambio mínimo y consistente con el service existente, evita un endpoint duplicado. El modal de detalle (`ClientDetailsModal`) carga las interacciones del cliente al abrirse y las muestra con fecha/hora (es-AR), fuente, intent y payload resumido. El modal es grande hoy (`size="lg"`) — la sección nueva crece verticalmente; si queda muy alto se evalúa scroll interno.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| Agregar `productos_asignados` (JSON) en Python podría ser lento con muchos clientes | Single pass + top 5; aceptable a escala tesis (SQLite, cientos de clientes) |
| Endpoint de consulta sin auth expone datos de gestión | Consistente con la postura actual (GETs abiertos); hardening con JWT queda documentado para el futuro |
| Matcher determinístico no entiende frases complejas o variantes | Chips de consultas rápidas en el widget + fallback `no-entendido` con sugerencias explícitas |
| Widget flotante puede molestar en pantallas chicas | Colapsable: botón flotante abre/cierra el panel; z-index alto; panel con altura acotada |
| `GET /interactions` con `client_id` deja afuera interacciones sin cliente linkeado | Correcto por diseño: el timeline es por cliente |
| Registro de consultas sin idempotency permite duplicados por reintentos | Aceptable (log append-only); se documenta |

## Migration Plan

1. **Backend primero** (independiente): servicio `admin_bot` + ruta de consulta + filtro `client_id` en interacciones + `VALID_SOURCES` ampliado + tests (`pytest`).
2. **Frontend después**: paginación (hooks + tablas), timeline en modal, toasts faltantes, y por último el widget (depende del endpoint).
3. **Sin migraciones de BD** ni dependencias nuevas. Rollback: revertir commits; el endpoint y el filtro nuevos no rompen comportamiento existente.

## Open Questions

- Umbral de "stock bajo": se fija en `LOW_STOCK_THRESHOLD = 5` en `src/core/config.py` (constante, fácil de ajustar). No requiere confirmación.
- El widget queda admin-only (Decisión 5). Si en el futuro el dueño quiere que otros usuarios lo vean, es un cambio de una condición.