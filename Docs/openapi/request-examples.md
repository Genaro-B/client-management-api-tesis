# Ejemplos de Requests

## Crear Cliente

### POST /api/v1/clientes

```json
{
  "nombre": "Juan",
  "apellido": "Perez",
  "telefono": "2991234567",
  "email": "juan.perez@email.com"
}
```

---

## Actualizar Cliente

### PUT /api/v1/clientes/1

```json
{
  "nombre": "Juan Carlos",
  "apellido": "Perez",
  "telefono": "2999876543",
  "email": "juan.perez@email.com"
}
```

---

## Buscar Cliente por Email

### GET /api/v1/clientes/email/juan.[perez@email.com](mailto:perez@email.com)

Sin cuerpo de solicitud.

---

## Obtener Cliente por ID

### GET /api/v1/clientes/1

Sin cuerpo de solicitud.

---

## Listar Clientes

### GET /api/v1/clientes

Sin cuerpo de solicitud.

---

## Eliminar Cliente

### DELETE /api/v1/clientes/1

Sin cuerpo de solicitud.
 
