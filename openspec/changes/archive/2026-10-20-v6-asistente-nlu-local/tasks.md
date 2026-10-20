## 1. Configuración base (deps + config + .env.example)

- [x] 1.1 **Agregar dependencia scikit-learn** en `backend/requirements.txt`. Verificar no romper formato existente.
- [x] 1.2 **Extender config con vars de NLU/cerebros** en `backend/src/core/config.py` siguiendo patrón por llamada (tipo `get_bcrypt_rounds()`). Añadir: `ADMIN_BOT_BRAIN` (default `classifier`), `ADMIN_BOT_NLU_THRESHOLD` (default `0.55`), `OLLAMA_URL` (default `http://localhost:11434`), `OLLAMA_MODEL` (default `qwen2.5:3b`), `OLLAMA_TIMEOUT_SECONDS` (default `30`). Documentar comportamiento.
- [x] 1.3 **Crear `.env.example`** en raíz con todas las vars nuevas comentadas + descripción breve (en español rioplatense). Incluir sección "Asistente administrativo" clara.
- [x] 1.4 **Verificación safety-net**: correr tests existentes (`cd backend; ..\.venv\Scripts\python.exe run_tests.py`) para confirmar línea base 316 passing. Capturar resultado.

## 2. NLU local: dataset + clasificador + tests unitarios (TDD)

- [x] 2.1 **Crear dataset NLU** en `backend/src/services/admin_bot/nlu/dataset.json` con intents: `clientes-nuevos-mes`, `stock-bajo`, `interacciones-hoy`, `producto-top`, `metricas-generales`, `ventas-hoy`, `ticket-cliente`, `no-entendido` (mínimo 15-20 frases cada uno). Incluir frases exactas de tests existentes + sinónimos + variaciones + typos leves.
- [x] 2.2 **Crear módulo clasificador** `backend/src/services/admin_bot/nlu/classifier.py` con: carga dataset, vectorización TF-IDF (word + char n-grams), entrenamiento lazy, cache en memoria (singleton), predicción con `predict_proba` + umbral, método `classify(text, threshold)` retornando `(intent, confidence)`. Soportar persistencia opcional con joblib (lazy save/load) sin romper si no existe.
- [x] 2.3 **Tests unitarios clasificador** `backend/tests/test_admin_bot_nlu_classifier.py` (TDD): (a) clasifica frase no vista pero semánticamente cercana; (b) confianza < umbral retorna comportamiento acorde; (c) incluye variantes de intents existentes; (d) maneja texto vacío con gracia. Correr y hacer pasar.
- [x] 2.4 **Validar** que cambios hasta acá no afectan router/service existentes: `cd backend; ..\.venv\Scripts\python.exe run_tests.py` (316 passing + nuevos verdes).

## 3. Cascada de cerebros + wiring en servicio (preservar determinismo)

- [x] 3.1 **Agregar helpers config al servicio**: usar funciones de config por llamada para leer `ADMIN_BOT_BRAIN`/threshold.
- [x] 3.2 **Modificar `AdminBotService.respond()`** para implementar cascada: (1) normalizar texto; (2) si `brain == 'deterministic'`: usar **únicamente** router determinístico (comportamiento idéntico); (3) si `brain == 'classifier'` (default): router primero → si `no-entendido` llamar clasificador con threshold → si aún `no-entendido` (o conf < umbral) retornar `no-entendido`; (4) si `brain == 'ollama'`: intentar Ollama (cuando implementado) con fallback al deterministic/`no-entendido`. **NO** cambiar handlers existentes.
- [x] 3.3 **Tests para modo deterministic**: asegurar que con `ADMIN_BOT_BRAIN=deterministic`, todos los tests existentes de admin-bot siguen comportándose igual. Ejecutar `cd backend; ..\.venv\Scripts\python.exe run_tests.py` → 316 passing.
- [x] 3.4 **Tests para cascada classifier**: añadir casos en `backend/tests/test_admin_bot_nlu_classifier_integration.py` (o extender existentes) probando: frase que matcher hoy manda a `no-entendido` es clasificada por fallback con conf >= threshold; conf < threshold → `no-entendido`. Mockear entorno.
- [x] 3.5 **Verificación**: backend tests verdes (316 + nuevos).

## 4. Capa opcional Ollama (cliente + contexto + tests mockeados)

- [x] 4.1 **Crear builder de contexto** `backend/src/services/admin_bot/ollama/context_builder.py` que reutilice helpers reales: ventas del día (`sale_service.ventas_del_dia`/`ventas_hoy`), ticket por cliente (si consulta menciona ID cliente), stock bajo, resumen métricas. Devolver string estructurado en español.
- [x] 4.2 **Crear cliente Ollama** `backend/src/services/admin_bot/ollama/client.py` con `httpx` (POST `{OLLAMA_URL}/api/chat`, stream:false), timeout configurable, system prompt rioplatense ("usá SOLO datos del contexto para números; si no sabés decilo"), manejo `httpx.ConnectError`, `httpx.TimeoutException`, `httpx.HTTPStatusError`. Retornar contenido o lanzar excepción controlada.
- [x] 4.3 **Integrar Ollama en servicio** (solo si `brain == 'ollama'`): construir contexto → llamar cliente → parsear respuesta a `{intent, respuesta}` o fallback a `no-entendido`/deterministic ante error. Nunca romper si Ollama ausente.
- [x] 4.4 **Tests Ollama mockeados** `backend/tests/test_admin_bot_ollama.py`: (a) respuesta exitosa usando contexto; (b) ConnectError → fallback graceful `no-entendido`; (c) Timeout → fallback graceful; (d) respuesta vacía/inesperada → fallback. Usar `unittest.mock.patch` con `httpx.post`.
- [x] 4.5 **Verificación**: backend 316 + nuevos verdes; frontend 110 verdes.

