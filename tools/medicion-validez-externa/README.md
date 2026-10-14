# Medición validez externa

Propósito: conjunto independiente de 40 mensajes redactados sin conocimiento del catálogo, para medir comportamiento sobre inputs no diseñados.

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
