# Design: v2-mejoras-bot-telegram

## Context

The current v1 bot uses a simple n8n webhook flow: receive Telegram message → map fields → POST to API. There's no response to the user, no conversation state, no menus, no command handling. Every inbound message is treated identically.

For v2 we need a conversational bot that:
- Responds to `/start` with a welcome menu
- Guides users through structured flows with buttons
- Tracks conversation state per user across messages
- Handles errors and unknown commands gracefully
- Maintains the existing idempotent logging to the API

All logic runs in n8n — no backend API changes.

## Architecture

```
Telegram
   │
   ▼  (webhook HTTPS)
n8n Telegram Trigger (inbound)
   │
   ├──▶ [0] Command router (Switch)
   │       ├── /start → Welcome handler
   │       └── /unknown → Error handler
   │
   ├──▶ [1] State reader (Function node)
   │       Reads conversation state from n8n static data (keyed by chat_id)
   │
   ├──▶ [2] Flow router (Switch node)
   │       Routes based on current conversation state:
   │       - idle/main_menu → Route by menu option
   │       - comprar/step_X  → Comprar sub-flow
   │       - ver_productos   → Ver productos handler
   │       - consultar_precios → Precios sub-flow
   │       - hablar_asesor   → Asesor sub-flow
   │       - otra_consulta   → Consulta sub-flow
   │
   ├──▶ [3] Sub-flow processors (Function/Switch nodes)
   │       Each sub-flow validates input, builds response,
   │       and transitions state to next step or back to menu
   │
   ├──▶ [4] State writer (Function node)
   │       Persists updated conversation state
   │
   ├──▶ [5] Response sender (Telegram Send node)
   │       Sends reply with appropriate keyboard markup
   │
   └──▶ [6] API logger (HTTP Request node)
       POST /api/v1/interactions/ with idempotency
```

## Conversation State Model

Stored in n8n's `getWorkflowStaticData('global')` as a JSON object keyed by `chat_id`:

```json
{
  "chat_id_12345": {
    "state": "main_menu",
    "flow": null,
    "step": 0,
    "data": {}
  },
  "chat_id_67890": {
    "state": "comprar",
    "flow": "comprar",
    "step": 2,
    "data": {
      "producto": "Widget X",
      "cantidad": null
    }
  }
}
```

### State values

| State | Description | Transitions |
|-------|-------------|-------------|
| `idle` | No active conversation | `/start` → `main_menu` |
| `main_menu` | Awaiting menu selection | Menu option → sub-flow state |
| `comprar` | In "Comprar" flow | Step progression or `cancel` → `main_menu` |
| `ver_productos` | Displaying product info (ephemeral) | Auto → `main_menu` |
| `consultar_precios` | In "Consultar precios" flow | Step progression or `cancel` → `main_menu` |
| `hablar_asesor` | In "Hablar con asesor" flow | Complete or `cancel` → `main_menu` |
| `otra_consulta` | In "Otra consulta" flow | Complete or `cancel` → `main_menu` |

## Decisions

### Decision 1: Reply Keyboard over Inline Keyboard

**Choice**: Reply Keyboard (persistent, visible at bottom of chat).

**Rationale**: Reply Keyboards stay visible until dismissed, guiding the user continuously. Inline Keyboards (below messages) are easy to miss and require tapping tiny buttons. For a first iteration, Reply Keyboard provides a more guided experience. The keyboard is dismissed during multi-step flows (e.g., typing a product name) and re-shown when returning to the main menu.

**Trade-off**: Reply Keyboard takes up screen space. Mitigated by removing it during text input steps.

### Decision 2: State storage via n8n Workflow Static Data

**Choice**: `getWorkflowStaticData('global')` in n8n Function nodes.

**Rationale**: No backend changes required, no external dependencies. Static data persists across executions within the same n8n instance. The data is keyed by `chat_id` to support multiple concurrent users.

**Risk**: Static data is in-memory and may reset on n8n restart. This is acceptable for v2 — lost state means the user returns to the main menu on next message, which is a graceful degradation.

**Alternatives considered**:
- **Backend API state store**: Rejected — requires new endpoint and DB migration, violating "no API changes" constraint.
- **n8n Variable Store**: Enterprise-only feature.
- **Wait + Webhook pattern**: Not suitable for multi-step async conversation.

### Decision 3: Single workflow vs. sub-workflows

**Choice**: Single n8n workflow with Switch nodes for routing.

**Rationale**: A single workflow is simpler to import, understand, and debug. Sub-flows are handled by Switch nodes that route by `state` and `step`. If the workflow grows too large, sub-flows can be extracted into separate n8n workflows later.

### Decision 4: Emoji prefixes on menu options

