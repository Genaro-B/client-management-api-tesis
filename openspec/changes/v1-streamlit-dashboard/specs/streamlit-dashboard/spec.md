## ADDED Requirements

### Requirement: Dashboard de métricas con cards de resumen
El sistema SHALL mostrar un dashboard con cards de resumen con las métricas principales obtenidas directamente de la base de datos.

#### Scenario: Muestra total de clientes
- **WHEN** el dashboard carga
- **THEN** se muestra una card con el total de clientes registrados

#### Scenario: Muestra clientes activos e inactivos
- **WHEN** el dashboard carga
- **THEN** se muestran cards con la cantidad de clientes activos y inactivos

#### Scenario: Muestra total de interacciones
- **WHEN** el dashboard carga
- **THEN** se muestra una card con el total de interacciones registradas

#### Scenario: Muestra interacciones de hoy y esta semana
- **WHEN** el dashboard carga
- **THEN** se muestran cards con interacciones del día actual y de los últimos 7 días

### Requirement: Timeline de interacciones (30 días)
El sistema SHALL mostrar un gráfico de línea con el conteo de interacciones por día para los últimos 30 días.

#### Scenario: Muestra timeline con 30 días
- **WHEN** el dashboard carga
- **THEN** se muestra un LineChart con 30 puntos (uno por día)
- **AND** los días sin interacciones aparecen con valor 0

### Requirement: Distribución de interacciones por fuente
El sistema SHALL mostrar un gráfico de torta con la distribución de interacciones agrupadas por `source`.

#### Scenario: Muestra PieChart por fuente
- **WHEN** el dashboard carga
- **THEN** se muestra un PieChart con cada source y su cantidad de interacciones

### Requirement: Top intents
El sistema SHALL mostrar un gráfico de barras con los 5 intents más frecuentes.

#### Scenario: Muestra top 5 intents
- **WHEN** el dashboard carga
- **THEN** se muestra un BarChart con los 5 intents más frecuentes ordenados descendente

### Requirement: Tabla de clientes con acciones CRUD
El sistema SHALL mostrar una tabla con todos los clientes y permitir crear, editar y eliminar desde el dashboard.

#### Scenario: Lista todos los clientes
- **WHEN** el dashboard carga la sección de clientes
- **THEN** se muestra una tabla con todos los clientes (ID, nombre, email, teléfono, DNI, estado, fecha)

#### Scenario: Crear un cliente nuevo
- **WHEN** el usuario completa el formulario de nuevo cliente y hace clic en Guardar
- **THEN** el cliente se crea en la base de datos y la tabla se actualiza

#### Scenario: Editar un cliente existente
- **WHEN** el usuario selecciona un cliente para editar y guarda los cambios
- **THEN** los datos del cliente se actualizan en la base de datos y la tabla se refresca

#### Scenario: Eliminar un cliente
- **WHEN** el usuario confirma la eliminación de un cliente
- **THEN** el cliente se elimina de la base de datos y la tabla se actualiza

### Requirement: Ver interacciones de un cliente
El sistema SHALL permitir seleccionar un cliente y ver sus interacciones asociadas.

#### Scenario: Muestra interacciones del cliente seleccionado
- **WHEN** el usuario selecciona un cliente de la tabla
- **THEN** se muestran las interacciones de ese cliente en una tabla aparte

### Requirement: Sidebar de navegación
El sistema SHALL tener un sidebar con navegación entre las secciones del dashboard.

#### Scenario: Navegación entre secciones
- **WHEN** el usuario hace clic en "Métricas" en el sidebar
- **THEN** se muestra la vista de métricas

#### Scenario: Navegación a clientes
- **WHEN** el usuario hace clic en "Clientes" en el sidebar
- **THEN** se muestra la vista de clientes con la tabla CRUD
