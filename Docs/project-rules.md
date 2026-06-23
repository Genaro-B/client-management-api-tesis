# Reglas del Proyecto

## Objetivo

Este documento establece las convenciones de desarrollo que deberán respetarse durante la implementación de la API.

Todas las decisiones de diseño deberán alinearse con estas reglas.

---

# Estructura de Carpetas

La aplicación deberá utilizar la siguiente estructura:

```text
src/
│
├── api/
│   ├── routes/
│   └── dependencies/
│
├── core/
│
├── database/
│
├── models/
│
├── schemas/
│
├── repositories/
│
├── services/
│
├── tests/
│
└── main.py
```

---

# Convenciones de Nombres

## Archivos

Utilizar snake_case.

### Correcto

```text
cliente_service.py
cliente_repository.py
cliente_schema.py
```

### Incorrecto

```text
ClienteService.py
ClienteRepository.py
```

---

# Modelos

Los modelos SQLAlchemy deberán utilizar nombres en singular.

### Correcto

```python
class Cliente
```

### Incorrecto

```python
class Clientes
```

---

# Schemas

Utilizar sufijos descriptivos.

### Ejemplos

```python
ClienteCreate
ClienteUpdate
ClienteResponse
```

---

# Services

Toda lógica de negocio deberá residir en services.

### Prohibido

* Lógica en routes.
* Acceso directo a base de datos desde routes.

---

# Repositories

Los repositories serán responsables exclusivamente del acceso a datos.

### Responsabilidades

* create
* find_by_id
* find_all
* update
* delete

---

# Rutas

Todas las rutas deberán comenzar con:

```text
/api/v1
```

Ejemplo:

```text
/api/v1/clientes
```

---

# Respuestas HTTP

Utilizar códigos estándar.

### Ejemplos

```text
200 OK
201 Created
204 No Content
400 Bad Request
404 Not Found
409 Conflict
500 Internal Server Error
```

---

# Validaciones

Toda validación de entrada deberá implementarse mediante Pydantic.

No realizar validaciones manuales cuando puedan resolverse mediante schemas.

---

# Manejo de Excepciones

La aplicación deberá implementar manejo global de excepciones.

Crear excepciones específicas para:

* Recurso no encontrado.
* Recurso duplicado.
* Error de negocio.

---

# Base de Datos

Toda interacción con la base de datos deberá realizarse mediante SQLAlchemy.

No utilizar consultas SQL embebidas salvo necesidad justificada.

---

# Testing

Las pruebas deberán ubicarse dentro de:

```text
tests/
```

Manteniendo una estructura similar al código fuente.

Ejemplo:

```text
tests/
├── services/
├── repositories/
└── api/
```

---

# Documentación

Toda funcionalidad nueva deberá reflejarse en:

* Swagger/OpenAPI.
* Documentación técnica correspondiente.

---

# Calidad de Código

Aplicar:

* SOLID
* DRY
* KISS
* Type Hints obligatorios

---

# Fuente de Verdad

La carpeta docs constituye la documentación oficial del proyecto.

Ante conflictos, prevalecerán los documentos contenidos en docs sobre cualquier otra fuente.
 
