# Tasks: v1-telegram-integration

## 1. Idempotency + Api-Key validation in backend

- [x] 1.1 Add `idempotency_key` column (unique, nullable) to interactions table via Alembic migration 0004
- [x] 1.2 Add `api_key` config via env var (`API_KEY`) and FastAPI dependency to validate `X-Api-Key` header
- [x] 1.3 Add idempotency check in InteractionService: if `X-Idempotency-Key` already exists → raise 409 Conflict
- [x] 1.4 Return 201 on first request with idempotency key, 409 on subsequent with same key
- [x] 1.5 Update Interaction schema to accept idempotency_key as optional field (via header, not body — schema left unchanged intentionally)

## 2. Tests

- [x] 2.1 Test: POST with X-Idempotency-Key returns 201 first time, 409 second time
- [x] 2.2 Test: POST without X-Api-Key returns 401/403
- [x] 2.3 Test: POST with invalid X-Api-Key returns 401/403

## 3. n8n flow example

- [x] 3.1 Create Docs/telegram-n8n-flow.json with n8n webhook flow that maps Telegram update to POST /api/v1/interactions
- [x] 3.2 Document field mapping: message_id → X-Idempotency-Key, from.id → user, text → payload.text, source → "telegram"

## 4. Developer setup docs

- [x] 4.1 Create Docs/telegram-dev-setup.md with ngrok + Telegram webhook configuration steps
- [x] 4.2 Document .env configuration (API_KEY) and how to run locally
