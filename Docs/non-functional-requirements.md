# Requisitos No Funcionales

## Introducción

Este documento define los requisitos no funcionales de la API REST para la gestión de clientes.

Los requisitos no funcionales establecen restricciones, características de calidad y criterios técnicos que deberán cumplirse durante el desarrollo y operación del sistema.

---

# RNF-01 Arquitectura

La aplicación deberá implementar una arquitectura en capas.

## Objetivos

* Separación de responsabilidades.
* Bajo acoplamiento.
* Alta cohesión.
* Facilidad de mantenimiento.

---

# RNF-02 Rendimiento

La API deberá responder las solicitudes en tiempos adecuados para aplicaciones de gestión.

## Objetivos

* Tiempo promedio de respuesta menor a 2 segundos.
* Operaciones CRUD optimizadas.
* Consultas eficientes a base de datos.

---

# RNF-03 Escalabilidad

La solución deberá permitir incorporar nuevas entidades y funcionalidades sin modificaciones significativas en la arquitectura existente.

## Ejemplos

* Usuarios.
* Roles.
* Productos.
* Ventas.
* Proveedores.

---

# RNF-04 Mantenibilidad

El código deberá estar organizado siguiendo buenas prácticas de desarrollo.

## Requisitos

* Principios SOLID.
* Nombres descriptivos.
* Separación por módulos.
* Código reutilizable.
* Documentación interna cuando corresponda.

---

# RNF-05 Disponibilidad

La API deberá encontrarse disponible para ser consumida por sistemas externos durante su operación normal.

---

# RNF-06 Persistencia

Toda la información registrada deberá almacenarse de forma persistente en una base de datos relacional.

## Tecnología

MySQL 8

---

# RNF-07 Seguridad

La arquitectura deberá permitir incorporar mecanismos de autenticación y autorización en futuras versiones.

## Posibles extensiones

* JWT.
* OAuth2.
* Control de acceso basado en roles.

---

# RNF-08 Validación de Datos

Toda solicitud recibida deberá ser validada antes de ejecutar reglas de negocio.

## Tecnología

Pydantic

---

# RNF-09 Documentación

La API deberá generar documentación técnica automáticamente.

## Herramientas

* OpenAPI
* Swagger UI
* ReDoc

## Endpoints

/docs

/redoc

---

# RNF-10 Observabilidad

La aplicación deberá registrar eventos relevantes para facilitar monitoreo y diagnóstico.

## Eventos

* Inicio de aplicación.
* Errores de ejecución.
* Errores de validación.
* Excepciones inesperadas.

---

# RNF-11 Compatibilidad

La API deberá comunicarse mediante HTTP y utilizar JSON como formato estándar de intercambio de información.

---

# RNF-12 Testing

La solución deberá permitir la ejecución de pruebas automatizadas.

## Herramienta

Pytest

## Alcance

* Servicios.
* Repositorios.
* Endpoints.

---

# RNF-13 Despliegue

La aplicación deberá poder ejecutarse tanto en entornos locales como en contenedores.

## Herramientas

* Docker
* Docker Compose

---

# RNF-14 Integración

La API deberá poder integrarse con servicios externos mediante HTTP REST.

## Integraciones previstas

* n8n
* Telegram Bot API
* Servicios de Inteligencia Artificial

---

# RNF-15 Bajo Costo Operativo

La solución deberá priorizar tecnologías open source y de libre disponibilidad, minimizando los costos de infraestructura y licenciamiento.
 
