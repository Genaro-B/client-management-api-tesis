# Ejemplos de Responses

## Cliente Creado

### HTTP 201

```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Perez",
  "telefono": "2991234567",
  "email": "juan.perez@email.com",
  "fechaRegistro": "2026-06-22T20:30:00",
  "activo": true
}
```

---

## Cliente Encontrado

### HTTP 200

```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Perez",
  "telefono": "2991234567",
  "email": "juan.perez@email.com",
  "fechaRegistro": "2026-06-22T20:30:00",
  "activo": true
}
```

---

## Lista de Clientes

### HTTP 200

```json
[
  {
    "id": 1,
    "nombre": "Juan",
    "apellido": "Perez",
    "email": "juan@email.com"
  },
  {
    "id": 2,
    "nombre": "Maria",
    "apellido": "Lopez",
    "email": "maria@email.com"
  }
]
```

---

## Error de Validación

### HTTP 400

```json
{
  "detail": "El correo electrónico es obligatorio"
}
```

---

## Cliente No Encontrado

### HTTP 404

```json
{
  "detail": "Cliente no encontrado"
}
```

---

## Cliente Duplicado

### HTTP 409

```json
{
  "detail": "Ya existe un cliente con ese correo electrónico"
}
```
 
