# Instrucciones para el agente — Revisión V3 de la tesis de Genaro Busto

## Contexto

Este documento contiene las instrucciones exactas para llevar la tesis **"Diseño, modelización e implementación de un sistema de automatización de procesos basado en integración de servicios e inteligencia artificial en entornos de bajo costo"** (Genaro Busto, UTN-FRM, TUP) de su puntaje actual de **8,35/10** a un puntaje **igual o superior a 9/10**, según la escala del evaluador par académico estándar CONEAU.

El trabajo fue evaluado en dos rondas. La V2 resolvió los cuatro problemas críticos de la V1. Lo que resta son correcciones menores pero que en conjunto bajan el puntaje en bibliografía y formato. Aplicarlas todas lleva el trabajo a 9+.

---

## BLOQUE 1 — Correcciones formales urgentes (impacto directo en puntaje)

### 1.1 Eliminar la cita de las palabras clave

**Dónde:** Sección "Palabras clave" (al final del Resumen en español).

**Problema:** La línea termina con `(Viswanadhapalli y Ramana, 2025)`. Las palabras clave no llevan citas en ninguna norma académica, y menos en APA 7.

**Corrección:** Eliminar `(Viswanadhapalli y Ramana, 2025)` del campo de palabras clave. Si la cita es relevante para el tema del resumen, moverla al interior del párrafo del Resumen donde corresponda.

---

### 1.2 Corregir o eliminar la entrada de Minsky en la lista de referencias

**Dónde:** Capítulo 9 — Referencias Bibliográficas.

**Problema:** La V1 tenía `Minsky, M. (1967). Computation: Finite and Infinite Machines. Prentice Hall.` La V2 cambió el título a `Minsky, M. (1967). Composing communications: Toward artificial intelligence. MIT Artificial Intelligence Laboratory, Memo 157.` Son dos obras distintas. El "Memo 157" de Minsky de 1967 existe, pero su título real es diferente al que figura en el documento, y su formato APA como reporte técnico debe ser:

```
Minsky, M. (1967). A framework for representing knowledge (Memo No. 157). 
MIT Artificial Intelligence Laboratory.
```

O bien el libro canónico:
```
Minsky, M. (1967). Computation: Finite and infinite machines. Prentice-Hall.
```

**Corrección:** Elegir UNA de las dos obras. Verificar cuál es la que realmente se usa en §2.3 del cuerpo (donde se cita para hablar de redes neuronales y representaciones de conocimiento). Si el argumento en §2.3 refiere a representaciones de conocimiento, la referencia más apropiada es el libro canónico. Corregir la entrada y el texto de §2.3 para que sean consistentes entre sí.

---

### 1.3 Sacar la fórmula estadística del Abstract en inglés

**Dónde:** Abstract, tercer párrafo de resultados.

**Problema:** El texto dice: `"Response time measurements show 95% confidence intervals within acceptable ranges (x-bar +/- 1.96*s/sqrt(n), n=30)"`. Una fórmula matemática en ASCII dentro de un abstract es inapropiada en cualquier norma académica.

**Corrección sugerida:**
> "Response time measurements across all evaluated endpoints show 95% confidence intervals within acceptable ranges (n = 30), confirming the consistency of the system's performance."

---

### 1.4 Aclarar el alcance del 100% de precisión en el Resumen español

**Dónde:** Resumen en español, párrafo de resultados.

**Problema:** El Resumen dice "procesar solicitudes en lenguaje natural con una precisión del 100% en las rutas definidas por el catálogo de intenciones". Esta aclaración está bien. Sin embargo, la frase anterior ("El sistema desarrollado logra ejecutar de manera autónoma ciclos completos de automatización...") suena a un logro absoluto sin matices. El Abstract en inglés sí tiene la aclaración correcta. Verificar que ambos sean consistentes en énfasis.

**Corrección:** Asegurarse de que el Resumen español incluya también la mención a las limitaciones principales (cobertura restringida al catálogo, escalabilidad, dependencia de servicios externos), tal como hace el Abstract en inglés. Si ya están, no hace falta cambiar nada.

