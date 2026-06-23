# Sistema de Automatización Inteligente para la Gestión de Clientes

## Descripción General

Este proyecto tiene como objetivo el diseño, desarrollo e implementación de una plataforma de automatización orientada a la gestión de clientes mediante la integración de servicios, procesamiento de lenguaje natural e inteligencia artificial.

La solución busca optimizar procesos operativos mediante la automatización de tareas administrativas, permitiendo que los usuarios interactúen con el sistema a través de interfaces conversacionales y flujos automatizados.

Como núcleo de la arquitectura se desarrolla una API REST basada en FastAPI, responsable de centralizar la lógica de negocio, la validación de datos y la persistencia de la información.

---

## Contexto Académico

Este proyecto se desarrolla como Trabajo Final Integrador de la Tecnicatura Universitaria en Programación de la Universidad Tecnológica Nacional (UTN).

La investigación se enfoca en el análisis y aplicación de tecnologías de automatización e inteligencia artificial en entornos de bajo costo, evaluando su viabilidad como herramienta para optimizar procesos organizacionales.

---

## Objetivos del Proyecto

### Objetivo General

Desarrollar una solución de automatización capaz de gestionar información de clientes mediante la integración de servicios e inteligencia artificial.

### Objetivos Específicos

- Diseñar una arquitectura desacoplada y escalable.
- Implementar una API REST para la gestión de clientes.
- Integrar servicios externos mediante flujos automatizados.
- Incorporar procesamiento de lenguaje natural para la interpretación de solicitudes.
- Centralizar la información en una base de datos relacional.
- Evaluar la factibilidad de soluciones de automatización de bajo costo.

---

## Arquitectura de Alto Nivel

```text
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Telegram   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     n8n     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   MySQL     │
└─────────────┘
```

---

## Alcance de la Primera Versión

La versión inicial se encuentra enfocada en la gestión de clientes.

### Funcionalidades Incluidas

- Registro de clientes.
- Consulta de clientes.
- Actualización de información.
- Eliminación de registros.
- Listado de clientes.
- Validación de datos.
- Documentación automática de API.
- Integración con flujos automatizados mediante n8n.
- Recepción de solicitudes desde Telegram.

### Funcionalidades Futuras

- Autenticación y autorización.
- Gestión de usuarios y roles.
- Historial de interacciones.
- Dashboard administrativo.
- Integración con CRM.
- Métricas y monitoreo.
- Automatizaciones avanzadas basadas en IA.
- Gestión de múltiples entidades de negocio.

---

## Stack Tecnológico

### Backend

- Python 3.13
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Persistencia

- MySQL 8

### Automatización

- n8n

### Integraciones

- Telegram Bot API
- Servicios de Inteligencia Artificial

### Infraestructura

- Docker
- Docker Compose

### Testing

- Pytest

### Documentación

- OpenAPI
- Swagger UI
- ReDoc

---

## Principios de Diseño

La solución se construye siguiendo buenas prácticas de ingeniería de software:

- Arquitectura en capas.
- Principios SOLID.
- Clean Code.
- Separación de responsabilidades.
- Desarrollo orientado a APIs.
- Documentación continua.
- Escalabilidad y mantenibilidad.
- Bajo acoplamiento entre componentes.
- Diseño orientado a integración de servicios.

---

## Metodología de Desarrollo

El proyecto se desarrolla mediante un enfoque incremental basado en especificaciones, utilizando documentación técnica como fuente principal para el diseño e implementación del sistema.

La construcción de los componentes se realiza a partir de documentos de arquitectura, requisitos funcionales, reglas de negocio y contratos API previamente definidos.

El desarrollo incorpora herramientas de asistencia basadas en inteligencia artificial para acelerar tareas de diseño e implementación, manteniendo la documentación como fuente de verdad del proyecto.

La validación se efectúa mediante pruebas unitarias, pruebas de integración y pruebas funcionales sobre los flujos automatizados implementados en n8n.

---

## Estructura de Documentación

```text
docs/
├── vision.md
├── requirements.md
├── domain-model.md
├── api-spec.md
├── architecture.md
├── tech-stack.md
├── non-functional-requirements.md
├── project-rules.md
├── master-prompt.md
│
├── database/
│   ├── database-schema.md
│   └── entity-relationship-diagram.md
│
└── openapi/
    ├── request-examples.md
    └── response-examples.md
```

---

## Estado del Proyecto

🚧 En desarrollo activo.

Actualmente el proyecto se encuentra en fase de implementación y validación de la arquitectura base.

Las actividades en curso incluyen:

- Desarrollo de la API REST utilizando FastAPI.
- Diseño e implementación del modelo de datos.
- Configuración de la persistencia mediante MySQL.
- Definición y validación de contratos API.
- Construcción de flujos de automatización en n8n.
- Integración con Telegram Bot API.
- Desarrollo y pruebas funcionales de un bot conversacional.
- Validación de procesos automatizados mediante n8n.
- Evaluación de la comunicación entre Telegram, n8n y la API.
- Definición de la estrategia de integración con servicios de inteligencia artificial.
- Pruebas incrementales de los distintos componentes antes de su integración definitiva.

El desarrollo se realiza de manera iterativa, validando cada componente individualmente para garantizar estabilidad, mantenibilidad y escalabilidad antes de avanzar hacia etapas más complejas del sistema.

---

## Líneas Futuras de Investigación y Desarrollo

- Incorporación de modelos de inteligencia artificial para interpretación avanzada de solicitudes.
- Automatización de procesos empresariales adicionales.
- Integración con sistemas CRM y ERP.
- Implementación de autenticación y autorización basada en roles.
- Desarrollo de interfaces web administrativas.
- Incorporación de métricas operativas y observabilidad.
- Evaluación comparativa de distintas herramientas de automatización e IA.

---

## Autor

**Genaro Busto**  
Tecnicatura Universitaria en Programación  
Universidad Tecnológica Nacional (UTN)

---

## Licencia

Proyecto desarrollado con fines académicos, educativos y de investigación. 
