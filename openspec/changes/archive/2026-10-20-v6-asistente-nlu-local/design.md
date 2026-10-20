## Context

El asistente administrativo actual usa un router determinístico (`AdminIntentRouter`) con patrones por intención. Cuando ninguna regla coincide, retorna `no-entendido`. Esto es preciso pero poco versátil ante sinónimos, formas alternativas o pequeños errores. 

El objetivo es mantener **exactamente** el comportamiento probado (316 backend + 110 frontend verdes), mientras agregamos un clasificador local (scikit-learn) como fallback cuando el matcher falla. También dejamos implementado (pero deshabilitado por defecto) un cerebro opcional basado en Ollama, con configuración clara y sin hacerlo obligatorio.

## Goals / Non-Goals

**Goals:**
- Añadir clasificador local NLU con umbral de confianza configurable, persistido/cached y entrenado con dataset en español rioplatense.
- Implementar cascada: **deterministic matcher PRIMERO** → si `no-entendido`, correr clasificador (si `classifier` brain) → si confianza < umbral, mantener `no-entendido`.
- Selección de cerebro via `ADMIN_BOT_BRAIN = classifier|deterministic|ollama` (default `classifier`).
- Mantener `ADMIN_BOT_BRAIN=deterministic` con comportamiento idéntico al actual.
- Capa Ollama opcional: cliente HTTP con `httpx`, construye contexto con datos reales, manejo de errores/timeouts, fallback graceful.
- Config por llamada (mirando patrón `get_bcrypt_rounds()`), nuevas vars documentadas en `.env.example`.
- Sección README sobre activación de Ollama.
- Alinear spec con intents reales (`ventas-hoy`, `ticket-cliente`).
- Tareas para limpiar archivos basura raíz (`backend.log`, `backend.err`, `tmp_botrouter.js`) y asegurar `.gitignore`.

**Non-Goals:**
- Cambiar contrato API (`/api/v1/admin-bot/consult` retorna `{intent, respuesta}`).
- Modificar widget frontend (solo lee `respuesta`).
- Hacer Ollama obligatorio o tener dependencia real en entorno de tests.
- Fix de `require_admin` (separado).
- Cambiar comportamiento de intents existentes.

## Decisions

### D1: Cascada determinística primero (no-regresión garantizada)
**Decisión:** Ejecutar siempre `AdminIntentRouter.classify()` primero. Solo si resultado es `no-entendido` y `ADMIN_BOT_BRAIN != deterministic`, invocar clasificador (y opcionalmente Ollama).
**Rationale:** Evita romper los 42 tests de admin-bot y cualquier comportamiento probado. El clasificador solo "rescata" casos que hoy caen en `no-entendido`.
**Alternativas:** Reemplazar matcher por clasificador (descartado: riesgo alto, perdería precisión de patrones exactos). Híbrido paralelo (descartado: ambigüedad).

### D2: Brain selection vía env var
**Decisión:** `ADMIN_BOT_BRAIN` con valores `classifier|deterministic|ollama`. Default `classifier`.
**Rationale:** Clarifica intención y permite aislar modo puro (deterministic) para debugging/regresión. 
**Alternativas:** Flag boolean (menos explícito para 3 modos).

### D3: Clasificador con TF-IDF + n-grams (palabra + carácter)
**Decisión:** Usar `TfidfVectorizer` con `analyzer='word'` + `char` n-grams (e.g. ngram_range apropiado) y clasificador lineal (`LogisticRegression` o `LinearSVC`). Entrenar con dataset versionado en código (15-20 frases por intent incluyendo frases exactas de tests + sinónimos/typos).
**Rationale:** Robusto para español, tolera variaciones/typos. Ligero, sin dependencias pesadas. joblib para persistir modelo/vectorizer en `backend/src/services/admin_bot/data/` o caché en memoria.
**Alternativas:** fastText (extra dep), spaCy (pesado), embeddings locales (complejidad).

### D4: Umbral de confianza configurable
**Decisión:** `ADMIN_BOT_NLU_THRESHOLD` default ~0.55. Si `proba.max()` < threshold → `no-entendido`.
**Rationale:** Evita falsos positivos. Ajustable sin tocar código.
**Alternativas:** 0.5 (más agresivo, riesgo de regresión sutil), 0.7 (muy conservador).