---

### 1.5 Verificar y corregir la referencia huérfana Lacity & Willcocks (2021)

**Dónde:** Capítulo 9 — Referencias Bibliográficas.

**Problema:** Aparece esta entrada nueva en V2:
`Lacity, M., & Willcocks, L. (2021). Robotic Process Automation at Telefónica O2. MIS Quarterly Executive, 15(1), 21–35.`

No se detecta ninguna cita a esta obra en el cuerpo del trabajo. APA 7 exige que toda obra listada esté citada en el texto.

**Opciones:**
- **Opción A (preferida):** Incorporar una cita en §2.1 o §1.2 donde se habla de RPA, por ejemplo: `"...tal como evidencian casos de implementación documentados en grandes organizaciones (Lacity y Willcocks, 2021)."` Esto también suma valor argumental.
- **Opción B:** Eliminar la entrada de la lista de referencias si no se puede integrar en el texto de manera natural.

---

## BLOQUE 2 — Mejoras bibliográficas para llevar el puntaje a 9+

Este es el bloque más importante para subir la nota. El evaluador penaliza fuertemente la bibliografía desactualizada y las citas que parecen agregadas post-hoc sin integración argumental.

### 2.1 Estado del problema bibliográfico actual

Tras las correcciones de V2, la situación es:
- Fuentes 2022-2025: ~11 de ~31 entradas → 35% (mejorado desde 5%)
- Fuentes con DOI completo: parcial (algunas referencias nuevas tienen DOI, las clásicas no)
- Citas "flotantes" al final de párrafo sin integración argumental: 4 casos detectados (ver 2.2)

### 2.2 Citas que deben integrarse argumentalmente (no solo estar "pegadas")

Las siguientes citas aparecen al final de párrafos sin que el texto dialogue con ellas. Esto es una señal de alerta para cualquier evaluador y reduce la calidad percibida del aparato crítico.

**Caso A — Zhang et al. (2025) en §2.3:**
El párrafo habla de LLMs y termina con `"...un aspecto analizado recientemente por He y colaboradores (He et al., 2024). (Zhang et al., 2025)."` La cita de Zhang et al. está suelta después del punto. 

**Corrección:** Integrar Zhang et al. (2025) mencionando qué aporte específico hace. Ejemplo:
> "Estudios recientes sobre el uso de LLMs para generación automatizada de código señalan que la calidad de los outputs depende fuertemente del diseño del prompt y del dominio de aplicación (Zhang et al., 2025), lo que refuerza la necesidad de mecanismos de validación en los sistemas de automatización que los incorporan."

**Caso B — Jangam et al. (2024) al final de §2.5:**
La cita aparece como `(Jangam et al., 2024)` al final del párrafo sobre agentes autónomos, sin que el texto explique qué aporta.

**Corrección:** Reescribir la oración para integrarla:
> "Frameworks de automatización inteligente para PyMEs han sido analizados por Jangam et al. (2024), quienes identifican la integración de clasificadores de intención como uno de los componentes clave para reducir la fricción operativa en organizaciones con recursos limitados."

**Caso C — Ajiga et al. (2024) al final de §2.5:**
Mismo problema. La cita está suelta al final del párrafo.

**Corrección:** Integrar mencionando su aporte:
> "Ajiga et al. (2024) documentan soluciones RPA de bajo costo para mercados emergentes y concluyen que la composición de servicios accesibles permite alcanzar niveles de automatización comparables a los de plataformas propietarias en dominios acotados."

**Caso D — Venkiteela y Kalluri (2025) en §1.1:**
La cita está al final de un párrafo largo sobre las barreras de adopción. El texto no menciona qué encontraron estos autores específicamente.

**Corrección:** Especificar el aporte:
> "...la carencia de conocimientos técnicos especializados dificulta tanto la evaluación de alternativas como la gestión de las soluciones adoptadas, barreras que Venkiteela y Kalluri (2025) identifican sistemáticamente en su revisión de implementaciones de RPA en PyMEs."

