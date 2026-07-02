## 1. Backend — Endpoint de métricas

- [x] 1.1 Crear `backend/src/api/routes/metrics.py` con router y endpoint `GET /dashboard`
- [x] 1.2 Implementar query de summary (total clientes, activos, inactivos, total interacciones, hoy, esta semana)
- [x] 1.3 Implementar query de interacciones por source (GROUP BY source)
- [x] 1.4 Implementar timeline de 30 días (interacciones por día, rellenar días sin datos con 0)
- [x] 1.5 Implementar registros por mes (GROUP BY month en fecha_registro)
- [x] 1.6 Implementar top 5 intents (GROUP BY intent, ORDER BY count DESC, LIMIT 5)
- [x] 1.7 Registrar el router en `src/main.py`

## 2. Frontend — Dashboard visual

- [x] 2.1 Instalar `recharts` en el frontend
- [x] 2.2 Crear `frontend/src/services/metricService.js` con función `getDashboard()`
- [x] 2.3 Renovar `MetricsPage.jsx` con cards de resumen (6 indicadores)
- [x] 2.4 Agregar gráfico de torta (PieChart) de interacciones por fuente
- [x] 2.5 Agregar gráfico de línea (LineChart) de timeline de 30 días
- [x] 2.6 Agregar gráfico de barras (BarChart) de top intents
- [x] 2.7 Manejar estados de loading, error y empty

## 3. Tests

- [x] 3.1 Agregar tests para el endpoint GET /api/v1/metrics/dashboard
- [x] 3.2 Verificar que todos los tests existentes sigan pasando
