## ADDED Requirements

### Requirement: Matcher determinístico de intenciones administrativas

El sistema SHALL proveer un router de intenciones administrativas (`AdminIntentRouter`) que clasifique texto libre en español en una intención administrativa usando pattern matching determinístico (palabras clave y expresiones regulares por intención), sin IA ni machine learning.

- Las intenciones soportadas SHALL ser: `clientes-nuevos-mes`, `stock-bajo`, `interacciones-hoy`, `producto-top`, `metricas-generales` y `no-entendido` (fallback).
- El router SHALL priorizar los patrones por intención en un orden definido y devolver la primera coincidencia.

#### Scenario: Detecta intención de clientes nuevos del mes
- **WHEN** el texto recibido es "¿cuántos clientes nuevos hay este mes?"
- **THEN** la intención detectada es `clientes-nuevos-mes`

#### Scenario: Detecta intención de stock bajo
- **WHEN** el texto recibido es "qué productos tienen stock bajo"
- **THEN** la intención detectada es `stock-bajo`

#### Scenario: Detecta intención de interacciones de hoy
- **WHEN** el texto recibido es "cuántas interacciones hubo hoy"
- **THEN** la intención detectada es `interacciones-hoy`

#### Scenario: Detecta intención de producto más vendido
- **WHEN** el texto recibido es "cuál es el producto más vendido"
- **THEN** la intención detectada es `producto-top`

#### Scenario: Detecta intención de métricas generales
- **WHEN** el texto recibido es "cómo vamos con el negocio"
- **THEN** la intención detectada es `metricas-generales`

#### Scenario: Texto irreconocible cae en fallback
- **WHEN** el texto recibido no coincide con ningún patrón conocido
- **THEN** la intención detectada es `no-entendido`

### Requirement: Endpoint de consulta del asistente

El sistema SHALL exponer `POST /api/v1/admin-bot/consult` que recibe un JSON `{"mensaje": "<texto libre>"}` y devuelve `{"intent": "<intención>", "respuesta": "<texto armado>"}` con status 200.

- La respuesta SHALL construirse con datos reales obtenidos de la base de datos a través de la misma capa de repositories que usan los endpoints existentes.
- El endpoint SHALL registrar cada consulta como una interacción con `source="admin-bot"` y el `intent` detectado.
- Si el `mensaje` está vacío o ausente, el endpoint SHALL responder con status 422.

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