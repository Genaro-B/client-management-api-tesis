# Proposal: v2-mejoras-bot-telegram

## Why

The current Telegram integration (v1) receives messages and stores them via the API, but it has no conversational flow — users type raw text, get a canned response, and there's no guidance or structure. The bot feels impersonal and confusing for new users. This change transforms the bot from a simple message forwarder into a guided conversational experience with menus, buttons, and structured flows, making it usable for real clients without AI.

## What Changes

- Add `/start` command handler with welcome message and main menu
- Add Reply Keyboard with structured options (Comprar, Ver productos, Consultar precios, Hablar con asesor, Otra consulta)
- Implement conversation flow: menu → selection → response → back to menu
- Add Back to Menu and Cancel buttons throughout the flow
- Add error handling for unknown commands and unexpected input
- Add conversation state tracking (current step, selected option) to manage multi-step flows
- Update n8n Telegram Send node configuration to support reply keyboards and outbound responses
- Update developer setup docs with the new flow architecture

**No changes to the backend API** — all conversational logic lives in n8n.

## Capabilities

### New Capabilities
- `telegram-conversational-bot`: conversational flow with menus, buttons, state management, and structured responses in n8n for the Telegram bot

### Modified Capabilities
- _None_ — the existing `telegram-integration` capability is purely about message ingestion and remains unchanged

## Impact

- **n8n**: New or significantly modified workflow replacing the simple trigger→store flow with a stateful conversational flow. Requires n8n Telegram Send node configured with a bot token for outbound responses.
- **Docs**: Update `Docs/telegram-n8n-flow.md` with the new flow architecture, conversation state design, and button/command handling. Update `Docs/telegram-dev-setup.md` with Telegram bot token configuration for sending messages.
- **API Backend**: No changes — the backend already stores interactions correctly.
