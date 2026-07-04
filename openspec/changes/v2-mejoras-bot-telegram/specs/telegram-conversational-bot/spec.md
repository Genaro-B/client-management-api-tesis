# Spec: telegram-conversational-bot

## ADDED Requirements

### Requirement: /start command handler

The bot SHALL respond to the `/start` command with a welcome message and display the main menu as a Reply Keyboard.

#### Scenario: User sends /start for the first time
- **WHEN** user sends `/start`
- **THEN** bot replies with a welcome message (greeting, brief intro, what the bot can do) AND shows the main menu keyboard with the available options

#### Scenario: User sends /start after an active conversation
- **WHEN** user sends `/start` while in the middle of a conversation flow
- **THEN** bot resets the conversation state AND shows the welcome message with the main menu

### Requirement: Main menu with Reply Keyboard

The bot SHALL display a Reply Keyboard with the following options: 🛒 Comprar, 📦 Ver productos, 💲 Consultar precios, 📞 Hablar con asesor, ❓ Otra consulta.

#### Scenario: Main menu is displayed after /start
- **WHEN** user completes `/start` or selects "Volver al menú"
- **THEN** bot shows the Reply Keyboard with all 5 menu options

#### Scenario: User sends text that does not match any menu option
- **WHEN** user sends free text instead of selecting a menu option
- **THEN** bot replies with a friendly error message explaining the available options AND re-shows the main menu

### Requirement: Conversation flow for each menu option

Each menu option SHALL trigger a specific conversational sub-flow that collects information and provides the appropriate response.

#### Scenario: User selects "Comprar"
- **WHEN** user selects "🛒 Comprar"
- **THEN** bot asks what product they want to buy, collects the product name, asks for quantity, confirms the request, and logs the interaction to the API

#### Scenario: User selects "Ver productos"
- **WHEN** user selects "📦 Ver productos"
- **THEN** bot replies with a message explaining how to view available products (e.g., "Visitá nuestro catálogo en línea: [link]") AND shows the main menu again

#### Scenario: User selects "Consultar precios"
- **WHEN** user selects "💲 Consultar precios"
- **THEN** bot asks which product or category they want pricing for, collects the query, logs it, and replies with info about how to get pricing

#### Scenario: User selects "Hablar con asesor"
- **WHEN** user selects "📞 Hablar con asesor"
- **THEN** bot collects the user's query, logs the interaction with a special "asesor" flag, and replies that an asesor will contact them soon

#### Scenario: User selects "Otra consulta"
- **WHEN** user selects "❓ Otra consulta"
- **THEN** bot asks the user to describe their question, logs the free-text input, and replies that they'll receive a response soon

### Requirement: Back and Cancel navigation

The bot SHALL provide "Volver al menú" and "Cancelar" options during multi-step flows to let users bail out or restart.

#### Scenario: User selects "Cancelar" during a flow
- **WHEN** user selects "Cancelar" at any step of a sub-flow
- **THEN** bot replies with a confirmation message AND shows the main menu

#### Scenario: User selects "Volver al menú" after completing a flow
- **WHEN** user completes a sub-flow (e.g., finishes the "Comprar" flow)
- **THEN** bot shows a confirmation AND returns to the main menu

### Requirement: Unknown command handling

The bot SHALL handle unrecognized commands gracefully without crashing.

#### Scenario: User sends an unknown command
- **WHEN** user sends an unknown command like `/foo`
- **THEN** bot replies with a friendly message saying the command is not recognized AND shows the main menu

#### Scenario: User sends gibberish text
- **WHEN** user sends random text that does not match a menu option or flow step
- **THEN** bot replies with a friendly message asking them to use the menu options AND re-shows the main menu

### Requirement: Conversation state tracking

The bot SHALL maintain conversation state per user (chat_id) to track the current flow step and selected option across messages.

#### Scenario: State is preserved across messages in a flow
- **WHEN** user selects "🛒 Comprar" (step 1: ask product)
- **AND** user replies with a product name (step 2: ask quantity)
- **THEN** bot remembers they are in the "Comprar" flow and correctly advances to the next step

#### Scenario: State resets when flow completes
- **WHEN** user completes a sub-flow
- **THEN** conversation state resets to "main_menu" for that user

#### Scenario: State resets on /start
- **WHEN** user sends `/start`
- **THEN** any existing conversation state is cleared and reset to idle

### Requirement: Log interactions to API

All user interactions SHALL be forwarded to the backend API (POST /api/v1/interactions/) with idempotency, preserving the existing v1 integration behavior.

#### Scenario: Message from conversational flow is logged
- **WHEN** user sends a message during any conversational flow step
- **THEN** the message is sent to POST /api/v1/interactions/ with source "telegram", the user id, and the payload containing the flow context (current_step, selected_option, message_text)

#### Scenario: Idempotency is maintained
- **WHEN** the same message_id is sent twice (n8n retry)
- **THEN** the API returns 409 and no duplicate is stored
