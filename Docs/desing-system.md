Estructura completa:

Sidebar colapsable con los 4 ítems de menú, logo CRM y botón para contraer
Topbar con título, subtítulo y botón "Nuevo Cliente"
Barra de búsqueda + filtro de estado + filtro de fecha + botón "Limpiar"
Tabla con las 8 columnas requeridas, avatares con iniciales en colores distintos, datos con DM Mono para IDs, teléfonos, DNI y fechas
Acciones por fila que aparecen al hacer hover (Ver / Editar / Eliminar)
Modales:

Ver detalles — tarjeta con toda la info del cliente y acceso directo a editar
Editar cliente — formulario completo con todos los campos, spinner mientras guarda
Eliminar — modal de confirmación con alerta roja, nombre del cliente y spinner
Estados visuales:

Spinner de carga al consultar la API simulada
Estado de error con botón "Reintentar conexión"
Estado vacío cuando no hay resultados
Toasts de éxito/error via sonner para cada acción
Diseño:

Sidebar oscuro (#0f172a) con nav en azul activo
Fondo slate-50, cards blancas con sombra sutil
Tipografía: Plus Jakarta Sans (títulos) + Inter (cuerpo) + DM Mono (datos tabulares)
Badges de estado con anillo de color (verde esmeralda / gris)
Analiza esta pantalla y genera una documentación del sistema de diseño utilizado. Describe colores, tipografías, tamaños, espaciados, componentes reutilizables, botones, tablas, formularios, estados, modales y reglas visuales necesarias para que un desarrollador frontend pueda implementar esta interfaz exactamente igual.

Voy a analizar el código implementado y generar la documentación completa del sistema de diseño.

Aquí está la documentación completa del sistema de diseño:

Design System Documentation — CRM AdminPanel
1. Fundamentos tipográficos
Familias de fuente
Rol	Familia	Uso
Display	Plus Jakarta Sans	Títulos de página, nombres en encabezados de modal, logo
Body / UI	Inter	Texto de interfaz general, labels, botones, párrafos
Mono	DM Mono	IDs, teléfonos, DNI, fechas en tabla, códigos de cliente
--font-sans:    "Inter", "Plus Jakarta Sans", system-ui, sans-serif;
--font-display: "Plus Jakarta Sans", system-ui, sans-serif;
--font-mono:    "DM Mono", monospace;
Escala tipográfica
Token	px	Uso
text-[10px]	10	Labels de sección UPPERCASE (encabezados de columna, field labels)
text-[11px]	11	IDs, datos mono en tabla, contadores de pie de tabla
text-[12px]	12	Subtítulo de topbar, badges de estado, texto secundario de modales
text-[13px]	13	Texto de tabla (email, teléfono), botones, inputs, nav items
text-[14px]	14	Títulos de alerta en modal, texto de error principal
text-[15px]	15	Base font-size del documento (--font-size)
text-[17px]	17	Título principal en topbar, nombre de cliente en modal de detalle
Pesos
Variable	Valor	Uso
--font-weight-normal	400	Texto de inputs, datos de tabla
--font-weight-medium	500	Labels de formulario, botones
font-semibold	600	Nombres de clientes, títulos de modal, botones primarios
font-bold	700	Labels UPPERCASE de fields, initials de avatares
Regla de labels uppercase
Todos los labels de campos de formulario y encabezados de columna de tabla siguen este patrón:

font-size: 10px;
font-weight: 700;
text-transform: uppercase;
letter-spacing: 0.1em; /* tracking-widest */
color: #94a3b8; /* slate-400 */
2. Paleta de colores
Tokens globales
Token	Valor	Clase Tailwind	Uso
--background	#f8fafc	bg-background	Fondo de página (slate-50)
--foreground	#0f172a	text-foreground	Texto principal (slate-900)
--card	#ffffff	bg-card	Fondo de cards y modales
--primary	#2563eb	bg-primary	Azul primario (blue-600)
--primary-foreground	#ffffff	text-primary-foreground	Texto sobre primario
--secondary	#f1f5f9	bg-secondary	Superficies secundarias (slate-100)
--muted	#f1f5f9	bg-muted	Fondos atenuados
--muted-foreground	#64748b	text-muted-foreground	Texto atenuado (slate-500)
--border	rgba(15,23,42,0.08)	border-border	Líneas divisorias sutiles
--destructive	#dc2626	bg-destructive	Rojo de peligro (red-600)
--ring	#93c5fd	ring-ring	Focus ring (blue-300)
Tokens del sidebar
Token	Valor	Uso
--sidebar	#0f172a	Fondo del sidebar (slate-900)
--sidebar-foreground	#f8fafc	Texto en sidebar
--sidebar-primary	#3b82f6	Nav item activo (blue-500)
--sidebar-accent	#1e293b	Hover de nav item (slate-800)
--sidebar-border	rgba(255,255,255,0.08)	Divisores en sidebar
Colores semánticos de estado
Estado	Background	Text	Ring/Border
Activo	bg-emerald-50 (#ecfdf5)	text-emerald-700 (#047857)	ring-emerald-200 (#a7f3d0)
Inactivo	bg-slate-100 (#f1f5f9)	text-slate-500 (#64748b)	ring-slate-200 (#e2e8f0)
Error	bg-red-50 (#fef2f2)	text-red-600 (#dc2626)	border-red-100 (#fee2e2)
Info/Accent	bg-blue-50 (#eff6ff)	text-blue-600 (#2563eb)	—
Paleta de avatares (rotación por id % 6)
0 → bg-blue-100    / text-blue-700
1 → bg-violet-100  / text-violet-700
2 → bg-emerald-100 / text-emerald-700
3 → bg-amber-100   / text-amber-700
4 → bg-rose-100    / text-rose-700
5 → bg-cyan-100    / text-cyan-700
3. Sistema de espaciado
Token Tailwind	px	Uso frecuente
gap-1	4px	Gap entre action buttons
gap-2 / gap-2.5	8–10px	Gap entre botones en modales
gap-3	12px	Grid de campos en formulario, gap de avatar+nombre
gap-4	16px	Separación de secciones dentro de modal
gap-5	20px	Separación entre bloque avatar y grid de datos
px-3	12px	Padding horizontal de inputs y selects
px-4	16px	Padding del botón "Nuevo Cliente"
px-5	20px	Padding horizontal de celdas de tabla
px-6	24px	Padding horizontal de modales
px-8	32px	Padding horizontal del topbar y área de contenido
py-2.5	10px	Altura de inputs, selects y botones
py-3.5	14px	Altura de encabezados de tabla
py-4	16px	Altura de filas de tabla
py-5	20px	Padding vertical del cuerpo de modal
py-28	112px	Padding vertical de estados vacíos/error/loading
mb-1.5	6px	Separación entre label y su input
mb-5	20px	Separación entre filtros y tabla
p-8	32px	Padding del área principal de contenido
4. Sistema de radios
Variable	Cálculo	px aprox.	Uso
--radius-sm	radius - 4px	4px	—
--radius-md	radius - 2px	6px	Botones de acción pequeños (rounded-md)
--radius-lg	0.5rem	8px	Base radius — inputs, selects, botones, badges
--radius-xl	radius + 4px	12px	Cards principales, modales (rounded-xl)
5. Sombras y elevación
Nivel	Clase	Uso
Nivel 0	Sin sombra	Sidebar, topbar, inputs
Nivel 1	shadow-sm	Tabla de clientes, botón primario (shadow-sm shadow-blue-500/20)
Nivel 2	shadow-xl	Modales sobre overlay
6. Layout principal
┌─────────────────────────────────────────────────────────┐
│  SIDEBAR (220px / 60px colapsado)  │  MAIN AREA (flex-1) │
│  bg: #0f172a                       │                     │
│  ┌──────────────────────────────┐  │  ┌───────────────┐  │
│  │ Logo (h-16, border-b)        │  │  │ Topbar (h-16) │  │
│  ├──────────────────────────────┤  │  ├───────────────┤  │
│  │ Nav items (py-4 px-2)        │  │  │ Content (p-8) │  │
│  │                              │  │  │ bg: slate-50  │  │
│  ├──────────────────────────────┤  │  │               │  │
│  │ Collapse toggle (border-t)   │  │  └───────────────┘  │
│  └──────────────────────────────┘  │                     │
└─────────────────────────────────────────────────────────┘
Layout: flex h-screen overflow-hidden
Sidebar: flex-shrink-0, transición de ancho transition-all duration-300
Main: flex-1 flex flex-col overflow-hidden min-w-0
Content: flex-1 overflow-y-auto
7. Componente: Sidebar
Ancho expandido:  220px (w-[220px])
Ancho colapsado:   60px (w-[60px])
Fondo: #0f172a
Transición: transition-all duration-300 ease-in-out
Logo area
Altura: h-16
Padding: px-5 (expandido) / justify-center (colapsado)
Separador inferior: border-b con rgba(255,255,255,0.07)
Logo badge: w-7 h-7 rounded-lg bg-blue-600, texto text-[11px] font-bold
Nombre: text-sm font-semibold, fuente Plus Jakarta Sans
Nav item — estado normal
padding: 10px 12px;     /* py-2.5 px-3 */
border-radius: 8px;     /* rounded-lg */
font-size: 13px;
font-weight: 500;
color: #94a3b8;         /* slate-400 */
background: transparent;
Nav item — hover
color: #ffffff;
background: rgba(255,255,255,0.07);
Nav item — activo
color: #ffffff;
background: #2563eb;    /* blue-600 */
box-shadow: 0 1px 2px rgba(0,0,0,0.05);
Botón collapse
padding: 8px 12px;
border-radius: 8px;
font-size: 12px;
color: #64748b;         /* slate-500 */
hover: color #cbd5e1, bg rgba(255,255,255,0.06)
8. Componente: Topbar
Altura: h-16 (64px)
Fondo: #ffffff
Borde inferior: border-b border-slate-100
Padding horizontal: px-8 (32px)
Elemento	Estilos
Título H1	text-[17px] font-semibold text-slate-900, fuente Plus Jakarta Sans
Subtítulo	text-[12px] text-slate-400 mt-0.5
Botón primario	Ver sección Botones → Primario
9. Componente: Botones
Primario (Nuevo Cliente)
background: #2563eb;
color: #ffffff;
font-size: 13px;
font-weight: 600;
padding: 10px 16px;     /* py-2.5 px-4 */
border-radius: 8px;
box-shadow: 0 1px 2px rgba(37,99,235,0.2);

hover: background #1d4ed8;
active: background #1e40af;
transition: colors 150ms;
Incluye icono <Plus size={15} strokeWidth={2.5} /> a la izquierda con gap-2.

Secundario / Ghost (Cancelar, Cerrar)
background: #f1f5f9;    /* slate-100 */
color: #334155;         /* slate-700 */
font-size: 13px;
font-weight: 600;
padding: 10px 0;        /* py-2.5, flex-1 */
border-radius: 8px;

hover: background #e2e8f0;
disabled: opacity 60%
Destructivo (Confirmar eliminación)
background: #dc2626;
color: #ffffff;
font-size: 13px;
font-weight: 600;
padding: 10px 0;
border-radius: 8px;

hover: background #b91c1c;
disabled: opacity 60%
Action Button (Ver / Editar / Eliminar en tabla)
padding: 6px;           /* p-1.5 */
border-radius: 6px;     /* rounded-md */
color: #94a3b8;         /* slate-400 base */
background: transparent;
transition: colors 150ms;

/* Por color de acción: */
Ver    → hover: bg-blue-50,  text-blue-600
Editar → hover: bg-amber-50, text-amber-600
Eliminar → hover: bg-red-50, text-red-600
Los action buttons son invisibles por defecto (opacity-0) y aparecen al hacer hover sobre la fila (group-hover:opacity-100).

Link-button (Reintentar)
font-size: 13px;
font-weight: 600;
color: #2563eb;
display: flex;
align-items: center;
gap: 4px;

hover: color #1d4ed8
10. Componente: Inputs y Selects
Input de búsqueda
background: #ffffff;
border: 1px solid rgba(15,23,42,0.08);
border-radius: 8px;
padding: 10px 16px 10px 36px;  /* pr-4, pl-9 para icono */
font-size: 13px;
color: #0f172a;
placeholder: #94a3b8;

focus:
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.20);
  transition: all 150ms;
Icono <Search size={14} /> posicionado absolute left-3.5 top-50% -translate-y-1/2 text-slate-400.

Input de formulario (dentro de modal)
background: #f8fafc;    /* slate-50 */
border: 1px solid #e2e8f0;  /* slate-200 */
border-radius: 8px;
padding: 10px 12px;     /* py-2.5 px-3 */
font-size: 13px;
color: #0f172a;
width: 100%;

focus:
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.20);
Select / Dropdown
Mismo estilo que Input de formulario +

appearance: none;
padding-right: 32px;   /* pr-8 */
cursor: pointer;
font-weight: 500;
Icono <ChevronDown size={13} /> posicionado absolute right-2.5, pointer-events-none.

Label de campo
font-size: 10px;
font-weight: 700;
text-transform: uppercase;
letter-spacing: 0.1em;
color: #64748b;         /* slate-500 */
margin-bottom: 6px;     /* mb-1.5 */
display: block;
11. Componente: Tabla
Contenedor
background: #ffffff;
border: 1px solid rgba(15,23,42,0.08);
border-radius: 12px;    /* rounded-xl */
box-shadow: 0 1px 2px rgba(0,0,0,0.05);
overflow: hidden;
Encabezado de tabla (<thead>)
background: rgba(248,250,252,0.8);  /* slate-50/80 */
border-bottom: 1px solid #f1f5f9;   /* slate-100 */

th:
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #94a3b8;         /* slate-400 */
  padding: 14px 20px;     /* py-3.5 px-5 */
  white-space: nowrap;
  text-align: left;
Filas (<tbody>)
divide-y: 1px solid #f8fafc;   /* slate-50 — muy sutil */

tr:
  transition: background 150ms;
  
tr:hover:
  background: rgba(239,246,255,0.3);  /* blue-50/30 */
Celdas (<td>)
padding: 16px 20px;   /* py-4 px-5 */
Tipos de celda
Celda	Estilos
ID	font-family: DM Mono, font-size: 11px, color: #94a3b8
Nombre	Avatar + font-size: 13px font-weight: 600 text-slate-800
Email	font-size: 13px, color: #475569 (slate-600)
Teléfono / DNI	font-family: DM Mono, font-size: 12px, color: #475569
Fecha	font-family: DM Mono, font-size: 12px, color: #64748b
Estado	Badge (ver componente Badge)
Acciones	Grupo de 3 ActionButtons
Footer de tabla
padding: 12px 20px;   /* py-3 px-5 */
border-top: 1px solid #f1f5f9;
background: rgba(248,250,252,0.5);
display: flex;
justify-content: space-between;
align-items: center;
font-size: 11px;
color: #94a3b8;
12. Componente: Avatar
width: 32px;   height: 32px;   /* w-8 h-8 en tabla */
width: 56px;   height: 56px;   /* w-14 h-14 en modal de detalle */
border-radius: 9999px;         /* rounded-full */
font-size: 11px;               /* tabla */
font-size: 18px;               /* modal */
font-weight: 700;
display: flex;
align-items: center;
justify-content: center;
Color determinado por id % 6 (ver paleta de avatares).
Contenido: iniciales en uppercase nombre[0] + apellido[0].

13. Componente: Badge de estado
display: inline-flex;
align-items: center;
gap: 6px;           /* gap-1.5 */
padding: 4px 10px;  /* py-1 px-2.5 */
border-radius: 9999px;
font-size: 11px;
font-weight: 700;
letter-spacing: 0.05em;

/* Activo */
background: #ecfdf5;
color: #047857;
box-shadow: inset 0 0 0 1px #a7f3d0;   /* ring-1 ring-emerald-200 */

/* Inactivo */
background: #f1f5f9;
color: #64748b;
box-shadow: inset 0 0 0 1px #e2e8f0;
Punto indicador:

width: 6px; height: 6px;
border-radius: 9999px;

/* Activo */  background: #10b981;
/* Inactivo */ background: #94a3b8;
14. Componente: Modal
Overlay
position: fixed;
inset: 0;
z-index: 50;
display: flex;
align-items: center;
justify-content: center;
padding: 16px;

/* Backdrop */
background: rgba(15,23,42,0.40);
backdrop-filter: blur(2px);
Click en backdrop cierra el modal (excepto si hay operación en curso).

Modal shell
background: #ffffff;
border: 1px solid #e2e8f0;   /* slate-200 */
border-radius: 12px;          /* rounded-xl */
box-shadow: 0 20px 60px rgba(0,0,0,0.25);  /* shadow-2xl */
overflow: hidden;
width: 100%;

/* Tamaños */
max-width: 448px;  /* max-w-md — modal eliminación */
max-width: 512px;  /* max-w-lg — modal editar / detalle */
Header del modal
display: flex;
align-items: center;
justify-content: space-between;
padding: 16px 24px;   /* py-4 px-6 */
border-bottom: 1px solid #f1f5f9;

título:
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: -0.015em;  /* tracking-tight */

botón X:
  padding: 6px;
  border-radius: 8px;
  color: #94a3b8;
  hover: bg-slate-100, color #475569
Body del modal
padding: 20px 24px;   /* py-5 px-6 */
15. Estados visuales de la tabla
Loading
Centrado vertical: py-28 (112px arriba y abajo)
Spinner: w-7 h-7, border-2, border-blue-600, border-t-transparent,
         border-radius: 9999px, animation: spin
Texto: font-size 13px, color #94a3b8
Error
Ícono container: w-12 h-12, border-radius 9999px,
                 bg-red-50, ring-1 ring-red-100
Ícono: <AlertCircle size={20} /> color red-500
Título: font-size 14px, font-weight 600, color #0f172a
Descripción: font-size 12px, color #94a3b8, max-width 20rem
Link retry: ver Botones → Link-button
Vacío (sin resultados)
Ícono container: w-12 h-12, border-radius 9999px,
                 bg-slate-100, ring-1 ring-slate-200
Ícono: <Inbox size={20} /> color slate-400
Título: font-size 14px, font-weight 600
Subtítulo: font-size 12px, color slate-400
16. Componente: Toast (Sonner)
Posición: top-right
Configuración: richColors closeButton

Tipo	Trigger
toast.success("Cliente actualizado correctamente")	PUT exitoso
toast.success("Cliente eliminado correctamente")	DELETE exitoso
toast.error("Error al actualizar el cliente")	PUT fallido
toast.error("Error al eliminar el cliente")	DELETE fallido
toast.info(...)	Acciones no implementadas aún
17. Estados de carga en botones
Cuando saving o deleting es true:

disabled: opacity 60%, cursor: default

/* Spinner inline */
width: 14px; height: 14px;
border: 2px solid rgba(255,255,255,0.9);
border-top-color: transparent;
border-radius: 9999px;
animation: spin;
margin-right: 8px;

/* Texto cambia a: */
"Guardando…" / "Eliminando…"
18. Reglas visuales globales
Scrollbar: oculta por defecto, overflow-hidden en el layout raíz, overflow-y-auto solo en zonas de scroll.
Transiciones: todas las interacciones usan transition-colors 150ms o transition-all 150ms. Nunca animaciones abruptas.
Hover en filas de tabla: group en <tr>, group-hover: en elementos hijos. Los action buttons son opacity-0 por defecto.
Focus: focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 — consistente en todos los inputs.
Sidebar colapsado: los title de los nav items hacen de tooltip nativo del navegador.
Datos monetarios o identificadores: siempre en DM Mono, nunca en Inter.
Botones en modal: siempre en par flex gap-2.5, con flex-1 para que ocupen el mismo ancho.
Acciones destructivas: confirmación obligatoria en modal separado antes de ejecutar el DELETE.
Grid de campos en formulario: 2 columnas para campos cortos (Nombre/Apellido, Teléfono/DNI), 1 columna para campos largos (Email, Dirección).
Z-index: modales en z-50, backdrop es hermano absoluto del contenido (no padre).
19. Dependencias requeridas
{
  "react": "^18",
  "lucide-react": "latest",
  "sonner": "latest",
  "tailwindcss": "^4"
}
Iconos utilizados
Users, LayoutDashboard, Settings, UserCircle  → sidebar nav
Plus                                           → botón Nuevo Cliente
Search                                         → barra de búsqueda
ChevronDown                                    → selects
Eye, Pencil, Trash2                            → acciones de fila
X                                              → cierre de modales
AlertCircle                                    → error y advertencia destructiva
Inbox                                          → estado vacío
Menu                                           → toggle sidebar
RefreshCw                                      → retry / actualizar