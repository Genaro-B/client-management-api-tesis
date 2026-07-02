## Why

La página de métricas actual solo muestra 3 números básicos (total, activos, inactivos) calculados desde el frontend con `getClients()`. No hay un endpoint dedicado, no hay gráficos, no hay tendencias. No podemos tomar decisiones sin datos — necesitamos un dashboard real que muestre la actividad del sistema.

## What Changes

- Nuevo endpoint `GET /api/v1/metrics/dashboard` que devuelve summary, interacciones por fuente, timeline, registros y top intents
- Nuevo router `backend/src/api/routes/metrics.py`
- Instalar `recharts` en el frontend
- Renovar `MetricsPage.jsx` completamente con cards, gráficos de barras, torta y línea
- Crear `metricService.js` para consultar el endpoint

## Capabilities

### New Capabilities
- `dashboard-metrics`: Endpoint unificado de métricas + visualización con gráficos interactivos

### Modified Capabilities

<!-- None -->

## Impact

- **Backend**: nuevo archivo `src/api/routes/metrics.py`, registro en `main.py`
- **Frontend**: nueva dependencia `recharts`, nuevo `services/metricService.js`, rewrite de `MetricsPage.jsx`
- **API**: nuevo endpoint público `GET /api/v1/metrics/dashboard`
- No hay breaking changes ni migraciones de BD
