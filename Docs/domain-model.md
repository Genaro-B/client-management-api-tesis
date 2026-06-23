# Modelo de Dominio

## Introducción

Este documento define las entidades de negocio administradas por la API REST del sistema.

El objetivo principal de la API es proporcionar operaciones de gestión de clientes que puedan ser consumidas por sistemas externos, flujos de automatización y aplicaciones de terceros.

---

# Entidad: Cliente

## Descripción

Representa una persona registrada dentro del sistema sobre la cual se realizan operaciones de alta, consulta, modificación y eliminación.

## Atributos

| Campo         | Tipo     | Obligatorio | Descripción                      |
| ------------- | -------- | ----------- | -------------------------------- |
| id            | Long     | Sí          | Identificador único autogenerado |
| nombre        | String   | Sí          | Nombre del cliente               |
| apellido      | String   | Sí          | Apellido del cliente             |
| telefono      | String   | No          | Número telefónico                |
| email         | String   | Sí          | Correo electrónico               |
| fechaRegistro | DateTime | Sí          | Fecha de creación del registro   |
| activo        | Boolean  | Sí          | Estado lógico del cliente        |

---

# Reglas de Negocio

## RN-CLI-01

El nombre es obligatorio.

## RN-CLI-02

El apellido es obligatorio.

## RN-CLI-03

El correo electrónico es obligatorio.

## RN-CLI-04

No podrán existir dos clientes con el mismo correo electrónico.

## RN-CLI-05

La fecha de registro será generada automáticamente por el sistema.

## RN-CLI-06

Los clientes se crearán con estado activo por defecto.

## RN-CLI-07

La eliminación de clientes podrá realizarse mediante eliminación lógica utilizando el campo activo.

---

# Operaciones de Negocio

La API deberá permitir las siguientes operaciones:

* Registrar cliente.
* Consultar cliente por identificador.
* Consultar cliente por correo electrónico.
* Obtener listado de clientes.
* Actualizar información de cliente.
* Desactivar cliente.
* Eliminar cliente.

---

# Consideraciones de Persistencia

La entidad Cliente será almacenada en una base de datos relacional.

La clave primaria será autogenerada.

El correo electrónico deberá poseer una restricción de unicidad.

Se implementarán índices sobre los campos de búsqueda frecuente para optimizar consultas.
