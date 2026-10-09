# Instrucciones para el agente — Correcciones V4 de la tesis de Genaro Busto

## Contexto

La tesis fue evaluada oficialmente en V3 con calificación 6,8/10 y dictamen
"Aprobable con observaciones mayores — requiere correcciones antes de la defensa".
Este documento contiene las correcciones obligatorias ordenadas por prioridad.
El archivo de trabajo es el .docx de la V3.

---

## PROBLEMA 1 — CRÍTICO: La IA prometida no está implementada

Este es el problema más grave. El título, las palabras clave, el encabezado de
página y partes de la Discusión hablan de "inteligencia artificial", pero el sistema
implementado usa solo reglas determinísticas (pattern matching). El evaluador lo
detecta de inmediato.

**La solución elegida es el REENCUADRE (no requiere implementar código nuevo).**

### 1.1 Cambiar el título

**Título actual:**
> "Diseño, modelización e implementación de un sistema de automatización de
> procesos basado en integración de servicios e inteligencia artificial en
> entornos de bajo costo"

**Título propuesto:**
> "Diseño, modelización e implementación de un sistema de automatización de
> procesos basado en integración de servicios e interpretación de lenguaje
> natural en entornos de bajo costo, con arquitectura preparada para
> inteligencia artificial"

Cambiar en: portada, declaración de autoría, encabezado de página (que aparece
en las 93 páginas como "Automatización de Procesos con IA en Entornos de Bajo
Costo"), índice general, y cualquier otro lugar donde figure el título completo.

### 1.2 Cambiar las palabras clave

**Palabras clave actuales:**
> automatización de procesos, integración de servicios, inteligencia artificial,
> procesamiento de lenguaje natural, arquitectura desacoplada, bajo costo,
> orquestación, entornos digitales

**Palabras clave propuestas:**
> automatización de procesos, integración de servicios, interpretación de lenguaje
> natural, arquitectura orientada a eventos, arquitectura preparada para IA,
> bajo costo, orquestación, entornos digitales de pequeña escala

Cambiar también en el Abstract (Keywords).

### 1.3 Reformular la hipótesis (§1.4)

La hipótesis actual es una disyunción ("reglas O LLM") que se confirma con
cualquiera de las dos ramas y por eso no es contrastable. Reemplazarla por
una hipótesis única referida a lo que realmente se implementó:

**Reemplazar el párrafo actual de §1.4 por:**
> "Es técnicamente viable diseñar e implementar un sistema de automatización
> de procesos funcional, basado en la integración de servicios de bajo costo y
> en un componente de interpretación de lenguaje natural implementado mediante
> reglas determinísticas, que permita ejecutar de manera autónoma ciclos
> completos de automatización en entornos digitales de pequeña escala, con
> niveles aceptables de rendimiento, precisión —medida como conformidad con el
> catálogo de intenciones predefinido— y estabilidad. La arquitectura propuesta
> está diseñada para incorporar un componente adaptativo basado en modelos de
> lenguaje de gran escala como extensión futura, sin modificaciones estructurales."

### 1.4 Eliminar la segunda pregunta de investigación (§1.3)

La segunda pregunta ("¿En qué medida un componente de interpretación…") no
tiene objetivo específico propio ni resultado que la responda. Eliminarla o
convertirla en una línea de trabajo futuro dentro de §1.7.

### 1.5 Reescribir los párrafos contradictorios de §6.2

En §6.2 ("La tensión costo-capacidad-control") hay párrafos que describen el
comportamiento de un LLM como si estuviera en el sistema actual. Son remanentes
de la versión anterior. Identificar y reescribir en condicional todo párrafo
que afirme que el sistema desarrollado incorpora IA o que pierde control por
variabilidad de un modelo. Ejemplo de lo que debe cambiar:

**Texto actual a corregir (§6.2, párrafo sobre capacidad):**
> "en el sistema desarrollado, la incorporación del componente de inteligencia
> artificial es la decisión de diseño que más contribuye a ampliar la capacidad
> del sistema"

**Reemplazar por:**
> "en la versión extendida del sistema, la incorporación del componente de
> inteligencia artificial sería la decisión de diseño que más contribuiría a
> ampliar la capacidad, a costa de introducir variabilidad y dependencia de
> servicios externos"

**Texto actual a corregir (§6.2, párrafo sobre control):**
> "el sistema desarrollado [...] acepta un nivel de control reducido como
> consecuencia de la incorporación del componente de inteligencia artificial"

**Reemplazar por:**
> "el sistema desarrollado prioriza el control mediante la implementación
> determinística; la versión extendida con LLM sacrificaría parte de ese
> control a cambio de mayor cobertura semántica"

Revisar todo §6.2 y hacer el mismo ajuste en cualquier oración que use presente
de indicativo para hablar del LLM como parte del sistema actual.

### 1.6 Reescribir §8.3 en condicional

§8.3 ("Gestión de la dependencia de IA") recomienda "validar las respuestas del
modelo de lenguaje" como si existiera. Reescribir en condicional:

**Antes:** "se recomienda explorar la posibilidad de implementar mecanismos de
validación de las respuestas del modelo de lenguaje"

**Después:** "cuando se incorpore el componente LLM en la versión extendida,
se recomienda implementar mecanismos de validación de sus respuestas que
permitan detectar automáticamente las situaciones en que la salida no cumple
con los requisitos del flujo de automatización"

### 1.7 Renombrar "Capa de procesamiento inteligente" en §4.5

El evaluador señala que "capa de procesamiento inteligente" e "interpretación
semántica" son denominaciones engañosas para un pattern matching literal.

**Renombrar en todo el documento:**
- "Capa de procesamiento inteligente" → "Capa de interpretación de solicitudes"
- "interpretación semántica" → "interpretación de intenciones"
- Donde se use "semántica" para describir el componente actual, reemplazar por
  "léxica" o "basada en patrones"

Esto afecta: §4.5, el título de la sección 5.3, la Tabla 2, la Figura 4, y
cualquier mención en Resumen/Abstract.

### 1.8 Ajustar §7 (Conclusiones)

Las conclusiones sobreafirman sobre el papel de la IA. Revisar todo párrafo
que diga "la presente investigación demuestra que [algo sobre IA]" y
reescribirlo indicando que lo demostrado es la viabilidad del componente
determinístico, y que el modelo híbrido con IA es una propuesta con validación
parcial (solo la rama determinística fue evaluada).

---

## PROBLEMA 2 — ALTO: Cinco referencias no localizadas

El evaluador buscó estas cinco referencias y no las encontró. Si no se puede
acreditar cada una con DOI o URL verificable, deben eliminarse del documento
junto con las afirmaciones que sostienen.

### Verificar o eliminar cada una:

**a) Ajiga, Ndambiri y Bwisa (2024)**
- Revista: "International Journal of Automation and Computing, 21(1)"
- Problema: esa revista cambió de nombre a Machine Intelligence Research en 2022,
  por lo que un volumen 2024 con ese título es improbable. No tiene DOI.
