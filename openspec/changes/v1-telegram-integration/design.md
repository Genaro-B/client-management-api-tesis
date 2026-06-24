# Design: v1-telegram-integration

## Mapping (n8n -> API)

- Telegram update fields: message.message_id -> idempotency-key; message.from.id -> user; message.text -> payload.text
- n8n webhook node transforms Telegram JSON into { source: "telegram", user: "<from.id>", payload: { message_id, text, chat_id }, intent: null }

## Headers

- X-Api-Key: required for authentication
- X-Idempotency-Key: use message_id prefixed with "tg-" to ensure unique per chat message

## Retry strategy

- n8n retries on failure with exponential backoff; server returns 409 on duplicate idempotency key

## Security

- Validate X-Api-Key; restrict webhook endpoints to known ngrok host during dev
