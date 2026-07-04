# Product Catalog

## ADDED Requirements

### Requirement: Create product
The system SHALL allow creating a new product with nombre, precio, descripcion, stock, and categoria.

#### Scenario: Create product with all fields
- **WHEN** a POST request is sent to `/api/v1/products/` with valid `nombre`, `precio`, `descripcion`, `stock`, and `categoria`
- **THEN** the system SHALL return status 201 with the created product including an `id` and `fecha_registro`

#### Scenario: Create product fails without nombre
- **WHEN** a POST request is sent to `/api/v1/products/` without `nombre`
- **THEN** the system SHALL return status 422 with a validation error

#### Scenario: Create product fails with negative price
- **WHEN** a POST request is sent to `/api/v1/products/` with `precio` < 0
- **THEN** the system SHALL return status 422 with a validation error

#### Scenario: Create product fails with negative stock
- **WHEN** a POST request is sent to `/api/v1/products/` with `stock` < 0
- **THEN** the system SHALL return status 422 with a validation error

### Requirement: List products
The system SHALL allow listing active products with optional search, limit, and offset.

#### Scenario: List all active products
- **WHEN** a GET request is sent to `/api/v1/products/`
- **THEN** the system SHALL return status 200 with a list of active products

#### Scenario: List products with search filter
- **WHEN** a GET request is sent to `/api/v1/products/?q=limpieza`
- **THEN** the system SHALL return only products whose nombre or categoria contains "limpieza"

#### Scenario: List products with pagination
- **WHEN** a GET request is sent to `/api/v1/products/?limit=5&offset=10`
- **THEN** the system SHALL return at most 5 products, skipping the first 10

### Requirement: Get product by ID
The system SHALL allow retrieving a single product by its ID.

#### Scenario: Get existing product
- **WHEN** a GET request is sent to `/api/v1/products/1`
- **THEN** the system SHALL return status 200 with the product data

#### Scenario: Get non-existent product
- **WHEN** a GET request is sent to `/api/v1/products/9999`
- **THEN** the system SHALL return status 404

#### Scenario: Get soft-deleted product
- **WHEN** a GET request is sent to `/api/v1/products/1` and the product was soft-deleted
- **THEN** the system SHALL return status 404

### Requirement: Update product
The system SHALL allow partial updates to a product's fields.

#### Scenario: Update product price
- **WHEN** a PATCH request is sent to `/api/v1/products/1` with `{"precio": 1500.50}`
- **THEN** the system SHALL return status 200 with the updated product

#### Scenario: Update product fails with negative price
- **WHEN** a PATCH request is sent to `/api/v1/products/1` with `{"precio": -10}`
- **THEN** the system SHALL return status 422

#### Scenario: Update non-existent product
- **WHEN** a PATCH request is sent to `/api/v1/products/9999`
- **THEN** the system SHALL return status 404

### Requirement: Delete product (soft-delete)
The system SHALL allow soft-deleting a product by setting `activo` to false.

#### Scenario: Soft-delete existing product
- **WHEN** a DELETE request is sent to `/api/v1/products/1`
- **THEN** the system SHALL return status 204 and the product SHALL have `activo=false`

#### Scenario: Delete non-existent product
- **WHEN** a DELETE request is sent to `/api/v1/products/9999`
- **THEN** the system SHALL return status 404

### Requirement: List inactive products
The system SHALL allow listing soft-deleted products.

#### Scenario: List inactive products
- **WHEN** a GET request is sent to `/api/v1/products/inactive`
- **THEN** the system SHALL return status 200 with only inactive products

### Requirement: Restore product
The system SHALL allow restoring a soft-deleted product.

#### Scenario: Restore inactive product
- **WHEN** a PATCH request is sent to `/api/v1/products/1/restore`
- **THEN** the system SHALL return status 200 with the product having `activo=true`

#### Scenario: Restore active product
- **WHEN** a PATCH request is sent to `/api/v1/products/1/restore` and the product is already active
- **THEN** the system SHALL return status 200 (no-op)

#### Scenario: Restore non-existent product
- **WHEN** a PATCH request is sent to `/api/v1/products/9999/restore`
- **THEN** the system SHALL return status 404

### Requirement: Export products to Excel
The system SHALL allow exporting all active products to an Excel (.xlsx) file.

#### Scenario: Export products
- **WHEN** a GET request is sent to `/api/v1/products/export`
- **THEN** the system SHALL return status 200 with Content-Type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

### Requirement: Product catalog in Telegram bot
The Telegram bot SHALL display real product data when the user selects "Ver catálogo" (option 2) or "Consultar precios" (option 3).

#### Scenario: User selects "Ver catálogo"
- **WHEN** the user sends "2" in Telegram
- **THEN** the bot SHALL display a list of all active products with name, price, and stock

#### Scenario: User selects "Consultar precios"
- **WHEN** the user sends "3" in Telegram
- **THEN** the bot SHALL display a list of product names with their prices

#### Scenario: No products available
- **WHEN** the user selects "Ver catálogo" and there are no active products
- **THEN** the bot SHALL display "No hay productos disponibles en este momento."

#### Scenario: API is unreachable
- **WHEN** the user selects "Ver catálogo" and the API returns an error or timeout
- **THEN** the bot SHALL display "No pude consultar los productos. Intentalo de nuevo más tarde."
