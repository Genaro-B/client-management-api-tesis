# frontend-testing Specification

## Purpose
TBD - created by archiving change v5-tests-frontend. Update Purpose after archive.

## Requirements

### Requirement: Suite de tests del frontend con Vitest y React Testing Library

El frontend SHALL contar con una suite de tests automatizados basada en Vitest + React Testing Library corriendo en entorno jsdom.
- El proyecto SHALL tener Vitest 2.x configurado en `frontend/vite.config.js` (o `vitest.config.js`) con `environment: 'jsdom'` y `globals: true`.
- El proyecto SHALL tener un setup de tests que importe `@testing-library/jest-dom`, provea un mock de `matchMedia` (jsdom no lo implementa nativamente) y limpie `localStorage`/`sessionStorage` entre tests.
- El `package.json` SHALL incluir los scripts `test` (ejecución única) y `test:watch` (modo watch).
- Los tests SHALL correr sin backend activo: las llamadas a servicios axios MUST estar mockeadas y no realizar requests de red reales.

#### Scenario: La suite corre en entorno jsdom
- **WHEN** se ejecuta `npm test` desde `frontend/`
- **THEN** la suite corre íntegramente en entorno jsdom
- **AND** el resultado es todos los tests en verde

#### Scenario: Los servicios están aislados del backend
- **WHEN** se ejecuta un test de un servicio (p. ej. `authService`)
- **THEN** axios está mockeado y no se realiza ninguna llamada HTTP real
- **AND** el test verifica el endpoint y los argumentos esperados

### Requirement: Cobertura mínima de áreas de la aplicación

La suite SHALL cubrir al menos las siguientes áreas del frontend: hooks, servicios, 5+ componentes, el contexto de autenticación o una página.
- La suite SHALL incluir tests del hook `useTheme` (lectura de `localStorage`, preferencia del sistema vía `matchMedia`, toggle y persistencia).
- La suite SHALL incluir tests del servicio `authService` (login contra `/api/v1/auth/login` y helpers de `sessionStorage`).
- La suite SHALL incluir tests de al menos 5 componentes, incluyendo `Pagination`, `StatusBadge`, `Avatar`, `Modal` y `ThemeToggle`.
- La suite SHALL incluir tests de `AuthContext` (login exitoso, login con error, logout y restauración de sesión desde storage) o de la página `LoginPage`.
- Los tests de componentes y páginas SHALL ser de valor real (interacción, render condicional, props) y NO triviales (evitar aserciones tautológicas).

#### Scenario: Los hooks se testean con storage y matchMedia mockeados
- **WHEN** `useTheme` se monta con `localStorage` conteniendo `crm_theme = "dark"`
- **THEN** el estado inicial es `dark = true`
- **AND** al hacer toggle el estado cambia a `light` y se persiste en `localStorage`
- **AND** el documento deja de tener la clase `dark` en `<html>`

#### Scenario: Modal responde a eventos de cierre
- **WHEN** el modal está abierto y el usuario presiona `Escape` o hace clic en el backdrop o en el botón de cierre
- **THEN** se invoca el callback `onClose`

### Requirement: Documentación de la suite en README

El README SHALL documentar la suite de tests del frontend.
- La fila "Tests Frontend" de "Próximas Implementaciones" SHALL pasar de ⏳ Pendiente a ✅ Implementado.
- La sección `## 🧪 Tests` SHALL incluir una subsección de frontend con una tabla de cobertura (nombre de archivo, cantidad de tests, qué cubre) y el comando para correrlos, siguiendo el estilo de la tabla del backend.

#### Scenario: La fila de Tests Frontend figura como implementada
- **WHEN** se lee "Próximas Implementaciones" en el README
- **THEN** la fila "Tests Frontend" tiene estado ✅ Implementado con descripción de la suite

#### Scenario: La tabla de cobertura documenta los archivos de test
- **WHEN** se lee la subsección "Tests Frontend" de `## 🧪 Tests`
- **THEN** aparece una tabla con cada archivo de test, la cantidad de tests y qué cubre
- **AND** figura el comando `npm test` para ejecutarlos