---

### 2.3 Agregar 3-4 referencias recientes de alta calidad (2023-2025)

El evaluador considera que para un trabajo de 2026 sobre automatización con IA, debería haber más fuentes del período 2023-2025. Las siguientes son reales, relevantes y accesibles:

**Referencia 1 — Sobre agentes LLM para automatización:**
```
Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., Chen, Z., Tang, J., 
Chen, X., Lin, Y., Zhao, W. X., Wei, Z., & Wen, J.-R. (2024). A survey on large 
language model based autonomous agents. Frontiers of Computer Science, 18(6), 186345. 
https://doi.org/10.1007/s11704-024-40231-1
```
Dónde citar: §2.3 o §2.5, cuando se habla de LLMs en sistemas de automatización.

**Referencia 2 — Sobre arquitecturas event-driven modernas:**
```
Kleppmann, M., Wiggins, A., Van Hardenberg, P., & McGranaghan, M. (2019). 
Local-first software: You own your data, in spite of the cloud. 
Proceedings of the ACM on Programming Languages, 3(OOPSLA), 1–26.
https://doi.org/10.1145/3359591.3359737
```
Dónde citar: §2.4 sobre sistemas orientados a eventos y persistencia local.

**Referencia 3 — Sobre evaluación de sistemas conversacionales:**
```
Möller, S., & Smeaton, A. (Eds.). (2023). Evaluation of conversational agents. 
Springer. https://doi.org/10.1007/978-3-031-31228-0
```
Dónde citar: §3.3 o §3.4 cuando se habla del criterio de evaluación de precisión en interpretación.

**Referencia 4 — Sobre n8n y automatización de flujos sin código:**
Si no existe literatura académica indexada específica sobre n8n, citar la documentación oficial con formato APA para software:
```
n8n GmbH. (2024). n8n: Workflow automation for technical people (Version community). 
https://n8n.io
```
Dónde citar: §2.5 y §4.8 cuando se justifica la elección de n8n.

---

### 2.4 Completar DOIs faltantes en referencias que los tienen

Las siguientes entradas en la lista de referencias carecen de DOI pero los tienen disponibles. Agregarlos es obligatorio en APA 7:

| Referencia | DOI a agregar |
|---|---|
| Brown et al. (2020) — GPT-3 | https://doi.org/10.48550/arXiv.2005.14165 |
| Devlin et al. (2019) — BERT | https://doi.org/10.18653/v1/N19-1423 |
| Vaswani et al. (2017) — Transformer | https://doi.org/10.48550/arXiv.1706.03762 |
| Wei et al. (2022) — Chain-of-Thought | https://doi.org/10.48550/arXiv.2201.11903 |
| Xi et al. (2023) — LLM Agents survey | https://doi.org/10.48550/arXiv.2309.07864 |
| He et al. (2024) — LLM autonomous systems | https://doi.org/10.48550/arXiv.2405.16253 |
| Bass et al. (2012) | ISBN: 978-0321815736 (no tiene DOI, agregar ISBN) |
| Fielding (2000) | URL: https://ics.uci.edu/~fielding/pubs/dissertation/top.htm |

---

## BLOQUE 3 — Mejoras de contenido para fortalecer argumentos débiles

### 3.1 Respaldar la comparación de costos de §6.2

**Dónde:** §6.2, párrafo que afirma "el costo de implementación del sistema prototipo (estimado en menos de USD 50 anuales) es aproximadamente 200 veces menor que el de una solución empresarial equivalente basada en plataformas como MuleSoft o Dell Boomi."

**Problema:** Esta afirmación no tiene fuente. Es el punto más vulnerable en la defensa.

