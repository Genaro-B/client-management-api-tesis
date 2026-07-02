# n8n → API: Interaction History Webhook

## How to configure an n8n Webhook node

1. Add a **Webhook** node to your workflow.
2. Set **HTTP Method** to `POST`.
3. Set **Path** (or full URL) to `https://<your-host>/api/v1/interactions/`.
4. In the **Response** tab set **Response Mode** to `Last Node`.
5. In the **JSON Output** of the webhook, structure the body as shown below.

## Payload format

```json
{
  "source": "n8n",
  "payload": "{\"event\": \"order.created\", \"orderId\": 123}",
  "user": "optional-user-or-bot-id",
  "intent": "order_creation",
  "result": "processed",
  "clientLookup": {
    "email": "cliente@example.com"
  }
}
```

### Field reference

| Field          | Required | Description                                      |
|----------------|----------|--------------------------------------------------|
| `source`       | ✅ Yes   | Must be one of: `telegram`, `webhook`, `n8n`, `api`, `system` |
| `payload`      | ✅ Yes   | Raw payload as a **JSON string** (not an object) |
| `user`         | ❌ No    | Identifier of the user/bot that triggered it     |
| `intent`       | ❌ No    | Optional NLP intent classification               |
| `result`       | ❌ No    | Processing result or status                      |
| `clientLookup` | ❌ No    | Object with `email` or `telefono` to link to a client |

## Example curl

```bash
curl -X POST http://localhost:8000/api/v1/interactions/ \
  -H "Content-Type: application/json" \
  -d '{
    "source": "n8n",
    "payload": "{\"event\": \"user.created\", \"userId\": 456}",
    "user": "n8n-workflow-orders",
    "intent": "user_creation",
    "clientLookup": {
      "email": "cliente@example.com"
    }
  }'
```

**Successful response** (201):

```json
{
  "id": 42,
  "timestamp": "2026-06-24T19:30:00Z"
}
```

## n8n expression to build the payload

In your n8n Webhook node response, use this expression to stringify the `payload` field:

```javascript
// Use JSON.stringify for the payload field to ensure it's a string
{
  "source": "n8n",
  "payload": JSON.stringify($json.eventData),
  "user": $json.userId || "",
  "clientLookup": {
    "email": $json.customerEmail
  }
}
```

### Tips

- The `payload` field **must be a string**, not a JSON object.
- If the client is not found by `email` or `telefono`, the interaction is still saved — `clientId` will be `null`.
- Validation errors return **400** with a descriptive message.