- Acción: buscar el DOI real en Springer o en el sitio de la revista. Si no
  existe, ELIMINAR la referencia y la cita en §2.5.

**b) Venkiteela y Kalluri (2025)**
- Revista: "International Journal of Information Technology, 17(1)"
- Problema: no localizada. No tiene DOI.
- Acción: buscar DOI en Springer (ISSN 2511-2104). Si no existe, ELIMINAR
  la referencia. La cita está en §1.1 y puede reemplazarse con
  Ajimati et al. (2025) que sí está verificada.

**c) Jangam, Patel y Sharma (2024)**
- Revista: "Journal of Intelligent Systems, 33(2)"
- Problema: no localizada. No tiene DOI.
- Acción: buscar en De Gruyter (editor de esa revista). Si no existe,
  ELIMINAR la referencia y la cita en §2.5. Reemplazar la afirmación con
  Ajimati et al. (2025).

**d) Viswanadhapalli y Ramana (2025)**
- Revista: "Applied Sciences, 15(3), 1-28"
- Problema: Applied Sciences (MDPI) usa número de artículo, no rango de páginas
  "1-28". No tiene DOI.
- Acción: buscar en MDPI con los apellidos de los autores. Si no existe,
  ELIMINAR la referencia y la cita en §2.3.

**e) Zhang, Wang y Liu (2025)**
- Revista: "ACM Computing Surveys, 57(4)"
- Problema: datos genéricos. No tiene DOI.
- Acción: buscar en ACM Digital Library. Si no existe, ELIMINAR la referencia
  y la cita en §2.3. La afirmación sobre generación de código puede sustentarse
  con Wang et al. (2024) que sí está verificada.

