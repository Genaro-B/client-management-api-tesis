<div align="center">
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/n8n-5A2B8C?style=flat&logo=n8n&logoColor=white" />
  <img src="https://img.shields.io/badge/Telegram-26A5E4?style=flat&logo=telegram&logoColor=white" />
  <img src="https://img.shields.io/badge/status-desarrollo-yellow" />
</div>

<br />

<div align="center">
  <h1>🏢 Client Management API</h1>
  <p><strong>Sistema de Automatización Inteligente para la Gestión de Clientes</strong></p>
  <p>API REST + Panel Web + Integración con Telegram mediante flujos automatizados</p>
  <br />
</div>

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Stack Tecnológico](#-stack-tecnológico)
- [Arquitectura](#-arquitectura)
- [Primeros Pasos](#-primeros-pasos)
- [API REST](#-api-rest)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Variables de Entorno](#-variables-de-entorno)
- [Seguridad](#-seguridad)
- [Autor](#-autor)

---

## 📌 Descripción General

Sistema modular de gestión de clientes que integra:

- **API REST** construida con **FastAPI** como núcleo de la lógica de negocio
- **Panel web** desarrollado en **React + Vite + Tailwind CSS**
- **Automatización** de flujos conversacionales mediante **n8n**
- **Canal de atención** vía **Telegram** con respuestas inteligentes

> Proyecto desarrollado como Trabajo Final Integrador de la **Tecnicatura Universitaria en Programación** — **UTN**.

---

## 🛠 Stack Tecnológico

<div align="center">

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| **Backend** | ![Python](https://img.shields.io/badge/Python%203.14-3776AB?style=flat&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) | API REST, lógica de negocio, validación |
| **Base de datos** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white) / ![MySQL](https://img.shields.io/badge/MySQL%208-4479A1?style=flat&logo=mysql&logoColor=white) | Persistencia (SQLite en dev, MySQL en prod) |
| **ORM** | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CC342D?style=flat&logo=python&logoColor=white) | Mapeo objeto-relacional |
| **Frontend** | ![React](https://img.shields.io/badge/React%2018-61DAFB?style=flat&logo=react&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white) ![Tailwind](https://img.shields.io/badge/Tailwind%204-06B6D4?style=flat&logo=tailwindcss&logoColor=white) | Panel administrativo |
| **Automatización** | ![n8n](https://img.shields.io/badge/n8n-5A2B8C?style=flat&logo=n8n&logoColor=white) | Flujos automatizados, integración con APIs |
| **Mensajería** | ![Telegram](https://img.shields.io/badge/Telegram%20Bot%20API-26A5E4?style=flat&logo=telegram&logoColor=white) | Canal de atención al cliente |
| **Túnel** | ![ngrok](https://img.shields.io/badge/ngrok-1F1E1E?style=flat&logo=ngrok&logoColor=white) | Exposición local para webhooks en desarrollo |

</div>

---

## 🏗 Arquitectura

```
┌──────────────┐
│   Usuario    │
│  (Telegram)  │
└──────┬───────┘
       │  mensaje de texto
       ▼
┌──────────────┐       ┌────────────┐
│    ngrok     │──────▶│    n8n     │
│ (túnel TLS)  │       │  Webhook   │
└──────────────┘       └─────┬──────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
           ┌──────────────┐  ┌──────────────┐
           │ Google Sheets│  │   FastAPI    │
           │   (log)      │  │ /interactions│
           └──────────────┘  └──────┬───────┘
                                    │
                                    ▼
                           ┌──────────────┐
                           │   SQLite /   │
                           │    MySQL     │
                           └──────────────┘

    ┌────────────────────────────────────────┐
    │           Frontend React               │
    │  (Dashboard → clientes, métricas,      │
    │            interacciones, perfil)       │
    └────────────────────────────────────────┘
```

### Flujo de una interacción

1. El usuario envía un mensaje al bot de Telegram
2. Telegram dispara un webhook hacia n8n (vía ngrok)
3. n8n extrae el mensaje, usuario y metadatos
4. **En paralelo:**
   - 📊 Guarda en Google Sheets (historial)
   - 📡 POST a `/api/v1/interactions/` (persistencia en BD)
5. n8n clasifica el mensaje según su contenido:
   - 🛒 "*comprar*" → respuesta de venta
   - 💰 "*precio*" → respuesta informativa
   - 👋 cualquier otro → respuesta general

---

## 🚀 Primeros Pasos

### Prerrequisitos

- Python 3.14+
- Node.js 20+
- n8n (`npm install -g n8n`)
- ngrok (cuenta gratuita)
- Bot de Telegram (creado con @BotFather)

### 1. Backend

```bash
# Activar entorno virtual
cd backend
.venv\Scripts\activate

# Ejecutar migraciones (si es primera vez)
alembic upgrade head

# Iniciar servidor
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

✅ `http://localhost:8000` — API  
📖 `http://localhost:8000/docs` — Documentación Swagger  
📖 `http://localhost:8000/redoc` — Documentación ReDoc

### 2. Frontend

```bash
cd frontend
npm install    # solo la primera vez
npm run dev
```

✅ `http://localhost:5173` — Panel web  
🔑 **Admin:** `genarobusto@gmail.com` (sin contraseña — solo email)

> El frontend utiliza el proxy de Vite (`/api → localhost:8000`), no requiere configuración CORS adicional.

### 3. n8n

```bash
n8n start
```

✅ `http://localhost:5678`

> **Importante:** Al configurar peticiones HTTP desde n8n hacia el backend local, usar `http://127.0.0.1:8000` en lugar de `localhost` para evitar problemas de resolución IPv6 en Windows.

### 4. ngrok + Telegram

```bash
ngrok http 5678
```

Tomar la URL `https://xxxx.ngrok.io` y **activar el workflow** en n8n.  
n8n configura automáticamente el webhook de Telegram.

---

## 📡 API REST

### Endpoints

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/clients/` | Listar clientes | — |
| `POST` | `/api/v1/clients/` | Crear cliente | — |
| `GET` | `/api/v1/clients/{id}` | Obtener cliente | — |
| `PATCH` | `/api/v1/clients/{id}` | Actualizar cliente | — |
| `DELETE` | `/api/v1/clients/{id}` | Eliminar cliente (soft-delete) | — |
| `GET` | `/api/v1/clients/inactive` | Clientes inactivos | Admin |
| `PATCH` | `/api/v1/clients/{id}/restore` | Restaurar cliente | Admin |
| `GET` | `/api/v1/clients/export` | Exportar a Excel | — |
| `POST` | `/api/v1/auth/login` | Iniciar sesión | — |
| `GET` | `/api/v1/interactions/` | Listar interacciones | — |
| `POST` | `/api/v1/interactions/` | Crear interacción | `X-Api-Key` |

> Los endpoints protegidos con **`X-Api-Key`** requieren el header con la clave configurada en la variable de entorno `API_KEY`.

---

## 🧪 Tests

La suite de tests está organizada en **tres capas** que reflejan la arquitectura hexagonal del backend:

| Capa | Archivo | Tests | ¿Qué cubre? |
|------|---------|-------|-------------|
| **Repositorio** | `test_client_repository.py` | 7 | CRUD contra SQLAlchemy, paginación, soft-delete, búsqueda |
| **Repositorio** | `test_interaction_repository.py` | 3 | Persistencia de interacciones, linking con clientes |
| **Servicio** | `test_client_service.py` | 2 | Reglas de negocio: unicidad de email |
| **Servicio** | `test_interaction_service.py` | 10 | Validaciones, clientLookup, idempotencia |
| **API** | `test_clients_api.py` | 22 | CRUD completo clientes vía HTTP, exportación Excel |
| **API** | `test_auth_api.py` | 5 | Login: exitoso, email no registrado, cuenta inactiva |
| **API** | `test_interaction_api.py` | 10 | POST con auth/idempotencia + GET listado |
| **API** | `test_integration_post.py` | 1 | Smoke test de creación de cliente |

**Total: 65 tests · 1.2s de ejecución**

### Cómo correrlos

```bash
# Desde la raíz del proyecto
cd backend
..\.venv\Scripts\python -m pytest tests/ -v

# Ejecutar un archivo específico
..\.venv\Scripts\python -m pytest tests/test_clients_api.py -v

# Ejecutar por nombre
..\.venv\Scripts\python -m pytest tests/ -k "login" -v
```

> ⚠️ **Importante:** Usar siempre el Python del entorno virtual (`.venv\Scripts\python.exe`), no el global. El sistema Python (`C:\Python314`) no tiene `openpyxl` ni las dependencias del proyecto.

### Arquitectura de testing

Todas las pruebas de API usan **SQLite en memoria** con `StaticPool`, lo que significa:
- ✅ **Aisladas:** cada test arranca con una base de datos vacía
- ✅ **Rápidas:** ~1.2s para los 65 tests
- ✅ **Sin efectos secundarios:** no tocan la base de datos real (`dev.db`)
- ✅ **Sin dependencias externas:** no necesitan n8n, Telegram ni ngrok

Las fixtures compartidas viven en `tests/conftest.py`:
- `db_session` — sesión SQLite en memoria por test
- `client` — `TestClient` de FastAPI con la BD overrideada
- `auth_headers` — headers con `X-Api-Key` para endpoints protegidos
- `sample_client` / `sample_inactive_client` — clientes precargados

---

## 📁 Estructura del Proyecto

```
├── backend/
│   ├── alembic/               # Migraciones de base de datos
│   ├── src/
│   │   ├── api/routes/        # Endpoints (clients, auth, interactions)
│   │   ├── core/              # Configuración, auth, excepciones
│   │   ├── database/          # Engine SQLAlchemy, sesión
│   │   ├── models/            # Modelos ORM
│   │   ├── repositories/      # Capa de acceso a datos
│   │   ├── schemas/           # Esquemas Pydantic
│   │   └── services/          # Lógica de negocio
│   ├── requirements.txt
│   └── dev.db                 # Base de datos local (no trackeada)
│
├── frontend/
│   ├── src/
│   │   ├── components/        # Sidebar, Topbar, tablas, modales
│   │   ├── hooks/             # useAuth, useClients
│   │   ├── pages/             # Login, Dashboard, Métricas, Interacciones
│   │   └── services/          # Clientes HTTP (Axios)
│   └── vite.config.js         # Proxy a backend
│
├── openspec/                  # Documentación técnica del proyecto
├── Docs/                      # Documentación adicional, flujos n8n
├── .gitignore
└── README.md
```

---

## 🔧 Variables de Entorno

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `DATABASE_URL` | `sqlite:///./dev.db` | Cadena de conexión a la base de datos |
| `API_KEY` | `dev-api-key-123` | Clave para endpoints protegidos (`X-Api-Key`) |

> En producción, cambiar `API_KEY` por un valor seguro y configurar `DATABASE_URL` para usar MySQL.

---

## 🔐 Seguridad

- Los archivos **`.json` exportados de n8n** contienen tokens y credenciales → **ignorados por git**
- La **`API_KEY`** por defecto es solo para desarrollo → **cambiar en producción**
- El login es **email-only** (sin contraseña) durante desarrollo
- La base de datos **SQLite** no debe usarse en producción

---

## 👨‍💻 Autor

**Genaro Busto**  
Tecnicatura Universitaria en Programación  
Universidad Tecnológica Nacional (UTN)

---

<div align="center">
  <sub>Desarrollado con fines académicos, educativos y de investigación.</sub>
</div>
