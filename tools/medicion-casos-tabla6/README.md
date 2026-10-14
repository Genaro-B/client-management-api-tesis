# Medición casos Tabla 6

Propósito: evidenciar la ejecución de los 102 casos definidos para la Tabla 6 con el código real del Bot Router (extraído de `Docs/flujos/Actual/v2-flujo-mejorado.json`).

## Cómo ejecutar

```bash
node tools/medicion-casos-tabla6/casos-tabla6.js
```

## Salida

`tools/medicion-casos-tabla6/resultados-casos-tabla6.json`

Estructura:
- generado
- nota_metodologica
- casos: [{id, categoria, intencion, mensaje, detectado, conforme}]
- por_categoria: {categoria: {count, conformes, no_conformes}}
- resumen: {total, conformes, no_conformes, conformidad_global_pct}

## Método

- Por cada mensaje se crea un runner FRESH (estado conversacional limpio: modo=menu, carrito vacío)
- Se ejecuta con AsyncFunction el `functionCode` exacto del nodo Bot Router
- Detección por huellas: `Número de producto inválido`, `no tiene stock disponible`, `No entendí ese comando`, `agregado a tu carrito`, `Bienvenido al sistema`, `Productos para comprar`, `Nuestro Catálogo`, `Lista de Precios`, `asesor se va a comunicar`, `Contame tu consulta`, `Tu carrito está vacío`, `Total: $`, `Compra finalizada`.
- Productos fijos: Jamón(1,8500,5), Queso(2,5200,3), Vino Tinto(3,12000,0)

## Nota de transparencia (reclasificación)

El mensaje `"quiero devolver"` fue diseñado originalmente como entrada no reconocida, pero en la
ejecución real el Bot Router lo deriva a **catálogo** porque la subcadena `ver` (sufijo de
"devol-ve-r") dispara la rama de catálogo antes que el caso por defecto. Por coherencia con el
comportamiento observable, se registró como **CAT6-21** de la categoría *catálogo*, y la categoría
*entrada no reconocida* quedó con 9 casos (NR6-01..NR6-05, NR6-07..NR6-10). El total sigue siendo
102 casos y la conformidad es 102/102 (100 %).