### Correcciones adicionales de bibliografía:

- **Lacity & Willcocks (2021):** el evaluador indica que el volumen 15(1) de
  MIS Quarterly Executive corresponde a 2016, no a 2021. Verificar y corregir
  el año. Si es 2016, ya existe la entrada Lacity y Willcocks (2016) y se
  convierte en duplicado: unificar.

- **Las cinco referencias al final de la lista** (Ajiga, Jangam, Viswanadhapalli,
  Venkiteela, Zhang) están fuera de orden alfabético y sin sangría francesa.
  Una vez resueltas (con DOI o eliminadas), reordenar toda la lista
  alfabéticamente y aplicar sangría francesa a todas las entradas.

- **El Kamouchi et al. (2023):** aparece citado en el cuerpo a veces como
  "El Kamouchi et al." y a veces como "Kamouchi et al." — unificar a
  "El Kamouchi et al." en todo el documento.

- **Minsky (1967):** en §2.3 se lo presenta como pionero "sobre redes neuronales".
  La obra "Computation: Finite and Infinite Machines" trata computación y
  autómatas finitos, no redes neuronales. Corregir la afirmación: mencionar
  que Minsky es uno de los fundadores del campo de la IA en sentido amplio,
  o citar su trabajo de redes neuronales de 1969 ("Perceptrons") si ese es
  el aporte relevante.

- **Bass et al. (2012):** tiene ISBN en formato APA 7, que no lo requiere.
  Eliminar el ISBN de la entrada o dejarlo solo si se quiere por consistencia
  con otras entradas que no lo tienen — pero ser consistente en toda la lista.

---

## PROBLEMA 3 — ALTO: Cifras muestrales contradictorias

En §3.4 y §5.x hay números que no coinciden entre sí. El evaluador los listó
todos. Corregir eligiendo una versión y siendo consistente en TODO el documento.

### La versión correcta a usar:

- **Pruebas de API:** 128 casos, distribuidos en 9 grupos (los 8 funcionales
  más la prueba E2E). En §3.4 donde dice "siete grupos funcionales" corregir
  a "ocho grupos funcionales, más una prueba de integración E2E".

- **Pruebas conversacionales:** 117 casos distribuidos en 9 intenciones
  (las 8 del menú más la entrada no reconocida). Eliminar toda mención a
  "38 interacciones reales vía Telegram" y a "5 categorías de intención
  (consulta, compra, soporte, navegación y saludo)" — esa taxonomía no existe
  en el sistema implementado y contradice la Tabla 6. Si las 38 interacciones
  son un conjunto adicional distinto, describirlo por separado con su propia
  taxonomía, o eliminarlo.

- **Endpoints:** la Tabla C.1 y la Tabla 5 muestran 5 endpoints. En §3.4
  donde dice "128 pruebas que cubren los 12 endpoints" corregir a "128 pruebas
  que cubren la API completa, incluyendo los 5 endpoints principales medidos
  en la Tabla 5 y los endpoints de autenticación, métricas e integración".

- **Intenciones:** usar siempre "9 intenciones" (las 8 del menú más la entrada
  no reconocida) o "8 intenciones del menú más el fallback". Nunca "7" ni "5".
  Revisar §5.1, §5.3 y la Tabla 6.

---

## PROBLEMA 4 — ALTO: Los dos fragmentos de código se contradicen

El Fragmento 1 usa comparación por igualdad exacta (`msg === 'hola'`).
El Fragmento 2 usa `includes()` sobre subcadenas. Son incompatibles: con el
Fragmento 2, "quiero comprar jabón" sería reconocido (contradice Tabla 7) y
cualquier mensaje que contenga "1" sería clasificado como compra.

