# Tasks: v1-telegram-integration

1. Create n8n flow example
   - Acceptance: n8n JSON export mapping Telegram webhook to POST /api/v1/interactions
   - Verify: Import into n8n and run with sample Telegram update

2. Provide ngrok dev instructions
   - Acceptance: README with steps to run ngrok and configure Telegram webhook to ngrok URL

3. Implement header handling and idempotency spec in API
   - Acceptance: API must accept X-Api-Key and X-Idempotency-Key and respond 409 on duplicates
   - Verify: curl with same idempotency key twice should yield first 201 then 409

4. Security considerations and tests
   - Acceptance: documented threats and mitigations
