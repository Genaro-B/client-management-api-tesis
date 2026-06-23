# Especificación de API REST

## Introducción

Este documento define los endpoints REST expuestos por el sistema para la gestión de clientes.

La API seguirá principios RESTful, utilizará JSON como formato de intercambio de datos y permitirá operaciones CRUD sobre la entidad Cliente.

---

# Información General

## Base URL

```text
/api/v1
```

## Content-Type

```http
application/json
```

---

# Modelo Cliente

```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Perez",
  "telefono": "2991234567",
  "email": "juan@email.com",
  "fechaRegistro": "2026-06-22T15:30:00",
  "activo": true
}
```

---

# POST /clientes

## Descripción

Registrar un nuevo cliente.

## Request

```json
{
  "nombre": "Juan",
  "apellido": "Perez",
  "telefono": "2991234567",
  "email": "juan@email.com"
}
```

## Response

```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Perez",
  "telefono": "2991234567",
  "email": "juan@email.com",
  "fechaRegistro": "2026-06-22T15:30:00",
  "activo": true
}
```

## Códigos

* 201 Created
* 400 Bad Request
* 409 Conflict

---

# GET /clientes

## Descripción

Obtener listado completo de clientes.

## Response

```json
[
  {
    "id": 1,
    "nombre": "Juan",
    "apellido": "Perez",
    "email": "juan@email.com"
  }
]
```

## Códigos

* 200 OK

---

# GET /clientes/{id}

## Descripción

Obtener cliente por identificador.

## Parámetros

| Nombre | Tipo | Descripción               |
| ------ | ---- | ------------------------- |
| id     | Long | Identificador del cliente |

## Códigos

* 200 OK
* 404 Not Found

---

# GET /clientes/email/{email}

## Descripción

Buscar cliente por correo electrónico.

## Códigos

* 200 OK
* 404 Not Found

---

# PUT /clientes/{id}

## Descripción

Actualizar información de un cliente.

## Request

```json
{
  "nombre": "Juan Carlos",
  "apellido": "Perez",
  "telefono": "2991234567",
  "email": "juan@email.com"
}
```

## Códigos

* 200 OK
* 400 Bad Request
* 404 Not Found

---

# DELETE /clientes/{id}

## Descripción

Eliminar un cliente.

## Códigos

* 204 No Content
* 404 Not Found

---

# Reglas de Validación

## nombre

* Obligatorio.
* Longitud máxima: 100 caracteres.

## apellido

* Obligatorio.
* Longitud máxima: 100 caracteres.

## email

* Obligatorio.
* Formato válido.
* Único en el sistema.

## telefono

* Opcional.
* Longitud máxima: 20 caracteres.

---

# Manejo de Errores

## Error de Validación

```json
{
  "timestamp": "2026-06-22T15:30:00",
  "status": 400,
  "error": "Bad Request",
  "message": "El correo electrónico es obligatorio"
}
```

## Recurso No Encontrado

```json
{
  "timestamp": "2026-06-22T15:30:00",
  "status": 404,
  "error": "Not Found",
  "message": "Cliente no encontrado"
}
```

## Recurso Duplicado

```json
{
  "timestamp": "2026-06-22T15:30:00",
  "status": 409,
  "error": "Conflict",
  "message": "Ya existe un cliente con ese correo electrónico"
}
```
 
