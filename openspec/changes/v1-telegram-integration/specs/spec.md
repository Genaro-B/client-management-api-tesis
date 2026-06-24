# Spec: telegram-integration

## Scenarios

1) Forward Telegram update to interactions
   - Given a Telegram update received by n8n
   - When mapped and POSTed to /api/v1/interactions with X-Api-Key and X-Idempotency-Key
   - Then server returns 201 and stores interaction

2) Idempotency
   - Given same X-Idempotency-Key sent twice
   - Then first request 201, second request 409 and no duplicate record
