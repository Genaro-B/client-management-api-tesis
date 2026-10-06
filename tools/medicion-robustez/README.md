# Medición de robustez del Bot Router

Ejecuta el **`functionCode` real del nodo `Bot Router`** del flujo de n8n
(`Docs/flujos/Actual/v2-flujo-mejorado.json`) fuera de la plataforma y mide su
comportamiento ante mensajes que **no están** en el catálogo de reglas.

## Cómo se ejecuta

```bash
node tools/medicion-robustez/medir.js
```

No requiere Telegram, ni la API, ni n8n, ni conexión a la base, ni red. El
script inyecta dos stubs mínimos (`$input.first().json` y
`getWorkflowStaticData`) y ejecuta el mismo código de producción con Node. Por
eso los números son reproducibles en cualquier máquina con Node 18+ y no
dependen de infraestructura transitoria.

Escribe `resultados.json` con el detalle completo caso por caso.

## Qué mide

| Métrica | Definición |
|---|---|
| **Precisión** | Porcentaje de mensajes que rutean a la intención esperada. |
| **Cobertura del catálogo** | Porcentaje de las invocaciones del catálogo que el clasificador sigue alcanzando bajo mutación. |
| **Tasa de fallback** | Porcentaje de mensajes que caen en la rama por defecto (`"No entendí ese comando"`). |

Sobre dos conjuntos declarados en `mutaciones.js`:

1. **Auditoría de variantes documentadas** — las 16 variantes que la Tabla 6 de
   la tesis afirma reconocer, ejecutadas contra el código.
2. **Mutación sistemática** — 8 reglas mecánicas y deterministas (cortesía,
   puntuación, mayúsculas, tildes, reordenamiento, error tipográfico, plural,
   oración completa) aplicadas a las variantes ya reconocidas, para medir la
   brecha de generalización.

## Qué NO es esto

**No es un conjunto de validación independiente redactado por terceros.** Es una
*prueba de robustez por mutación sistemática*. La diferencia importa y hay que
declararla: los mensajes los genera un conjunto de reglas declaradas y
deterministas, no personas. Sirve para medir si el clasificador generaliza más
allá de lo que fue entrenado, y no reemplaza la validación por terceros.

## Limitación metodológica

Cada mensaje se evalúa con **estado conversacional limpio** (`modo = menu`,
carrito vacío). Se está midiendo la **capa de clasificación**, no el flujo de
extremo a extremo. El comportamiento dependiente de estado (selección de
producto, cantidades, validación de rango) se cubre aparte en la sección 3 del
script, que reproduce los casos de la Tabla 7 con su secuencia real.
