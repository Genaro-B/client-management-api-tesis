## Context

Actualmente no existe un endpoint de métricas. La página `MetricsPage.jsx` obtiene todos los clientes con `getClients()` y calcula 3 números (total/activos/inactivos) del lado del cliente — ineficiente y sin datos de interacciones.

El sistema ya tiene datos de clientes e interacciones en SQLite. Necesitamos un endpoint backend que agregue esos datos y un frontend que los visualice con gráficos.

## Goals / Non-Goals

**Goals:**
- Endpoint `GET /api/v1/metrics/dashboard` con datos agregados de clients + interactions
- Dashboard visual con cards de resumen, gráfico de torta (fuentes), línea (timeline), barras (intents)
- Cero nuevas tablas o migraciones — todo sobre datos existentes

**Non-Goals:**
- No se agregan métricas en tiempo real (WebSocket)
- No hay filtros ni fechas custom — dashboard fijo con últimos 30 días
- No hay exportación de métricas

## Decisions

1. **Endpoint único vs múltiples**: Un solo `GET /dashboard` que devuelve todo. Más simple de cachear y consumir. Si escala mal en el futuro, se divide.

2. **Cálculos en SQL vs Python**: Las agregaciones simples (count, group by) se hacen con SQLAlchemy queries. El timeline de 30 días se arma en Python para evitar SQL complejo.

3. **Recharts vs Chart.js**: Recharts es declarativo (JSX), liviano, y se integra naturalmente con React. Chart.js requiere canvas y más boilerplate.

4. **Endpoint sin auth**: Por consistencia con el resto de los endpoints de lectura (GET /clients, GET /interactions). Si se necesita protección en el futuro, se agrega `verify_api_key`.

## Risks / Trade-offs

- [Riesgo] El query de timeline puede ser lento con muchas interacciones → Mitigación: limitado a 30 días con índices en `timestamp`
- [Riesgo] Recharts agrega ~30KB al bundle → Mitigación: es una dependencia común, vale la pena por la UX
