## Context

El proyecto tiene un backend FastAPI completo con modelos SQLAlchemy (`Client`, `Interaction`) y conexión a MySQL. Ya existe un frontend React con dashboard de métricas y CRUD de clientes. Se agrega un dashboard Streamlit como herramienta interna que conecta directo a la base de datos, sin depender de la API REST.

El dashboard Streamlit está pensado para:
- Visualización rápida de métricas sin necesidad de que la API esté corriendo
- Consulta directa a DB para exploración de datos
- Operaciones administrativas livianas

## Goals / Non-Goals

**Goals:**
- Dashboard Streamlit que conecta directo a MySQL mediante SQLAlchemy
- Reutilizar modelos existentes (`Client`, `Interaction`) del backend
- Visualización de métricas: cards de resumen, gráficos (timeline, fuentes, intents)
- CRUD de clientes desde el dashboard
- Visualización de interacciones por cliente
- Desplegable con `docker-compose` o standalone con `streamlit run`

**Non-Goals:**
- NO reemplazar el frontend React existente
- NO pasar por la API REST — conexión directa a DB
- NO implementar autenticación compleja (modo internal tool)
- NO reemplazar testes existentes del backend

## Decisions

### Decisión 1: Conexión directa a DB con SQLAlchemy
- **Opción**: Reutilizar `backend/src/database/session.py` y `backend/src/models/` en lugar de duplicar config
- **Rationale**: Los modelos ya están definidos y probados. Streamlit puede importar del mismo `backend/src/` agregando al PYTHONPATH
- **Alternativa**: Crear modelos duplicados en `dashboard/` — descartado por mantenimiento

### Decisión 2: Ubicación del proyecto
- **Opción**: `dashboard/` en la raíz del repo (no dentro de `backend/`)
- **Rationale**: Es una aplicación separada del backend, con sus propias dependencias y entry point
- **Alternativa**: Meterlo en `backend/dashboard/` — descartado porque mezcla concerns

### Decisión 3: Librería de gráficos
- **Opción**: Plotly (interactivo, nativo Streamlit, zoom, hover)
- **Rationale**: Streamlit tiene `st.plotly_chart()` nativo, los gráficos son interactivos y se ven bien
- **Alternativa**: Matplotlib — menos interactivo; Altair — buena opción pero menos conocido

### Decisión 4: Manejo de caché
- **Opción**: Usar `@st.cache_data` de Streamlit para evitar consultas repetidas a DB
- **Rationale**: Streamlit rerunea todo el script en cada interacción, sin caché cada clic hace una query nueva
- **TTL**: Cache con TTL de 60 segundos para métricas, sin caché para operaciones CRUD

### Decisión 5: Autenticación
- **Opción**: Sin autenticación (modo internal tool, solo accesible en localhost)
- **Rationale**: Es una herramienta interna de desarrollo/administración, no un producto público
- **Alternativa**: Basic auth con Streamlit secrets — overkill para este caso

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| Streamlit compite con el frontend React por atención | Dejarlo claro en la documentación: Streamlit es internal tool, React es el frontend oficial |
| Cambios en modelos del backend rompen el dashboard | El dashboard importa los mismos modelos — si cambian, se rompe en compile time, fácil de detectar |
| Performance: Streamlit rerunea todo en cada interacción | Usar `@st.cache_data` con TTL para queries pesadas de métricas |
| Dependencias duplicadas | Mantener `dashboard/requirements.txt` separado pero apuntando a mismas versiones de SQLAlchemy, pymysql |
