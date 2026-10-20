# admin-bot Specification

## Purpose
TBD - created by archiving change v3-mejoras-interfaz-bot-administrativo. Update Purpose after archive.
## Requirements
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

### Requirement: Endpoint de consulta del asistente

El sistema SHALL exponer `POST /api/v1/admin-bot/consult` que recibe un JSON `{"mensaje": "<texto libre>"}` y devuelve `{"intent": "<intención>", "respuesta": "<texto armado>"}` con status 200.

- La respuesta SHALL construirse con datos reales obtenidos de la base de datos a través de la misma capa de repositories que usan los endpoints existentes.
- El endpoint SHALL registrar cada consulta como una interacción con `source="admin-bot"` y el `intent` detectado.
- Si el `mensaje` está vacío o ausente, el endpoint SHALL responder con status 422.
- El endpoint SHALL exigir un token JWT válido de un usuario con `role="admin"` (dependencia `require_admin`): sin header o con token inválido SHALL responder `401`, y un usuario autenticado con role distinto de `admin` SHALL recibir `403`.

#### Scenario: Consulta de clientes nuevos responde con datos reales
- **WHEN** se envía "¿cuántos clientes nuevos hay este mes?" y existen 3 clientes registrados en el mes actual
- **THEN** la respuesta tiene `intent: "clientes-nuevos-mes"`
- **AND** la respuesta menciona la cantidad real (3)

#### Scenario: Consulta de stock bajo lista productos bajo umbral
- **WHEN** se envía "productos con stock bajo" y existen productos con stock menor o igual al umbral configurado
- **THEN** la respuesta lista nombre y stock de esos productos

#### Scenario: Consulta de interacciones de hoy responde el conteo real
- **WHEN** se envía "cuántas interacciones hubo hoy" y hay 7 interacciones en el día
- **THEN** la respuesta menciona la cantidad real (7)

#### Scenario: Consulta de producto más vendido responde el top
- **WHEN** se envía "cuál es el producto más vendido"
- **THEN** la respuesta indica el/los productos con mayor cantidad total asignada entre todos los clientes

#### Scenario: Consulta de métricas responde resumen
- **WHEN** se envía "cómo vamos" o "dame las métricas"
- **THEN** la respuesta incluye total de clientes, activos, inactivos, interacciones totales, de hoy y de la semana

#### Scenario: Consulta registrada como interacción
- **WHEN** una consulta es procesada exitosamente
- **THEN** se persiste una interacción con `source="admin-bot"` e `intent` detectado

#### Scenario: Texto no entendido sugiere consultas válidas
- **WHEN** se envía texto irreconocible
- **THEN** la respuesta es un mensaje amigable que lista las consultas que el asistente sí entiende

#### Scenario: Usuario con role user recibe 403
- **WHEN** un usuario autenticado con `role="user"` envía `POST /api/v1/admin-bot/consult` con un token válido
- **THEN** responde `403` y no procesa la consulta

### Requirement: Widget de chat flotante

El frontend SHALL mostrar un widget de chat flotante (asistente administrativo) en todas las páginas autenticadas, visible únicamente para usuarios administradores.

- El widget SHALL ser un botón flotante en la esquina inferior derecha que abre y cierra un panel de chat.
- El panel SHALL tener burbujas de mensajes (usuario a la derecha, asistente a la izquierda), campo de texto y botón de envío.
- El widget SHALL ofrecer chips de consultas rápidas: "Clientes nuevos del mes", "Productos con stock bajo", "Interacciones de hoy", "Producto más vendido" y "Resumen de métricas".
- El widget SHALL mostrar un indicador "escribiendo…" mientras espera la respuesta del endpoint.
- El widget SHALL manejar errores de red mostrando un mensaje de error en el chat y permitiendo reintentar.
- El widget SHALL respetar el tema claro/oscuro usando las variables de Tailwind existentes (`bg-card`, `text-foreground`, `text-muted-foreground`, etc.).

#### Scenario: Widget visible solo para administradores
- **WHEN** un usuario administrador navega a cualquier página autenticada
- **THEN** el botón flotante del asistente es visible

#### Scenario: Widget oculto para usuarios estándar
- **WHEN** un usuario estándar navega a cualquier página autenticada
- **THEN** el botón flotante del asistente no es visible

#### Scenario: Conversación con burbujas de mensajes
- **WHEN** el usuario escribe "productos con stock bajo" y envía el mensaje
- **THEN** se agrega una burbuja con la consulta del usuario
- **AND** se muestra "escribiendo…" hasta que llega la respuesta
- **AND** la respuesta del asistente se agrega como burbuja siguiente

#### Scenario: Chip de consulta rápida envía la consulta
- **WHEN** el usuario hace clic en el chip "Interacciones de hoy"
- **THEN** se envía la consulta correspondiente como si la hubiera escrito

#### Scenario: Error de red se muestra en el chat
- **WHEN** el endpoint no responde por un problema de red
- **THEN** se muestra una burbuja de error con un mensaje descriptivo
- **AND** el usuario puede reintentar la consulta

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

