 # Esquema de Base de Datos

## Introducción

Este documento define la estructura lógica de la base de datos utilizada por la API de gestión de clientes.

---

# Tabla: clientes

## Descripción

Almacena la información principal de los clientes registrados en el sistema.

## Estructura

| Campo          | Tipo         | Restricciones      |
| -------------- | ------------ | ------------------ |
| id             | BIGINT       | PK, AUTO_INCREMENT |
| nombre         | VARCHAR(100) | NOT NULL           |
| apellido       | VARCHAR(100) | NOT NULL           |
| telefono       | VARCHAR(20)  | NULL               |
| email          | VARCHAR(255) | NOT NULL, UNIQUE   |
| fecha_registro | DATETIME     | NOT NULL           |
| activo         | BOOLEAN      | NOT NULL           |

---

# Índices

## UK_CLIENTE_EMAIL

```sql
UNIQUE(email)
```

---

# Reglas de Integridad

* El correo electrónico debe ser único.
* El nombre es obligatorio.
* El apellido es obligatorio.
* La fecha de registro es generada por el sistema.
* El cliente se crea activo por defecto.

---

# Estrategia de Eliminación

Se priorizará eliminación lógica mediante el campo:

```text
activo
```

permitiendo conservar el historial de información.