## 5. API/brain selection + wiring fino + tests API

- [x] 5.1 **Asegurar route no cambia contrato**: `backend/src/api/routes/admin_bot.py` mantiene `ConsultRequest`, `ConsultResponse` (`{intent, respuesta}`), auth `get_current_user`, logging con `source="admin-bot"`. Sin cambios a estructura.
- [x] 5.2 **Tests API adicionales** (si necesario) para cubrir modos: `ADMIN_BOT_BRAIN=deterministic` no altera respuestas existentes; modo classifier con fallback funciona end-to-end. Mockear env.
- [x] 5.3 **Verificar integración**: `cd backend; ..\.venv\Scripts\python.exe run_tests.py` → todos verdes (316 + tests nuevos). `cd frontend; npm test` → 110 passing.

## 6. Documentación + limpieza archivos basura + .gitignore

- [x] 6.1 **Actualizar `README.md`**: añadir sección "Asistente administrativo: cómo funciona y cómo activarlo con Ollama" (español rioplatense). Explicar: matcher primero (seguridad), clasificador fallback, `ADMIN_BOT_BRAIN`, umbral, activación Ollama (`ollama pull qwen2.5:3b`, set `ADMIN_BOT_BRAIN=ollama`, verificar `OLLAMA_URL`), que es opcional y deshabilitado por defecto.
- [x] 6.2 **Limpiar archivos basura raíz**: eliminar `backend.log`, `backend.err`, `tmp_botrouter.js` si existen. No modificar otros archivos.
- [x] 6.3 **Verificar/actualizar `.gitignore`** para cubrir `backend.log`, `backend.err`, `tmp_botrouter.js` (y opcionalmente artefactos joblib si se generan localmente). Solo añadir líneas necesarias, sin romper existente.
- [x] 6.4 **Verificación final docs**: revisar enlaces/claridad. No tocar código.

## 7. Verificación integral (crítica "no romper nada")

- [x] 7.1 **Backend completo**: `cd backend; ..\.venv\Scripts\python.exe run_tests.py` → **316 + nuevos tests deben pasar**. Sin failures pre-existentes.
- [x] 7.2 **Frontend completo**: `cd frontend; npm test` → **110 passing** (sin cambios).
- [x] 7.3 **Modo deterministic explícito**: probar con `ADMIN_BOT_BRAIN=deterministic` que comportamiento coincide con baseline (revisar tests críticos). 
- [x] 7.4 **Modo classifier default**: confirmar default es `classifier` y no rompe casos existentes.
- [x] 7.5 **Ollama mockeado**: confirmar tests Ollama no requieren servidor real.
- [x] 7.6 **Smoke test manual rápido** (opcional pero seguro): endpoints admin-bot existentes siguen funcionando con auth.
- [x] 7.7 **Checklist "no romper nada"** completo. All green.

## 8. Mejora post-v6: enriquecimiento de vocabulario NLU (TDD)

- [x] 8.1 **Medir el gap** (baseline): con umbral 0.55, comparar `router.match()` vs `clasificar()` para "cuanto facturamos hoy", "quiero ver los numeros del negocio", "necesito saber la plata que entro hoy", "cuanta guita entro hoy", "cuanto stok queda". Confirmar que caen en `no-entendido` (confianza < umbral o argmax erróneo). Capturado.
- [x] 8.2 **RED**: crear tests fallantes parametrizados en `backend/tests/test_admin_bot_nlu_classifier_vocabulario.py` cubriendo criterios 1-4 (cascada real vía servicio + `clasificar()` a nivel clasificador). Correr → deben fallar (9 fallos).
- [x] 8.3 **GREEN — enriquecer dataset**: agregar familias de sinónimos de vocabulario distinto al matcher en `dataset.json` (ventas-hoy: facturar/plata/guita/ingresos/recaudar/dinero; metricas-generales: números/balance/ganancias/gestión; stock-bajo: stock/inventario + variantes con typo "stok"). ~38 frases nuevas en ventas-hoy, ~15 en metricas-generales, ~10 en stock-bajo. Correr → verde.
- [x] 8.4 **Umbral**: mantener `ADMIN_BOT_NLU_THRESHOLD=0.55` (default documentado). Justificación con datos: todas las frases positivas quedan ≥ 0.70 (mínimo, el typo "quanto stok qeda") y las requeridas ≥ 0.88; las `no-entendido` quedan seguras porque su argmax ES la clase `no-entendido`. No fue necesario tocar `config.py` ni `.env.example`.
- [x] 8.5 **TRIANGULATE**: agregar ≥2 casos extra por comportamiento (paráfrasis reales: "cuanta plata entro hoy", "quiero ver el balance general", "cuanto stock queda"; typos extra: "quanto stok qeda", "cuanto facturamo hoy", "cuanta plata entro oy"; ruido: capital de Francia, receta, 2+2, partido, canción). Correr → verde.
- [x] 8.6 **Criterio 3 (typos)**: "cuanto stok queda" → `stock-bajo` (0.92) resuelto por enriquecimiento, sin crear falsos positivos. Sin limitación pendiente para este caso.
- [x] 8.7 **Criterio 4 (cero falsos positivos)**: las 20 frases `no-entendido` del dataset siguen clasificando como `no-entendido`.
- [x] 8.8 **Verificación final**: `cd backend; ..\.venv\Scripts\python.exe run_tests.py` → **419 passed** (370 baseline + 49 nuevos). `openspec validate v6-asistente-nlu-local --strict` → OK. Sin cambios en router/servicio/config/threshold.