### D5: Lectura de config por llamada
**Decisión:** Nuevas funciones tipo `get_bcrypt_rounds()` en config (o helpers) que leen `os.getenv` con defaults en cada llamada (o cached). Seguir patrón existente en `security.py:22-25`.
**Rationale:** Coherente con código actual. Fácil testear/mockear con env vars.
**Alternativas:** Module-level constants (se setean al import) — menos flexible para tests.

### D6: Ollama client con httpx (mockeable)
**Decisión:** Cliente aislado (`ollama_client.py`) usando `httpx.Client`/`post` con `timeout`, `json`, manejo `httpx.ConnectError`, `httpx.TimeoutException`. Response: parsear `message.content`. Tests mockean httpx.
**Rationale:** `httpx` ya en requirements. Mockeable. No hard dependency.
**Alternativas:** requests (no presente), aiohttp innecesario.

### D7: Contexto real para Ollama
**Decisión:** Builder de contexto reutiliza helpers existentes: `sale_service.ventas_del_dia`/`ventas_hoy`, `ticket` por cliente, resumen de métricas, stock bajo. Prompt sistema en español rioplatense: "usá SOLO los datos del contexto para números; si no sabés decilo". 
**Rationale:** Evita alucinaciones numéricas. Reutiliza lógica probada.
**Alternativas:** Pasar solo consulta (peligroso), incluir too much (ruido).

### D8: Dataset entrenado con frases de tests + variantes
**Decisión:** Incluir explícitamente las frases usadas en tests existentes (para asegurar matching) + sinónimos/variantes comunes rioplatenses. Generar dataset pequeño pero representativo.
**Rationale:** Maximiza compatibilidad con casos existentes y mejora cobertura.
**Alternativas:** Dataset gigante (overkill, sin beneficio).

## Risks / Trade-offs

- **[Riesgo: Regresión silenciosa]** → Mitigación: mantener `deterministic` path intacto; correr 316+110 existentes; tests nuevos verifican modo deterministic conserva comportamiento. 
- **[Riesgo: scikit-learn peso/tiempos]** → Mitigación: entrenamiento lazy + cache (joblib) en memoria; modelo pequeño. Primera predicción puede tardar un poco (entrenamiento), subsiguientes instantáneas.
- **[Riesgo: Umbral mal elegido]** → Mitigación: configurable via env; default conservador; tests cubren < threshold → no-entendido.
- **[Riesgo: Ollama accidentalmente "activado"]** → Mitigación: default `classifier`, flag explícito `ollama`. Documentado como opcional. Nunca usado en CI/tests.
- **[Riesgo: Dataset incompleto para nuevos casos]** → Mitigación: fallback a `no-entendido` cuando confianza baja. Fácil de extender dataset sin tocar lógica.
- **[Trade-off: Mantenemos matcher + ML]** → Más robusto (best of both). Código un poco más complejo, pero justificado por "no romper nada".
- **[Trade-off: joblib artifacts]** → Pequeño archivo binario versionado con código (entrenable desde dataset) o generado lazy. Evitar binarios gigantes.

## Migration Plan

No migración de datos. Cambios aditivos:
1. Agregar deps: `scikit-learn` a `backend/requirements.txt`.
2. Crear módulo NLU + dataset + cliente Ollama (nuevos archivos).
3. Wiring en `admin_bot_service.py` con selección de cerebro (manteniendo handlers existentes).
4. Config vars en `backend/src/core/config.py` (pattern por llamada).
5. `.env.example` con nuevas vars.
6. `README.md` sección Ollama.
7. Tareas limpieza archivos basura + `.gitignore`.

Rollback: volver a usar `ADMIN_BOT_BRAIN=deterministic` (o revert commit) — comportamiento vuelve a puro matcher.

## Open Questions

- **Umbral exacto:** ¿0.55 o 0.6? Sugerido 0.55 inicialmente; ajustar si tests muestran falsos positivos.
- **Persistencia modelo:** ¿guardar `.joblib` generado en `backend/src/services/admin_bot/models/` (ignorado si muy grande?) o entrenar en memoria en cada arranque? Lazy + cached in module singleton.
- **Dataset ubicación:** `backend/src/services/admin_bot/nlu/dataset.json` (pequeño, versionado). 
- **Manejo Ollama en modo ollama:** ¿usar Ollama para clasificar intención Y generar respuesta? O solo generar respuesta con intención inferida? Diseño propone: Ollama brain puede intentar responder usando contexto; si falla comprensión → fallback.
- **Sincronizar spec con código existente:** Ya confirmados `ventas-hoy` y `ticket-cliente` presentes. Incluir en delta spec.

Todos resueltos con decisiones anteriores.