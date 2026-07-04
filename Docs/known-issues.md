# Known Issues

## CI: pytest exit code 4 en Ubuntu

- **Síntoma**: Los tests pasan localmente (Windows, Python 3.14, pytest 9.0.3) pero fallan en GitHub Actions con exit code 4 de pytest.
- **Causa**: Error interno de pytest durante la colección de tests en `backend/tests/`, específico del runner de Ubuntu.
- **Tracking**: Pendiente de resolución. Ver investigación en `openspec/` o preguntar al agente.
- **Workaround**: `python -m unittest discover` funciona, pero los tests usan fixtures de pytest.

## Streamlit: comando no reconocido en Windows

- **Síntoma**: `streamlit run app.py` → error "no se reconoce como programa"
- **Causa**: El ejecutable de Streamlit no está en el PATH de Windows
- **Solución**: Usar `python -m streamlit run app.py` en lugar de `streamlit run app.py`

---

## n8n: Importación de JSON falla con "unexpected end of input line 169"

- **Síntoma**: Al importar el JSON del flujo a n8n, aparece `unexpected end of input line 169`.
- **Causa**: Un brace `}` faltante en el `functionCode` del nodo **Bot Router**. Scripts de modificación automática (Python) borraron el cierre del `else-if` + bloque `DEFAULT` + línea de persistencia.
- **Solución**: Reemplazar solo el bloque de opción 7, no todo el `functionCode`. Verificar siempre `braces open == braces close`.
- **Estado**: ✅ RESUELTO — el archivo `Sistema de Automatizacion v2 - Simple.json` es la base estable.

## n8n: Clear Carrito llama a API que no existe / falla

- **Síntoma**: Al seleccionar opción 7 (finalizar compra), el nodo **Clear Carrito** (HTTP Request) muestra error de conexión.
- **Causa**: El Switch Router rutea por `accion = 'finalizar'` al nodo Clear Carrito, que hace `PUT /api/v1/clients/{id}/productos`. El backend puede no estar corriendo o el endpoint no está implementado para este caso.
- **Solución**: Cambiar `accion = 'finalizar'` por `accion = null` en la opción 7. Así el Switch Router cae al default (Telegram Send) y solo muestra el mensaje de éxito sin llamar a la API.
- **Estado**: ✅ RESUELTO (workaround para demo — pendiente implementar carrito real con API).

## n8n: Producto se agrega de a 1 (sin cantidad)

- **Síntoma**: Cada vez que se selecciona un producto, se agrega 1 unidad. Para comprar 5 hay que seleccionar el producto 5 veces.
- **Causa**: El flujo original no tenía estado de "esperando cantidad". Seleccionar un número de producto lo agregaba inmediatamente al carrito.
- **Solución**: Agregar estado `pendingProducto` en el `userState`. Al seleccionar un producto, se guarda en `pendingProducto` y se pregunta "¿Cuántas unidades querés?". El siguiente mensaje numérico se interpreta como cantidad.
- **Estado**: ✅ RESUELTO — flujo de 2 pasos: seleccionar producto → especificar cantidad.

## n8n: Carrito no se vacía al finalizar compra

- **Síntoma**: Después de opción 7 (finalizar compra), al volver a opción 6 (ver carrito), siguen apareciendo los productos anteriores.
- **Causa**: La opción 7 solo mostraba mensaje de éxito pero nunca limpiaba `userState.carrito`.
- **Solución**: Agregar `userState.carrito = [];` en el bloque de opción 7.
- **Estado**: ✅ RESUELTO.

---

## Pendientes para futuro

| # | Issue | Prioridad | Notas |
|---|-------|-----------|-------|
| 1 | **Carrito real con API** — que option 7 persista la compra en backend y vacíe el carrito vía API | Media | Ahora es simulado con `getWorkflowStaticData()` |
| 2 | **Keyboard buttons** — reemplazar entrada numérica por botones inline/reply | Baja | Mejora UX |
| 3 | **Confirmación antes de finalizar** — preguntar "¿Estás seguro?" antes de opción 7 | Baja | Evita finalizar por error |
| 4 | **Editar cantidad desde carrito** — poder cambiar cantidad de un producto ya agregado | Baja | Opción 6 mejorada |
| 5 | **Ver detalle de producto** — precio, stock, descripción antes de agregar al carrito | Baja | Opción de "Ver más" en catálogo |
| 6 | **Múltiples carritos / historial de compras** — separar carrito actual de compras anteriores | Baja | Para post-demo |