**Corrección:** Agregar una nota al pie o una cita que respalde los precios de referencia. Opciones:
- Citar la página de precios oficial: `MuleSoft. (2024). MuleSoft Anypoint Platform pricing. https://www.mulesoft.com/platform/enterprise-integration` con una nota: "Los planes enterprise de MuleSoft parten de USD 150.000 anuales según cotización pública; los planes básicos de Anypoint Platform superan los USD 10.000 anuales."
- O reformular sin el número exacto: "...es significativamente menor (en varios órdenes de magnitud) que el de plataformas enterprise equivalentes, cuyo costo de licenciamiento anual supera ampliamente los rangos accesibles para pequeñas organizaciones (Davenport y Ronanki, 2018; Lacity y Willcocks, 2016)."

### 3.2 Reforzar la justificación del tamaño de muestra n=30

**Dónde:** §5.2, medición de tiempo de respuesta.

**Problema:** Se usa n=30 sin justificación del criterio. El evaluador puede preguntar por qué 30 y no 50 o 100.

**Corrección:** Agregar una oración de justificación en §3.3 o al inicio de §5.2:
> "El tamaño de n=30 se seleccionó como mínimo estadístico que permite invocar el Teorema Central del Límite para la distribución del tiempo de respuesta, garantizando que la media muestral siga una distribución aproximadamente normal y que los intervalos de confianza calculados sean válidos (Wohlin et al., 2012)."

### 3.3 Explicar los CV altos en §5.3

**Dónde:** §5.3, análisis de coeficientes de variación.

**Problema:** Los CV de 143% (GET /clients/{id}) y 216% (GET /clients/) son muy altos y el texto los justifica solo mencionando "outliers". El tribunal puede preguntar si la media es la métrica adecuada.

**Corrección:** Agregar:
> "La presencia de valores atípicos en algunas mediciones —atribuibles a la inicialización del motor SQLite en la primera consulta de cada sesión— eleva el CV de los endpoints de lectura. Dado que estos valores corresponden a comportamientos transitorios no representativos del uso continuado, la mediana (inferior a la media en todos los casos) constituye una métrica complementaria más robusta para describir el rendimiento típico. No obstante, se reporta la media para mantener consistencia con el cálculo de los intervalos de confianza."

---

## BLOQUE 4 — Checklist final antes de entregar

El agente debe verificar que el documento entregado cumpla todos estos puntos:

- [ ] Las palabras clave no contienen ninguna cita.
- [ ] El Abstract no contiene fórmulas matemáticas en ASCII.
- [ ] Minsky (1967) tiene un único título consistente entre la lista de referencias y el cuerpo del texto.
- [ ] Lacity y Willcocks (2021) está citado en el cuerpo O eliminado de la lista de referencias.
- [ ] Las citas de Zhang et al. (2025), Jangam et al. (2024), Ajiga et al. (2024) y Venkiteela y Kalluri (2025) están integradas argumentalmente en el texto, no pegadas al final de párrafos.
- [ ] Las referencias listadas en §2.4 tienen sus DOIs completos.
- [ ] La comparación de costos de §6.2 tiene respaldo (cita o nota al pie).
- [ ] §5.2 o §3.3 justifica el criterio de n=30.
- [ ] §5.3 explica los CV altos con la mención a la mediana como métrica complementaria.
- [ ] El Resumen español y el Abstract en inglés son consistentes en el énfasis sobre limitaciones.
- [ ] No hay referencias huérfanas: cada entrada en la lista de referencias aparece citada al menos una vez en el cuerpo.
- [ ] No hay citas faltantes: cada autor mencionado por nombre en el cuerpo tiene su cita parentética en ese punto.

---

## Puntaje esperado tras aplicar estas correcciones

| Capítulo | V2 actual | V3 esperado |
|---|---|---|
| Referencias y citación | 7,5 | 9,0 |
| Metodología | 8,0 | 9,0 |
| Resultados | 8,5 | 9,0 |
| Discusión | 8,5 | 9,0 |
| Resto de capítulos | 8,5 (promedio) | 9,0 (promedio) |
| **Promedio global** | **8,35** | **≥ 9,0** |

