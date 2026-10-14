# customer-registration Specification

## Purpose
TBD - created by archiving change v5-ventas-tickets. Update Purpose after archive.
## Requirements
### Requirement: Registro único de prospecto desde el bot (sin login)

El sistema SHALL exponer `POST /api/v1/clients/register-bot` protegido con `X-API-Key` que reciba `{telegram_user_id, nombre, apellido, telefono}` y cree O vincule un `Client` con `password_hash = NULL`, `role = "user"`, `activo = true`.

- El registro SHALL ser de UNA sola vez y idempotente: si el `telegram_user_id` ya está vinculado, el endpoint SHALL devolver el cliente existente (status 200) sin crear otro.
- El contrato NO incluye contraseña ni email del usuario: el prospecto NUNCA inicia sesión.
- El contrato de nombre/apellido: el flujo n8n pregunta "nombre y apellido" y separa en el primer espacio; si hay una sola palabra, `apellido` se envía como string vacío (columna `NOT NULL` lo admite).

#### Scenario: Registro nuevo
- **WHEN** el bot envía `register-bot` con un `telegram_user_id` inexistente
- **THEN** se crea un `Client` con `password_hash = null`, los datos enviados y el `telegram_user_id` seteado
- **THEN** la respuesta tiene status 201 con el cliente

#### Scenario: Segundo registro no duplica
- **WHEN** el bot envía `register-bot` dos veces con el mismo `telegram_user_id`
- **THEN** existe un único `Client` y la segunda respuesta devuelve el mismo cliente con status 200

#### Scenario: Cliente creado antes del cambio se vincula por teléfono
- **WHEN** ya existe un `Client` sin `telegram_user_id` cuyo `telefono` coincide con el enviado
- **THEN** el endpoint setea `telegram_user_id` en ese cliente existente en lugar de crear uno nuevo

#### Scenario: Sin API-Key
- **WHEN** se llama el endpoint sin header `X-API-Key`
- **THEN** la respuesta tiene status 401

### Requirement: Email placeholder para prospectos de Telegram

El registro SHALL generar `email = "tg{telegram_user_id}@telegram.local"` para cumplir el `NOT NULL + UNIQUE` existente de `Client.email`, sin migrar la columna.

- El dominio generado SHALL ser `.local` para poder identificar/filtrar los emails sintéticos (el panel los mostrará como "sin email" cuando corresponda).
- El sistema NO SHALL pedir ni aceptar email del prospecto en este flujo.

#### Scenario: Email sintético único
- **WHEN** se registra el prospecto con `telegram_user_id = "12345"`
- **THEN** el cliente queda con `email = "tg12345@telegram.local"` y pasa la restricción de unicidad

#### Scenario: Dos prospectos no colisionan en el índice unique
- **WHEN** se registran dos prospectos con distinto `telegram_user_id`
- **THEN** ambos emails generados son distintos y ambos INSERTs son válidos

### Requirement: Identidad durable `telegram_user_id`

El sistema SHALL persistir `telegram_user_id` (string, nullable, unique e indexado) en la tabla `clients` vía migración Alembic, como identidad primaria del bot. Los clientes existentes quedarán con `NULL` hasta ser vinculados.

#### Scenario: Migración sobre base con datos
- **WHEN** se aplica la migración `0008` sobre un `dev.db` que ya tiene clientes, productos e interacciones
- **THEN** la columna nueva existe con todos los registros previos en `NULL` y ningún dato existente se modifica

#### Scenario: Unicidad de la columna
- **WHEN** se intenta persistir dos clientes con el mismo `telegram_user_id`
- **THEN** la restricción unique de la base lo rechaza

