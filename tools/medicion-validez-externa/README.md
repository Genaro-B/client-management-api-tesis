# Medición validez externa

Propósito: conjunto de 40 mensajes en lenguaje libre, redactados por el autor del trabajo (único redactor) sin derivarlos de los mensajes del catálogo implementado ni del código del nodo de enrutamiento, para medir el comportamiento del clasificador ante formulaciones no diseñadas. La independencia del conjunto es limitada: el autor diseñó el catálogo y el código del sistema.

## Cómo ejecutar

```bash
node tools/medicion-validez-externa/validez.js
```

## Salida

`tools/medicion-validez-externa/resultados-validez-externa.json`

Estructura:
- generado
- nota_metodologica
- total
- precision (conformes/total)
- tasa_fallback (fallback/total)
- cobertura (% de categorías esperadas con al menos un mensaje conforme; incluye fallback)
- detalle[]
- por_intencion
- fallos[]

## Método

- Cada mensaje evaluado con runner FRESH (estado limpio)
- Código real del Bot Router desde JSON
- Detección por huellas

## Herramienta y consigna original

- Herramienta: **OpenCode**, modelo **big-pickle** (proveedor `opencode`, variante `default`).
- Versión: la interfaz no expone un número de versión del modelo; por ese motivo no fue registrada.
- La consigna literal emitida en la sesión de generación (7 de octubre de 2026), reproducida en su idioma original, fue:

> Purpose: independent validation set — messages redacted WITHOUT knowledge of the catalog (fresh natural user phrasings, many with tildes/typos/colloquialisms), to measure how the router behaves on inputs it was not designed for. Create:
> - `tools/medicion-validez-externa/independientes.js` exporting `INDEPENDIENTES` = EXACTLY these 40 entries: { id: 'I1'..'I40', intencion_esperada (ONE of menu|comprar|catalogo|precios|asesor|otra|carrito|finalizar|fallback), mensaje }:

> Los 40 mensajes que continuaban en esa consigna son, textualmente, los que hoy se ejecutan en `independientes.js` y se registran en `resultados-validez-externa.json` (I1–I40). La herramienta transcribió ese listado al código y generó el arnés de medición; el redactor del conjunto fue el autor del trabajo, único redactor.
