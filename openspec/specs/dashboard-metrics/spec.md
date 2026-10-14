# dashboard-metrics Specification

## Purpose
TBD - created by archiving change dashboard-metrics. Update Purpose after archive.
## Requirements
### Requirement: Dashboard summary endpoint

El sistema SHALL exponer `GET /api/v1/metrics/dashboard` que devuelva un objeto JSON con las siguientes secciones: `summary`, `interactionsBySource`, `interactionsTimeline`, `registrationsByMonth`, `topIntents`.

#### Scenario: Returns full dashboard payload
- **WHEN** se hace GET a `/api/v1/metrics/dashboard`
- **THEN** la respuesta tiene status 200
- **THEN** el body contiene los campos `summary`, `interactionsBySource`, `interactionsTimeline`, `registrationsByMonth`, `topIntents`

#### Scenario: Summary contains correct counts
- **WHEN** se hace GET a `/api/v1/metrics/dashboard`
- **THEN** `summary.totalClients` es el total de clientes no-admin
- **THEN** `summary.activeClients` es el total de clientes activos no-admin
- **THEN** `summary.inactiveClients` es activeClients - totalClients
- **THEN** `summary.totalInteractions` es el total de interacciones
- **THEN** `summary.interactionsToday` es el conteo de interacciones del día actual
- **THEN** `summary.interactionsThisWeek` es el conteo de interacciones de los últimos 7 días

### Requirement: Interactions by source

El endpoint SHALL devolver un desglose de interacciones agrupadas por `source`.

#### Scenario: Returns source breakdown
- **WHEN** hay interacciones con distintos `source`
- **THEN** `interactionsBySource` contiene un objeto con cada source como key y su count como value

### Requirement: Interactions timeline (30 days)

El endpoint SHALL devolver el conteo de interacciones por día para los últimos 30 días.

#### Scenario: Returns daily counts
- **WHEN** se hace GET a `/api/v1/metrics/dashboard`
- **THEN** `interactionsTimeline` es un array de objetos con `date` e` y `count`
- **THEN** cada `date` tiene formato `YYYY-MM-DD`
- **THEN** el array cubre exactamente 30 días (incluyendo días sin interacciones con count 0)

### Requirement: Client registrations by month

El endpoint SHALL devolver la cantidad de clientes registrados por mes.

#### Scenario: Returns monthly registration counts
- **WHEN** se hace GET a `/api/v1/metrics/dashboard`
- **THEN** `registrationsByMonth` es un array de objetos con `month` (YYYY-MM) y `count`
- **THEN** los meses están ordenados ascendente

### Requirement: Top intents

El endpoint SHALL devolver los 5 intents más frecuentes entre las interacciones que tienen `intent` no nulo.

#### Scenario: Returns top intents
- **WHEN** hay interacciones con distintos `intent`
- **THEN** `topIntents` es un array de objetos con `intent` y `count`
- **THEN** están ordenados descendente por `count`
- **THEN** máximo 5 elementos

### Requirement: Dashboard visual

El frontend SHALL mostrar el dashboard de métricas con gráficos interactivos.

#### Scenario: Shows summary cards
- **WHEN** el dashboard carga exitosamente
- **THEN** se muestran 6 cards: Total Clientes, Activos, Inactivos, Interacciones, Hoy, Esta Semana

#### Scenario: Shows interactions by source chart
- **WHEN** el dashboard carga exitosamente
- **THEN** se muestra un gráfico de torta (PieChart) con la distribución por fuente

#### Scenario: Shows interactions timeline
- **WHEN** el dashboard carga exitosamente
- **THEN** se muestra un gráfico de línea (LineChart) con interacciones de los últimos 30 días

#### Scenario: Shows top intents
- **WHEN** el dashboard carga exitosamente
- **THEN** se muestra un gráfico de barras horizontal (BarChart) con los top intents

#### Scenario: Shows loading state
- **WHEN** el dashboard está cargando
- **THEN** se muestra un spinner

#### Scenario: Shows error state
- **WHEN** la request al endpoint falla
- **THEN** se muestra un mensaje de error con opción de reintentar

### Requirement: Endpoint de métricas de ventas

El sistema SHALL exponer `GET /api/v1/metrics/ventas?desde=<YYYY-MM-DD>&hasta=<YYYY-MM-DD>` (JWT) devolviendo `summary` con `ventas` (cantidad), `ingresos` (suma de totales), `ticketPromedio` (`ingresos / ventas`, 0 si no hay ventas) y `vsPeriodoAnterior` (variación % respecto del período inmediato anterior de igual duración).

- Todas las secciones SHALL contar SOLO ventas con `estado IN ("CONFIRMADO", "COMPLETADO")` (base contable).
- Sin parámetros, el período por defecto SHALL ser los últimos 30 días.

#### Scenario: Resumen con base contable
- **WHEN** hay 2 ventas CONFIRMADO (100 y 300) y 3 PENDIENTE en el período
- **THEN** `summary.ventas = 2`, `summary.ingresos = 400`, `summary.ticketPromedio = 200`

#### Scenario: Ticket promedio sin ventas
- **WHEN** el período no tiene ventas de la base contable
- **THEN** `summary.ventas = 0`, `summary.ingresos = 0` y `summary.ticketPromedio = 0`

#### Scenario: Comparación con el período anterior
- **WHEN** el período actual tuvo 4 ventas y el anterior 2
- **THEN** `vsPeriodoAnterior` refleja la variación calculada (p. ej. +100%)

### Requirement: Serie temporal y análisis de productos de ventas

El endpoint de métricas de ventas SHALL devolver `serieDiaria` (`[{fecha, ventas, ingresos}]` con días sin ventas en 0, formato `YYYY-MM-DD`, ascendente), `porHorario` (conteo de ventas por hora del día) y `topProductos` (productos de la base contable ordenados por cantidad vendida, top 5).

#### Scenario: Días vacíos en cero
- **WHEN** el período de 7 días solo tiene ventas el día 1 y el día 5
- **THEN** `serieDiaria` tiene exactamente 7 entradas, con `ventas: 0, ingresos: 0` los días sin ventas

#### Scenario: Top productos solo de la base contable
- **WHEN** un producto tiene 10 unidades en ventas PENDIENTE y 3 en CONFIRMADO
- **THEN** aparece con 3 unidades en `topProductos`

### Requirement: Página de ventas en el panel React

El frontend SHALL mostrar una página "Ventas" (entrada en la navegación) con: cards de resumen (ventas, ingresos, ticket promedio, variación vs período anterior), gráfico de la serie temporal, tabla de ventas con su estado (badge) y acciones de transición (confirmar/completar/cancelar según estado), y un buscador de tickets por cliente + fecha.

- Las acciones de transición SHALL llamar a los endpoints JWT y refrescar los datos; los errores muestran toast (patrón sonner existente).
- La página SHALL seguir los patrones existentes del panel (`ProductsPage`/`ProductTable`, axios instance, `MetricCard`, `StatusBadge`).

#### Scenario: Visualización del resumen
- **WHEN** la página carga con datos disponibles
- **THEN** se muestran las 4 cards y el gráfico de la serie temporal

#### Scenario: Confirmar una venta desde la UI
- **WHEN** un usuario marca "Confirmar" en una venta PENDIENTE
- **THEN** la venta pasa a CONFIRMADO, la tabla refleja el nuevo estado y aparece un toast de éxito

#### Scenario: Estado de error
- **WHEN** la request de métricas falla
- **THEN** se muestra mensaje de error con opción de reintentar