El evaluador pide que el código publicado sea el real exportado del flujo n8n.

**Acción:** elegir el fragmento que refleje el código real del Bot Router.
Si el real usa `===` (igualdad exacta), eliminar el Fragmento 2 o marcarlo
claramente como "versión simplificada ilustrativa". Si usa `includes()`,
alinear la Tabla 7 (el caso 1, "Quiero comprar jabón", sería reconocido
y el resultado cambia). También alinear la Tabla 6 con el código real:
si usa `===`, los alias "cuánto cuesta", "hablar con alguien" y "mis productos"
deben estar en el código con esa igualdad exacta o el 100% es incorrecto.

---

## PROBLEMA 5 — MEDIO: Índices y orden de figuras desfasados

El índice general tiene todos los capítulos desplazados entre 1 y 7 páginas
respecto de las páginas reales del PDF. La Figura 8 aparece antes que la
Figura 7. Las Tablas 6 y 7 aparecen después de las tablas de Anexos en el
índice. La sección §5.7 no figura en el índice.

**Acción:** regenerar ambos índices (General y de Figuras y Tablas) después
de aplicar todos los cambios, para que reflejen la paginación real final.
Agregar §5.7 al índice. Mover la Figura 8 a después de la Figura 7 en el
cuerpo del texto.

---

## PROBLEMA 6 — MEDIO: Resumen y Abstract no son equivalentes

El Resumen español menciona "< 15 ms" y "128 pruebas" que el Abstract no tiene.
El Abstract menciona CV altos que el Resumen no tiene. Deben decir lo mismo.

**Acción:** usar el Abstract como base (está más completo) y hacer que el
Resumen español sea su traducción fiel. Verificar que ambos mencionen:
- 128 pruebas funcionales automatizadas
- Tiempos de respuesta inferiores a 15 ms
- Precisión del 100% en las rutas del catálogo de intenciones
- Las tres limitaciones principales (cobertura restringida, escalabilidad,
  dependencia de servicios externos)

---

## PROBLEMA 7 — MEDIO: Otras correcciones técnicas menores

### 7.1 Cita a Gamma et al. (1994) en §4.5
El texto atribuye a Gamma et al. (1994) el "patrón Strategy" para el
clasificador por reglas. El clasificador del Fragmento 1 no implementa el
patrón Strategy (que requiere interfaz intercambiable con múltiples
implementaciones concretas). Eliminar la cita o reformular: "siguiendo
el principio de encapsulamiento de la lógica de clasificación, compatible
con el patrón Strategy (Gamma et al., 1994) para una futura extensión".

### 7.2 Licencia de n8n en Tabla 1
La Tabla 1 dice "código abierto (Sustainable Use License)". El evaluador
señala que esa licencia no es de código abierto en sentido OSI (es
fair-code). Corregir a: "fair-code (Sustainable Use License)" o
"código fuente disponible (licencia Sustainable Use, no OSI)".

### 7.3 Trigger de Telegram en Tabla B.1
La Tabla B.1 describe el trigger como "webhook de tipo polling". Webhook y
polling son mecanismos mutuamente excluyentes. Verificar cuál usa n8n
en el flujo real y corregir: si es polling, decir "polling"; si es webhook,
decir "webhook".

### 7.4 Backoff exponencial en Anexo C
El Anexo C afirma "reintento con backoff exponencial en el conector de
mensajería" pero ningún nodo de la Tabla B.1 lo implementa. Eliminar la
afirmación o agregar el nodo correspondiente a la Tabla B.1.

### 7.5 Tildes en rótulos de figuras
Las siguientes figuras tienen tildes faltantes en sus rótulos. Corregir:
- "documentacion" → "documentación"
- "metricas" → "métricas"
- "analiticas" → "analíticas"
- "Interaccion" → "Interacción"
- "Analisis" → "Análisis"
- "automatizacion" → "automatización"

