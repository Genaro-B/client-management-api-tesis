# Tasks: v2-mejoras-bot-telegram

## 1. Setup — Bot token and Telegram Send node

- [ ] 1.1 Create a new Telegram bot via @BotFather (or use existing) and obtain the bot token
- [ ] 1.2 Configure the bot token as an environment variable in n8n (`TELEGRAM_BOT_TOKEN`)
- [ ] 1.3 Configure the existing API_URL and API_KEY env vars if not already set
- [ ] 1.4 Verify Telegram Send node works by sending a test message to the bot chat

## 2. Conversation state management

- [x] 2.1 Create a Function node "Read Conversation State" that reads `getWorkflowStaticData('global')` keyed by `chat_id` and attaches `conversationState` to the execution data
- [x] 2.2 Create a Function node "Write Conversation State" that persists the updated state object to static data
- [x] 2.3 Define the default state shape: `{ state: "idle", flow: null, step: 0, data: {} }`
- [x] 2.4 Add error handling in both state nodes: default to `main_menu` state on read errors

## 3. /start command and welcome flow

- [x] 3.1 Add a Switch node "Command Router" that checks if message text starts with `/`
- [x] 3.2 Route `/start` to a welcome handler: build welcome text with greeting and bot description
- [x] 3.3 Build the main menu Reply Keyboard markup (2×2 grid with 5th option centered below)
- [x] 3.4 Configure Telegram Send node to send welcome message with the main menu keyboard
- [x] 3.5 Set conversation state to `main_menu` after `/start`
- [x] 3.6 Route unknown commands (e.g., `/foo`) to an error handler that shows "comando no reconocido" + main menu

## 4. Main menu routing

- [x] 4.1 Add a Switch node "Flow Router" that routes by `conversationState.state`
- [x] 4.2 Create routes for each menu option: `comprar`, `ver_productos`, `consultar_precios`, `hablar_asesor`, `otra_consulta`
- [x] 4.3 Route any message that doesn't match a flow option to an "unknown input" handler that re-shows the main menu
- [x] 4.4 Route "Cancelar" text (from any state) to reset to `main_menu`

## 5. Comprar sub-flow

- [x] 5.1 Step 1: Ask "¿Qué producto querés comprar?" — remove keyboard for text input, set state to `comprar/step1`
- [x] 5.2 Step 2: Receive product name → validate non-empty → ask "¿Qué cantidad querés?" → set state to `comprar/step2`, store producto in state.data
- [x] 5.3 Step 3: Receive quantity → validate positive number → build confirmation message → log to API with flow context → return to main menu
- [x] 5.4 Add validation: if user sends unexpected input, re-ask the current question (max 3 retries)
- [x] 5.5 Show "Cancelar" button during text input steps

## 6. Ver productos sub-flow

- [x] 6.1 Send product catalog info with link
- [x] 6.2 Offer inline actions: "Sí, quiero consultar" (→ otra_consulta) or "Volver al menú" (→ main_menu)
- [x] 6.3 Log interaction with flow context

## 7. Consultar precios sub-flow

- [x] 7.1 Step 1: Ask "¿Sobre qué producto o categoría querés información de precios?" — remove keyboard
- [x] 7.2 Step 2: Receive query → validate non-empty → build response → log to API → return to main menu
- [x] 7.3 Show "Cancelar" button during text input

## 8. Hablar con asesor sub-flow

- [x] 8.1 Step 1: Ask "Decime en qué podemos ayudarte" — remove keyboard
- [x] 8.2 Step 2: Receive message → build response → log to API with `requiere_asesor: true` flag → return to main menu
- [x] 8.3 Show "Cancelar" button during text input

## 9. Otra consulta sub-flow

- [x] 9.1 Step 1: Ask "Contame, ¿en qué puedo ayudarte?" — remove keyboard
- [x] 9.2 Step 2: Receive message → build response → log to API → return to main menu
- [x] 9.3 Show "Cancelar" button during text input

## 10. API logging integration

- [x] 10.1 Ensure every incoming message (regardless of flow) is forwarded to POST /api/v1/interactions/ via HTTP Request node
- [x] 10.2 Include flow context in payload: `{ flow, step, conversation_state }` alongside message data
- [x] 10.3 Maintain idempotency: X-Idempotency-Key = `tg-{message_id}`
- [x] 10.4 Add error handling: if API logging fails, continue the conversation flow (non-blocking)

## 11. Documentation

- [ ] 11.1 Update `Docs/telegram-n8n-flow.md` with the new conversational flow architecture: state machine diagram, sub-flow descriptions, keyboard layouts
- [ ] 11.2 Update `Docs/telegram-dev-setup.md` with Telegram bot token configuration for send operations
- [x] 11.3 Create `Docs/flujos/Actual/v2-flujo-mejorado.json` with the complete n8n workflow export
- [ ] 11.4 Document keyboard markup JSON structure (ReplyKeyboardMarkup) for future modifications

## 12. Testing and verification

- [ ] 12.1 Test /start command: verify welcome message and main menu keyboard appear
- [ ] 12.2 Test each menu option end-to-end: select option → follow sub-flow → return to menu
- [ ] 12.3 Test Cancel button during each sub-flow: verify return to main menu
- [ ] 12.4 Test unknown commands: verify friendly error message + main menu
- [ ] 12.5 Test state persistence: start a flow, send an unrelated message, verify the flow resumes correctly
- [ ] 12.6 Test multiple concurrent users: send messages from two different chats, verify isolated state
- [ ] 12.7 Verify all interactions are logged to the API with correct flow context in payload
- [ ] 12.8 Verify idempotency: same message_id sent twice → 409 logged but conversation continues
