## ADDED Requirements

### Requirement: Clasificador local de intenciones (fallback)

El sistema SHALL disponer de un clasificador local de intenciones (NLU) basado en `scikit-learn` que actúe como **fallback** del matcher determinístico. El clasificador SHALL NO reemplazar el matcher determinístico; solo se invocará cuando el matcher retorne `no-entendido`.

#### Scenario: Matcher falla y clasificador acierta
- **WHEN** el usuario envía una frase que el matcher determinístico NO reconoce (retorna `no-entendido`)
- **AND** el clasificador local predice una intención válida con confianza >= `ADMIN_BOT_NLU_THRESHOLD`
- **THEN** el sistema retorna esa intención

#### Scenario: Confianza por debajo del umbral
- **WHEN** el clasificador local predice una intención con confianza < `ADMIN_BOT_NLU_THRESHOLD`
- **THEN** el sistema retorna `no-entendido`
- **AND** la respuesta indica que no se entendió la consulta (sin invocar LLM externo)

### Requirement: Cascada de resolución de intención y selección de cerebro (ADMIN_BOT_BRAIN)

El sistema SHALL soportar selección de cerebro mediante la variable de entorno `ADMIN_BOT_BRAIN` con valores permitidos `classifier`, `deterministic`, `ollama`. El comportamiento por cascada SHALL preservar la no-regresión del matcher determinístico.

#### Scenario: Modo deterministic preserva comportamiento exacto
- **WHEN** `ADMIN_BOT_BRAIN` es `deterministic`
- **THEN** la resolución de intención utiliza **únicamente** el matcher determinístico existente
- **AND** el comportamiento es idéntico al estado actual (incluyendo las frases que hoy retornan `no-entendido`)

#### Scenario: Modo classifier aplica cascada determinística-primero
- **WHEN** `ADMIN_BOT_BRAIN` es `classifier` (default)
- **THEN** el matcher determinístico se ejecuta **primero**
- **AND** solo si retorna `no-entendido`, se ejecuta el clasificador local
- **AND** si el clasificador retorna confianza < umbral, el resultado es `no-entendido`

#### Scenario: Modo ollama usa LLM con fallback determinístico
- **WHEN** `ADMIN_BOT_BRAIN` es `ollama`
- **THEN** el cerebro Ollama intenta generar/derivar la intención o respuesta
- **AND** ante error o falta de comprensión, el sistema cae de vuelta al matcher determinístico (o a `no-entendido` según corresponda) para garantizar robustez

### Requirement: Capa opcional de LLM local (Ollama) deshabilitada por defecto

El sistema SHALL incluir una implementación opcional para Ollama **deshabilitada por defecto**. Ollama SHALL NOT ser requerido para ejecutar la aplicación ni los tests.

#### Scenario: Ollama no disponible produce fallback graceful
- **WHEN** `ADMIN_BOT_BRAIN` es `ollama`
- **AND** el servicio Ollama no está disponible o responde con timeout
- **THEN** el sistema NO arroja excepción no controlada
- **AND** retorna `no-entendido` (o emplea fallback determinístico) de forma graceful

#### Scenario: Ollama habilitado usa contexto con datos reales
- **WHEN** `ADMIN_BOT_BRAIN` es `ollama`
- **AND** Ollama responde correctamente
- **THEN** la respuesta generada SHALL basarse en contexto compuesto con datos reales del sistema (ventas del día, stock bajo, métricas o ticket según la consulta)
- **AND** si no hay datos para responder, SHALL indicarlo explícitamente (sin inventar números)

### Requirement: Configuración de NLU y cerebros (variables de entorno)

El sistema SHALL soportar variables de entorno para configurar el comportamiento del asistente (lectura por llamada, coherente con el patrón existente): `ADMIN_BOT_BRAIN`, `ADMIN_BOT_NLU_THRESHOLD`, `OLLAMA_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT_SECONDS`. Los valores por defecto SHALL ser razonables y documentados.

#### Scenario: Defaults seguros
- **WHEN** no se definen variables de entorno para el asistente
- **THEN** `ADMIN_BOT_BRAIN` por defecto es `classifier`
- **AND** `ADMIN_BOT_NLU_THRESHOLD` tiene valor por defecto ~0.55
- **AND** `OLLAMA_URL` por defecto es `http://localhost:11434`
- **AND** `OLLAMA_MODEL` por defecto es `qwen2.5:3b`
- **AND** `OLLAMA_TIMEOUT_SECONDS` por defecto es `30`

#### Scenario: Configuración sobreescrita
- **WHEN** se define `ADMIN_BOT_BRAIN=deterministic`
- **THEN** el sistema utiliza únicamente el matcher determinístico
- **AND** cuando se define `ADMIN_BOT_BRAIN=ollama`, el cerebro opcional se activa (solo si está habilitado explícitamente)

## MODIFIED Requirements

### Requirement: Matcher determinístico de intenciones administrativas

El sistema SHALL proveer un router de intenciones administrativas (`AdminIntentRouter`) que clasifique texto libre en español en una intención administrativa usando pattern matching determinístico (palabras clave y expresiones regulares por intención). El matcher determinístico SHALL ser la **primera capa** de una cascada de resolución de intenciones y SHALL NO usar IA ni machine learning. Cuando el matcher retorne `no-entendido`, el sistema SHALL poder invocar un clasificador local (ML) como capa de fallback, según la configuración (`ADMIN_BOT_BRAIN`).

#### Scenario: Clasifica clientes nuevos del mes
- **WHEN** el usuario escribe "¿cuántos clientes nuevos tuvimos este mes?"
- **THEN** el sistema retorna la intención `clientes-nuevos-mes`

#### Scenario: Clasifica stock bajo
- **WHEN** el usuario consulta "¿qué productos tienen stock bajo?"
- **THEN** el sistema retorna la intención `stock-bajo`

#### Scenario: Clasifica interacciones de hoy
- **WHEN** el usuario pregunta "¿cuántas interacciones tuvimos hoy?"
- **THEN** el sistema retorna la intención `interacciones-hoy`

#### Scenario: Clasifica producto top
- **WHEN** el usuario pide "¿cuál fue el producto más vendido?"
- **THEN** el sistema retorna la intención `producto-top`

#### Scenario: Clasifica métricas generales
- **WHEN** el usuario solicita "ver métricas generales"
- **THEN** el sistema retorna la intención `metricas-generales`

#### Scenario: Clasifica ventas de hoy
- **WHEN** el usuario pregunta "¿cuánto vendimos hoy?"
- **THEN** el sistema retorna la intención `ventas-hoy`

#### Scenario: Solicita ticket de cliente
- **WHEN** el usuario escribe "quiero ver el ticket del cliente 5"
- **THEN** el sistema retorna la intención `ticket-cliente`

#### Scenario: Sin coincidencia retorna no-entendido
- **WHEN** ninguna regla coincide con la consulta
- **THEN** el sistema retorna la intención `no-entendido`