### 7.6 Fuente de figuras y tablas
Ninguna figura ni tabla incluye "Fuente: elaboración propia". Agregar al
pie de cada figura y tabla que sea de elaboración propia.

### 7.7 Tabla 7 con doble título
La Tabla 7 tiene dos rótulos distintos seguidos. Dejar solo uno:
"Análisis de casos límite del Bot Router".

### 7.8 Título en metadatos del PDF
El nombre interno del archivo todavía dice
"Tesis_Final_UTNV2 - VERSION FINAL V3.docx". Al exportar el PDF final,
corregir el nombre del archivo a "Tesis_Final_UTN_Busto_V4.pdf" o similar.

### 7.9 Firma del autor
La firma en la Declaración de Autoría dice "Genaro Busto." con punto final.
Eliminar el punto.

### 7.10 §3.5 incompleto
§3.5 anuncia un procedimiento de cinco etapas pero desarrolla solo las
tres primeras. Agregar las etapas 4 (implementación y validación del
prototipo) y 5 (análisis de resultados y formulación de conclusiones)
con una descripción de 3-4 líneas cada una, coherente con lo que efectivamente
se hizo según los capítulos 4 y 5.

### 7.11 Referencia a "capítulo de especificaciones" en §5.1
§5.1 dice "los requisitos funcionales definidos en el capítulo de
especificaciones". Ese capítulo no existe. Reemplazar por "los requisitos
funcionales definidos en §1.5 (objetivos específicos) y §3.3 (variables
e indicadores)".

### 7.12 Tabla 7, Caso 3: condición de prueba
El caso 3 de la Tabla 7 supone un catálogo de 3 productos, pero la API
devuelve "total: 7" según el Anexo E. Aclarar en la nota de la tabla:
"este caso fue evaluado con un catálogo de prueba de 3 productos para
simular una selección fuera de rango; el catálogo de producción tiene 7."

---

## CHECKLIST FINAL antes de entregar la V4

- [ ] Título cambiado en portada, encabezado de página, índice y metadatos
- [ ] Palabras clave actualizadas en Resumen y Abstract (Keywords)
- [ ] Hipótesis única y contrastable en §1.4
- [ ] Segunda pregunta de investigación eliminada o movida a trabajos futuros
- [ ] §6.2 reescrito: LLM en condicional, no en presente
- [ ] §8.3 reescrito: LLM en condicional
- [ ] "Capa de procesamiento inteligente" renombrada en todo el documento
- [ ] Conclusiones (§7) ajustadas: no sobreafirman sobre IA
- [ ] Las 5 referencias problemáticas: tienen DOI verificable O fueron eliminadas
- [ ] Lacity & Willcocks: año verificado y corregido
- [ ] Lista de referencias en orden alfabético con sangría francesa uniforme
- [ ] "El Kamouchi" unificado en todas las citas
- [ ] Minsky: descripción de su obra corregida
- [ ] Cifras muestrales unificadas: 128 pruebas / 9 grupos / 117 conversacionales
      / 9 intenciones / sin mención a "38 interacciones" ni "5 categorías"
- [ ] Un solo fragmento de código alineado con el comportamiento real de la Tabla 6
- [ ] Índice General regenerado con páginas reales
- [ ] Índice de Figuras y Tablas regenerado y con §5.7
- [ ] Figura 8 movida a después de Figura 7 en el cuerpo
- [ ] Resumen y Abstract equivalentes en contenido
- [ ] Tabla 7 con un solo título
- [ ] Tildes en rótulos de figuras corregidas
- [ ] "Fuente: elaboración propia" en todas las figuras y tablas
- [ ] Licencia de n8n corregida a "fair-code"
- [ ] Trigger de Telegram: webhook O polling (no ambos)
- [ ] Backoff exponencial: eliminado o con nodo en Tabla B.1
- [ ] Cita a Gamma et al. en §4.5 corregida
- [ ] §3.5 con las 5 etapas completas
- [ ] §5.1 sin referencia a "capítulo de especificaciones"
- [ ] Tabla 7 Caso 3 con nota sobre el catálogo de prueba
- [ ] Firma sin punto final
- [ ] Nombre del archivo PDF corregido
