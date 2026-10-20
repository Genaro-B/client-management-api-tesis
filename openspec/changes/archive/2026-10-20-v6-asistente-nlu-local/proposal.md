## Why

El asistente administrativo actual ("admin bot") responde con un matcher determinístico muy preciso, pero limitado: muchas frases naturales (sinónimos, errores de tipeo o formas distintas de preguntar lo mismo) caen en `no-entendido`. Se busca hacerlo más versátil y con mejor comprensión **sin depender de un LLM externo**, agregando un clasificador local de intenciones (scikit-learn) que actúe como fallback del matcher existente. A la vez, se deja una capa opcional de LLM local (Ollama) **deshabilitada por defecto**, lista para activarse por configuración.

## What Changes

- **Cascada de selección de cerebro**: variable de entorno `ADMIN_BOT_BRAIN` (`classifier` | `deterministic` | `ollama`). Por defecto `classifier`.
- **Path de seguridad sin regresión**: el matcher determinístico existente corre **primero** siempre; solo cuando devuelve `no-entendido` se consulta el clasificador local. Esto garantiza preservar el comportamiento actual (0 regresiones).
- **Clasificador local (fallback)**: módulo de NLU local con scikit-learn (TF-IDF con n-grams de palabra y carácter) entrenado con dataset etiquetado en español rioplatense, con umbral de confianza configurable (`ADMIN_BOT_NLU_THRESHOLD`, default ~0.55). Persistido en caché/lazy-load.
- **Capa opcional Ollama (deshabilitada por defecto)**: cliente HTTP con `httpx` hacia `POST {OLLAMA_URL}/api/chat` (stream:false), contexto construido con datos reales (ventas del día, stock bajo, métricas), con timeouts, manejo de errores y fallback a `no-entendido`. Nunca requerido para ejecutar tests.
- **Configuración explícita**: nuevas variables de entorno con defaults y lectura por llamada (patrón coherente con `get_bcrypt_rounds()`), documentadas en `.env.example`.
- **Documentación**: sección en `README.md` sobre cómo funciona y cómo activar Ollama paso a paso.
- **Limpieza menor**: tareas para eliminar/ignorar los archivos basura en raíz (`backend.log`, `backend.err`, `tmp_botrouter.js`).
- **Alineación de spec**: se agregan los intents `ventas-hoy` y `ticket-cliente` (presentes en código, ausentes en spec actual) y se ajusta el requisito del matcher para reflejar que es la primera capa de una cascada.

## Capabilities

### Modified Capabilities

- `admin-bot`: modifica el requisito "Matcher determinístico de intenciones administrativas" para describirlo como **primera capa** de una cascada (permitiendo un clasificador local ML como fallback según configuración). Se añaden requisitos dentro de esta misma capability para: clasificador local de intenciones (fallback), cascada de resolución y selección de cerebro (`ADMIN_BOT_BRAIN`), capa opcional de LLM local (Ollama) deshabilitada por defecto, y configuración de NLU/cerebros vía variables de entorno. También se amplía la cobertura con los intents `ventas-hoy` y `ticket-cliente`.

## Impact

- **Backend**: `backend/src/services/admin_bot/` (wiring de cascada), `backend/src/core/config.py` (nuevas variables), `backend/requirements.txt` (+`scikit-learn`), `.env.example` (nuevo), tests de admin-bot extendidos.
- **Frontend**: sin cambios funcionales (widget lee `respuesta`).
- **Deps**: `scikit-learn` añadido (no rompe tests existentes). `httpx` ya presente. Ollama opcional.
- **Tests**: 316 backend + 110 frontend deben permanecer verdes. Nuevos tests unitarios del clasificador y tests con httpx mockeado para Ollama.
- **Docs**: `README.md` actualizado con sección de activación de Ollama.