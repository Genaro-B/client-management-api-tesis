## ADDED Requirements

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
