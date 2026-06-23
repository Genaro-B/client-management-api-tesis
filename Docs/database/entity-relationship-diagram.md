# Diagrama Entidad Relación

## Versión Inicial

```mermaid
erDiagram

    CLIENTES {
        BIGINT id PK
        VARCHAR nombre
        VARCHAR apellido
        VARCHAR telefono
        VARCHAR email UK
        DATETIME fecha_registro
        BOOLEAN activo
    }
```

---

## Descripción

La primera versión del sistema utiliza una única entidad principal denominada Cliente.

La arquitectura deberá permitir la incorporación futura de nuevas entidades sin afectar significativamente la estructura existente.

Posibles extensiones:

* Usuario
* Rol
* Producto
* Venta
* Interacción
* Proveedor
 
