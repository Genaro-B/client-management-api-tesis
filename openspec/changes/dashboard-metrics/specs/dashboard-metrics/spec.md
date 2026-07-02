## ADDED Requirements

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