**Choice**: Include emojis on menu buttons (🛒 Comprar, 📦 Ver productos, etc.).

**Rationale**: Emojis make buttons visually scannable and improve UX without adding complexity. They are rendered natively by Telegram.

## Sub-flow Designs

### Comprar flow

```
User selects "🛒 Comprar"
  → Bot: "¿Qué producto querés comprar?"
  → User replies with product name
  → Bot: "¿Qué cantidad querés?"
  → User replies with quantity
  → Bot: "Perfecto, vamos a procesar tu solicitud de {cantidad} x {producto}. Un asesor te va a contactar."
  → Log interaction with payload { flow: "comprar", producto, cantidad }
  → Return to main menu
```

### Ver productos flow

```
User selects "📦 Ver productos"
  → Bot: "Podés ver nuestro catálogo completo en: [link]. ¿Querés consultar por algún producto en particular?"
  → Keyboard: "Sí, quiero consultar" | "Volver al menú"
  → "Sí" → transition to "Otra consulta" flow
  → "Volver" → main menu
```

### Consultar precios flow

```
User selects "💲 Consultar precios"
  → Bot: "¿Sobre qué producto o categoría querés información de precios?"
  → User replies
  → Bot: "Gracias, vamos a consultar los precios de {producto/categoría} y te vamos a responder a la brevedad."
  → Log interaction with payload { flow: "consultar_precios", consulta }
  → Return to main menu
```

### Hablar con asesor flow

```
User selects "📞 Hablar con asesor"
  → Bot: "Decime en qué podemos ayudarte y un asesor se va a comunicar con vos a la brevedad."
  → User replies with message
  → Bot: "Gracias por tu consulta. Un asesor se va a comunicar con vos pronto."
  → Log interaction with payload { flow: "hablar_asesor", mensaje, requiere_asesor: true }
  → Return to main menu
```

### Otra consulta flow

```
User selects "❓ Otra consulta"
  → Bot: "Contame, ¿en qué puedo ayudarte?"
  → User replies
  → Bot: "Gracias por tu consulta. Te vamos a responder a la brevedad."
  → Log interaction with payload { flow: "otra_consulta", mensaje }
  → Return to main menu
```

## Keyboard Layouts

### Main Menu Keyboard (ReplyKeyboardMarkup)

```
┌──────────────────────┬──────────────────────┐
│ 🛒 Comprar           │ 📦 Ver productos     │
├──────────────────────┼──────────────────────┤
│ 💲 Consultar precios  │ 📞 Hablar con asesor │
├──────────────────────┼──────────────────────┤
│ ❓ Otra consulta      │                      │
└──────────────────────┴──────────────────────┘
```

### During multi-step flows

- Reply Keyboard removed (no buttons) so user can type freely
- Flow continues via text input validation

### Cancel / Back keyboard (when expecting optional actions)

```
┌──────────────────────────┐
│ ❌ Cancelar              │
└──────────────────────────┘
```

## n8n Node Configuration

### Telegram Trigger node
- **Type**: Telegram Trigger (n8n node, not webhook)
- **Credential**: Bot token from @BotFather
- **Updates**: `message`, `callback_query` (future use)

### Telegram Send node
- **Type**: Telegram Send
- **Credential**: Same bot token
- **Uses**: sendMessage with `reply_markup` for ReplyKeyboardMarkup

### Function nodes (state management)

State reader (inbound):
```javascript
const staticData = getWorkflowStaticData('global');
const chatId = $input.first().json.message.chat.id;
const state = staticData[chatId] || { state: 'idle', flow: null, step: 0, data: {} };
return [{ json: { ...$input.first().json, conversationState: state } }];
```

State writer (outbound):
```javascript
const staticData = getWorkflowStaticData('global');
const chatId = $input.first().json.message.chat.id;
const newState = $input.first().json.newConversationState;
staticData[chatId] = newState;
return [{ json: { ...$input.first().json } }];
```

## API Logging

Each incoming message SHALL be forwarded to `POST /api/v1/interactions/` with:
- **source**: `"telegram"`
- **user**: Telegram `from.id`
- **payload**: JSON string containing `{ message_id, text, chat_id, date, flow, step, conversation_state }`
- **Headers**: `X-Api-Key` and `X-Idempotency-Key: tg-{message_id}`

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Static data lost on n8n restart | Graceful degradation: users return to main menu on next message, no data loss for completed interactions (already logged to API) |
| Function node errors break the flow | Wrap state reads/writes in try-catch; default to `main_menu` state on error |
| Multiple users simultaneously | State is keyed by chat_id — naturally isolated per user |
| Telegram rate limits on sendMessage | Keep responses concise; n8n handles retries |
| n8n workflow becomes too large | Design Switch nodes with clear separation; extract to sub-workflows later if needed |
