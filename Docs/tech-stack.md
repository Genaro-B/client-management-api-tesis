 # Stack Tecnológico

## Introducción

Este documento define las tecnologías seleccionadas para el desarrollo de la API REST del proyecto.

La elección de cada tecnología se basa en criterios de simplicidad, productividad, documentación disponible, facilidad de integración y adecuación al contexto de una solución de automatización de bajo costo.

---

# Backend

## Framework

FastAPI

### Justificación

* Alto rendimiento.
* Soporte nativo para APIs REST.
* Generación automática de documentación OpenAPI.
* Integración sencilla con validaciones mediante Pydantic.
* Curva de aprendizaje reducida.

---

# Lenguaje de Programación

Python 3.13

### Justificación

* Amplio ecosistema.
* Excelente integración con herramientas de inteligencia artificial.
* Sintaxis simple y mantenible.
* Gran adopción en automatización y desarrollo backend.

---

# Validación de Datos

Pydantic

### Responsabilidades

* Validación de solicitudes.
* Validación de respuestas.
* Serialización y deserialización de datos.
* Definición de esquemas DTO.

---

# Persistencia

## Base de Datos

MySQL 8

### Justificación

* Amplia adopción empresarial.
* Facilidad de administración.
* Compatibilidad con herramientas de análisis y monitoreo.
* Estabilidad y madurez tecnológica.

---

# ORM

SQLAlchemy

### Responsabilidades

* Mapeo objeto-relacional.
* Gestión de entidades.
* Construcción de consultas.
* Persistencia de datos.

---

# Migraciones

Alembic

### Responsabilidades

* Versionado del esquema de base de datos.
* Gestión de cambios estructurales.
* Evolución controlada del modelo de datos.

---

# Documentación de API

OpenAPI / Swagger

### Características

* Generación automática.
* Exploración interactiva de endpoints.
* Pruebas manuales desde navegador.

---

# Testing

Pytest

### Objetivos

* Validación de endpoints.
* Validación de servicios.
* Validación de reglas de negocio.

---

# Contenedorización

Docker

### Objetivos

* Reproducibilidad de entornos.
* Facilidad de despliegue.
* Aislamiento de dependencias.

---

# Control de Versiones

Git

Repositorio alojado en GitHub.

---

# Integraciones Externas

## Telegram Bot API

Canal de interacción con usuarios.

## n8n

Motor de automatización y orquestación de procesos.

---

# Principios de Desarrollo

* Arquitectura en capas.
* Separación de responsabilidades.
* Código desacoplado.
* Principios SOLID.
* Desarrollo orientado a APIs.
* Documentación continua.
