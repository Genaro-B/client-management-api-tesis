## 1. Setup del proyecto Streamlit

- [x] 1.1 Crear directorio `dashboard/` con `requirements.txt` (streamlit, plotly, pandas, sqlalchemy, pymysql)
- [x] 1.2 Crear `dashboard/app.py` con configuración de página, conexión a DB reusando modelos del backend
- [x] 1.3 Agregar `PYTHONPATH` para que Streamlit pueda importar `backend.src` — resuelto en `db.py` con `sys.path.insert`

## 2. Dashboard de métricas

- [x] 2.1 Implementar queries de métricas (total clientes, activos, inactivos, interacciones totales/hoy/esta semana)
- [x] 2.2 Mostrar cards de resumen con `st.metric` o custom HTML — se usan divs con CSS personalizado
- [x] 2.3 Implementar timeline de interacciones (30 días) con Plotly LineChart
- [x] 2.4 Implementar gráfico de torta de interacciones por fuente
- [x] 2.5 Implementar gráfico de barras de top 5 intents
- [x] 2.6 Agregar `@st.cache_data` con TTL a las queries de métricas

## 3. CRUD de clientes

- [x] 3.1 Mostrar tabla de clientes con datos desde DB
- [x] 3.2 Implementar formulario para crear cliente
- [x] 3.3 Implementar edición de cliente (seleccionar de tabla, editar, guardar)
- [x] 3.4 Implementar eliminación de cliente con confirmación
- [x] 3.5 Refrescar tabla automáticamente después de operaciones CRUD — via `st.rerun()` + `st.cache_data.clear()`

## 4. Interacciones por cliente

- [x] 4.1 Agregar columna de acciones "Ver interacciones" en la tabla de clientes
- [x] 4.2 Mostrar interacciones del cliente seleccionado en tabla aparte
- [x] 4.3 Mostrar métricas rápidas del cliente (total interacciones, última interacción)

## 5. Sidebar y navegación

- [x] 5.1 Implementar sidebar con navegación entre secciones (Métricas, Clientes)
- [x] 5.2 Usar `st.sidebar.radio` con dos opciones (Métricas y Clientes)

## 6. Docker y polish

- [ ] 6.1 Agregar servicio Streamlit al `docker-compose.yml` — pendiente
- [ ] 6.2 Verificar que el dashboard funciona con `docker compose up` — pendiente
- [x] 6.3 Documentado en README.md
