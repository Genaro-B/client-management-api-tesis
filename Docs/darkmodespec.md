# Dark Mode Design Specification

## 1. Objetivo

Este documento define la implementación del modo oscuro para la aplicación web, manteniendo compatibilidad con el Design System existente.

El objetivo es permitir al usuario alternar entre:

* Modo claro (Light Mode)
* Modo oscuro (Dark Mode)

manteniendo consistencia visual en todos los componentes del sistema.

---

# 2. Estrategia de implementación

El sistema debe utilizar variables de tema (Design Tokens) en lugar de modificar estilos individuales.

La aplicación debe manejar dos esquemas:

* Light Theme
* Dark Theme

El cambio de tema debe afectar:

* Fondos
* Textos
* Cards
* Sidebar
* Tablas
* Formularios
* Modales
* Botones
* Estados visuales

---

# 3. Tokens de color

## Light Mode

| Token      | Valor               | Uso                  |
| ---------- | ------------------- | -------------------- |
| Background | #f8fafc             | Fondo general        |
| Card       | #ffffff             | Tarjetas y modales   |
| Foreground | #0f172a             | Texto principal      |
| Muted      | #64748b             | Texto secundario     |
| Border     | rgba(15,23,42,0.08) | Separadores          |
| Primary    | #2563eb             | Acciones principales |
| Error      | #dc2626             | Errores              |

---

## Dark Mode

| Token      | Valor                  | Uso                  |
| ---------- | ---------------------- | -------------------- |
| Background | #020617                | Fondo general        |
| Card       | #0f172a                | Tarjetas y modales   |
| Foreground | #f8fafc                | Texto principal      |
| Muted      | #94a3b8                | Texto secundario     |
| Border     | rgba(255,255,255,0.10) | Separadores          |
| Primary    | #3b82f6                | Acciones principales |
| Error      | #ef4444                | Errores              |

---

# 4. Layout

## Sidebar

### Light

* Fondo oscuro existente:
  #0f172a

* Texto:
  #f8fafc

El sidebar mantiene su apariencia.

### Dark

Debe adaptarse:

* Fondo:
  #020617

* Hover:
  #1e293b

* Item activo:
  #2563eb

---

# 5. Cards

## Light

```css
background: #ffffff;
border: 1px solid rgba(15,23,42,0.08);
```

## Dark

```css
background: #0f172a;
border: 1px solid rgba(255,255,255,0.10);
```

Mantener:

* border-radius 12px
* shadow suave
* padding consistente

---

# 6. Tipografía

Mantener el sistema actual:

| Uso            | Fuente            |
| -------------- | ----------------- |
| Títulos        | Plus Jakarta Sans |
| Texto UI       | Inter             |
| Datos técnicos | DM Mono           |

Cambios:

Dark Mode:

Texto principal:
#f8fafc

Texto secundario:
#94a3b8

---

# 7. Inputs

## Light

* Fondo:
  #ffffff

* Border:
  #e2e8f0

* Texto:
  #0f172a

## Dark

* Fondo:
  #020617

* Border:
  #334155

* Texto:
  #f8fafc

Placeholder:

#64748b

Focus:

Mantener:

* Ring azul
* Border azul
* Transición 150ms

---

# 8. Tabla

## Header

Dark:

```css
background: #020617;
color: #94a3b8;
```

## Filas

Normal:

```css
background:#0f172a;
```

Hover:

```css
background:#1e293b;
```

Mantener:

* DM Mono para IDs
* Estados mediante badges

---

# 9. Badges

## Activo

Light:

* Fondo:
  #ecfdf5

* Texto:
  #047857

Dark:

* Fondo:
  #064e3b

* Texto:
  #a7f3d0

## Inactivo

Dark:

* Fondo:
  #334155

* Texto:
  #cbd5e1

---

# 10. Modales

Dark Mode:

Overlay:

```css
background: rgba(0,0,0,0.60);
```

Modal:

```css
background:#0f172a;
border:1px solid #334155;
```

Texto:

Principal:
#f8fafc

Secundario:
#94a3b8

---

# 11. Botones

## Primary

Mantener:

* Azul institucional
* Texto blanco
* Hover más oscuro

## Secondary

Dark:

```css
background:#1e293b;
color:#e2e8f0;
```

## Destructive

Dark:

```css
background:#dc2626;
```

---

# 12. Selector de tema

Ubicación recomendada:

Topbar.

Opciones:

* Light
* Dark
* System

Componente:

```
ThemeToggle
```

Estados:

Normal:
Icono sol/luna.

Hover:
Cambio de fondo.

---

# 13. Persistencia

El tema seleccionado debe almacenarse:

Ejemplo:

```javascript
localStorage.setItem(
 "theme",
 "dark"
)
```

Al iniciar:

1. Leer preferencia guardada.
2. Aplicar tema.
3. Si no existe:
   usar preferencia del sistema.

---

# 14. Transiciones

Todos los cambios de tema deben utilizar:

```css
transition:
background-color 200ms,
color 200ms,
border-color 200ms;
```

Evitar cambios bruscos.

---

# 15. Componentes afectados

El modo oscuro debe aplicarse a:

* Sidebar
* Topbar
* Dashboard cards
* Tablas
* Formularios
* Inputs
* Selects
* Buttons
* Modales
* Toasts
* Badges
* Estados loading/error/empty

---

# 16. Reglas generales

* Nunca usar colores hardcodeados dentro de componentes.
* Usar variables de tema.
* Mantener contraste accesible.
* Todos los componentes deben funcionar en ambos modos.
* El cambio de tema no debe modificar lógica de negocio.
