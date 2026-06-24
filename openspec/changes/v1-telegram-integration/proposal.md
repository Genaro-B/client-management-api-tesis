# Proposal: v1-telegram-integration

## Intent

Integrate Telegram inbound messages via n8n to the API using a webhook receiver. Provide developer flow using ngrok for local testing and idempotency guarantees to avoid duplicate processing.

## Scope

### In Scope
- n8n flow examples mapping Telegram webhook to POST /api/v1/interactions
- Developer instructions using ngrok and X-Api-Key, X-Idempotency-Key headers
- Security and retry strategy design

### Out of Scope
- Full production-grade Telegram bot implementation (hooks for messaging responses)

## Capabilities

### New Capabilities
- `telegram-integration`: docs and infra for connecting Telegram -> n8n -> API

## Approach

Use n8n webhook node to receive Telegram updates, map fields to our interaction schema, set X-Idempotency-Key to update ID or message_id, forward to POST /api/v1/interactions with X-Api-Key for auth. Use ngrok for local dev.

## Success Criteria

- [ ] Developer can receive Telegram messages locally and persist via /api/v1/interactions
- [ ] Idempotency prevents duplicate storage on retries
