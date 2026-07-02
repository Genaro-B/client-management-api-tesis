# Authentication Module Specification

## 1. Objetivo

Este documento define la implementación del módulo de autenticación para el sistema:

**UTN Tesis de Grado**

El módulo permite validar usuarios mediante la API de autenticación y controlar el acceso según el rol asignado.

El sistema debe permitir:

* Inicio de sesión.
* Identificación de roles.
* Redirección según permisos.
* Protección de funcionalidades administrativas.
* Cierre de sesión.

---

# 2. Diseño visual

La pantalla de autenticación debe respetar el Design System definido en:

```
docs/design-system.md
```

Mantener:

* Tipografía Plus Jakarta Sans para títulos.
* Inter para textos generales.
* Paleta azul institucional.
* Cards blancas.
* Bordes redondeados.
* Sombras suaves.
* Estilo SaaS profesional.

---

# 3. Estructura de pantalla Login

## Header superior

Ubicación:

Esquina superior izquierda:

* Nombre:
  "Genaro Busto"
* Badge:
  "UTN"

Esquina superior derecha:

Chip:

"Conexión segura"

Representa el estado seguro de autenticación.

---

## Contenido central

Elemento principal:

Emblema UTN azul centrado.

Título:

```
UTN Tesis de Grado
```

Estilo:

* Plus Jakarta Sans
* Tamaño 26px
* Peso semibold

Subtítulo:

```
Sistema de automatización y administración de prospectos
```

Descripción:

Texto explicativo en color slate:

"Plataforma para la gestión y seguimiento de prospectos académicos."

---

# 4. Card de autenticación

Características:

* Fondo blanco.
* Border radius 16px.
* Border slate-200.
* Shadow-xl.

Contiene:

* Campos de acceso.
* Botón login.
* Mensajes de error.
* Accesos rápidos de prueba.

---

# 5. Formulario Login

Campos:

## Email

Input:

Placeholder:

```
Ingrese correo institucional
```

Icono:

```
<Mail />
```

---

## Contraseña

Input:

Placeholder:

```
Ingrese contraseña
```

Icono:

```
<Lock />
```

---

## Botón iniciar sesión

Texto normal:

```
Iniciar sesión
```

Estado loading:

```
Validando acceso...
```

Durante loading:

* Botón deshabilitado.
* Mostrar spinner interno.
* Bloquear múltiples envíos.

---

# 6. Manejo de errores

Cuando las credenciales sean incorrectas:

Mostrar alerta:

```
Usuario o contraseña incorrectos
```

Características:

* Fondo rojo claro.
* Icono AlertCircle.
* Texto descriptivo.
* Diseño consistente con estados de error del sistema.

---

# 7. Usuarios demo

Agregar tarjetas de acceso rápido para pruebas.

## Administrador

Credenciales:

```
Email:
admin@utn.edu.ar

Password:
admin123
```

Resultado esperado:

Acceso completo.

---

## Usuario estándar

Credenciales:

```
Email:
usuario@utn.edu.ar

Password:
usuario123
```

Resultado esperado:

Acceso limitado.

---

# 8. Sistema de roles

Los permisos deben obtenerse desde la API.

La lógica del frontend solamente interpreta el rol recibido.

Ejemplo:

```javascript
const isAdmin = user.role === "admin";
```

La autorización real pertenece al backend.

---

# 9. Rol Administrador

Cuando el usuario tiene rol:

```
admin
```

Debe acceder al dashboard completo.

Permisos:

* Crear participantes.
* Editar participantes.
* Eliminar participantes.
* Ver acciones disponibles.
* Acceder a todos los modales.

Elementos visibles:

* Botón "Nuevo Cliente".
* Columna "Acciones".
* Acciones:

  * Ver.
  * Editar.
  * Eliminar.

---

# 10. Rol Usuario estándar

Cuando el usuario tiene rol:

```
user
```

Debe acceder a modo lectura.

Permisos:

* Consultar información.
* Visualizar participantes.

Restricciones:

Ocultar:

* Botón crear.
* Botones editar.
* Botones eliminar.
* Acciones administrativas.

Mostrar aviso:

```
Modo solo lectura
```

ubicado en el pie del dashboard.

---

# 11. Dashboard y rol visible

El dashboard debe mostrar el rol actual del usuario.

Ubicación:

Topbar.

Ejemplo:

```
Usuario: Genaro Busto

Rol:
Administrador
```

o

```
Rol:
Usuario estándar
```

---

# 12. Flujo de autenticación

## Login exitoso

Flujo:

```
Usuario ingresa credenciales
          |
          v
Frontend envía solicitud API
          |
          v
API valida usuario
          |
          v
API devuelve usuario + rol
          |
          v
Frontend guarda sesión
          |
          v
Redirige Dashboard
```

---

## Logout

Flujo:

```
Usuario selecciona cerrar sesión
          |
          v
Eliminar sesión/token
          |
          v
Mostrar toast:
"Sesión cerrada correctamente"
          |
          v
Redirigir Login
```

---

# 13. Protección de rutas

Las rutas administrativas deben estar protegidas.

Ejemplo:

```
/dashboard
```

Disponible para todos los usuarios autenticados.

```
/admin/*
```

Disponible solamente para usuarios con rol admin.

---

# 14. Componentes requeridos

Crear componentes reutilizables:

```
src/
├── pages/
│    ├── LoginPage
│    └── DashboardPage
│
├── components/
│    ├── LoginCard
│    ├── RoleBadge
│    ├── DemoCredentialCard
│    └── ProtectedRoute
│
├── services/
│    └── authService
│
└── hooks/
     └── useAuth
```

---

# 15. Estados de autenticación

Estados requeridos:

* Usuario no autenticado.
* Validando credenciales.
* Login exitoso.
* Credenciales incorrectas.
* Sesión expirada.
* Usuario sin permisos.

Todos los estados deben mostrar feedback visual al usuario.
