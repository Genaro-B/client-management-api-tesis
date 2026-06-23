 # Master Prompt

## Contexto

Actúa como arquitecto de software senior especializado en FastAPI, Python y arquitecturas empresariales.

Debes generar una API REST profesional basándote exclusivamente en la documentación disponible dentro de la carpeta docs.

---

## Objetivo

Construir una API REST para la gestión de clientes.

La API formará parte de un sistema de automatización integrado con Telegram, n8n y servicios de inteligencia artificial.

---

## Tecnologías Obligatorias

* Python 3.13
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic
* MySQL
* Pytest
* Docker

---

## Arquitectura Obligatoria

Implementar arquitectura en capas:

* Controllers (Routes)
* Services
* Repositories
* Models
* Schemas
* Database

Separar estrictamente responsabilidades.

---

## Entidad Principal

Cliente

Campos:

* id
* nombre
* apellido
* telefono
* email
* fechaRegistro
* activo

---

## Reglas de Negocio

* nombre obligatorio
* apellido obligatorio
* email obligatorio
* email único
* fechaRegistro automática
* activo = true por defecto

---

## Endpoints Obligatorios

POST /api/v1/clientes

GET /api/v1/clientes

GET /api/v1/clientes/{id}

GET /api/v1/clientes/email/{email}

PUT /api/v1/clientes/{id}

DELETE /api/v1/clientes/{id}

---

## Calidad de Código

Aplicar:

* SOLID
* Clean Code
* Type Hints
* Dependency Injection
* Manejo global de excepciones

---

## Testing

Generar pruebas automáticas utilizando Pytest.

---

## Documentación

Generar automáticamente:

* Swagger
* OpenAPI
* ReDoc

---

## Restricciones

No utilizar Flask.

No utilizar Django.

No utilizar lógica de negocio dentro de los controllers.

No acceder a la base de datos directamente desde los endpoints.

---

## Fuente de Verdad

Los documentos contenidos en la carpeta docs constituyen la fuente oficial de requisitos y arquitectura.
