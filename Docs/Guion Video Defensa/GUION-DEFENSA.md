# 🎬 GUION VIDEO — DEFENSA DE TESIS

**Título:** Diseño, modelización e implementación de un sistema de automatización de procesos basado en integración de servicios e inteligencia artificial en entornos de bajo costo

**Autor:** Genaro Busto — Legajo N.º 52610 — UTN FRM — TUP

**Resultado del jurado:** 9,15/10 · Aprobado con observaciones menores · Defensa habilitada

**Uso de este guion:** grabá tomando cada bloque de forma secuencial (sección "Qué mostrar" + "Qué decir"). No necesitás leer palabra por palabra: el guion da el mensaje clave de cada bloque y los datos exactos que tenés que mencionar. Duración total estimada: 12–15 minutos.

---

## ESTRUCTURA GENERAL DEL VIDEO (12–15 min)

| # | Bloque | Tiempo aproximado |
|---|--------|-------------------|
| 1 | Presentación y contexto | 1:30 |
| 2 | Problema y motivación | 2:00 |
| 3 | Hipótesis y objetivos | 1:30 |
| 4 | Solución: arquitectura del sistema | 3:00 |
| 5 | Demo en vivo | 2:30 |
| 6 | Resultados medidos | 2:30 |
| 7 | Por qué es viable (costo + modelo híbrido) | 1:30 |
| 8 | Cierre y defensa prevista | 1:30 |

---

## BLOQUE 1 — PRESENTACIÓN Y CONTEXTO (1:30)

**Qué mostrar:** pantalla con portada de la tesis / tu nombre.

**Qué decir:**

> Buenas, mi nombre es Genaro Busto, legajo 52610, de la Tecnicatura Universitaria en Programación. Mi trabajo final se titula: *"Diseño, modelización e implementación de un sistema de automatización de procesos basado en integración de servicios e inteligencia artificial en entornos de bajo costo"*.
>
> En los próximos minutos les voy a mostrar qué problema resuelve, cómo lo resolví, la evidencia de que funciona y por qué esta solución es viable y útil en la práctica.

---

## BLOQUE 2 — EL PROBLEMA Y LA MOTIVACIÓN (2:00)

**Qué mostrar:** diapositiva con las 3 barreras de las PyMEs frente a la automatización.

**Qué decir:**

> La automatización de procesos es hoy uno de los ejes centrales de la transformación digital. Reduce costos operativos y libera a las personas para tareas de mayor valor.
>
> El problema es que **las grandes herramientas de automatización no están al alcance de todos**. La bibliografía muestra tres barreras que dejan afuera a pequeñas empresas, emprendimientos y proyectos en etapas iniciales:
>
> 1. **Barrera económica:** las plataformas de automatización empresarial tienen costos de licenciamiento, implementación y mantenimiento que representan un porcentaje desproporcionado del presupuesto disponible.
> 2. **Barrera de infraestructura:** requieren servidores, configuraciones y equipos técnicos.
> 3. **Barrera de conocimiento:** implementarlas exige perfiles especializados que una PyME no puede sostener.
>
> (Cita de respaldo: Lacity y Willcocks, 2016; Venkiteela y Kalluri, 2025 — las barreras documentadas en la revisión de RPA en PyMEs.)
>
> La pregunta que guía mi trabajo entonces es: **¿es posible construir un sistema de automatización funcional combinando herramientas accesibles, sin depender de plataformas costosas?**

---

## BLOQUE 3 — HIPÓTESIS Y OBJETIVOS (1:30)

**Qué mostrar:** diapositiva con hipótesis + los 5 objetivos específicos resumidos en 3 ideas.

**Qué decir:**

> Mi hipótesis de trabajo fue la siguiente:
>
> **"Es técnicamente viable implementar un sistema de automatización de procesos mediante la integración de servicios accesibles y herramientas de inteligencia artificial de bajo costo, logrando precisiones aceptables en dominios acotados."**
>
> Para validarla me propuse cinco objetivos concretos:
>
> - [ ] Diseñar la arquitectura desacoplada del sistema.
> - [ ] Implementar la interpretación de solicitudes en lenguaje natural.
> - [ ] Implementar la capa de orquestación de procesos.
> - [ ] Medir el rendimiento y la precisión con datos reales.
> - [ ] Evaluar la viabilidad económica de la solución.
>
> Lo importante de esta hipótesis es que **es verificable**: definí umbrales de aceptación a priori (tiempo de respuesta, precisión y tasa de error) y después los confronto con datos reales.

---

## BLOQUE 4 — LA SOLUCIÓN: ARQUITECTURA DEL SISTEMA (3:00)

**Qué mostrar:** diagrama de arquitectura en pantalla (ir señalando cada capa).

**Qué decir:**

> La solución tiene cuatro componentes principales, todos de bajo costo y de código abierto:
>
> **1. La API REST (backend)** — desarrollada en **Python 3.13 con FastAPI**. Expone los servicios de gestión: clientes, productos, asignaciones e interacciones. Usa **SQLAlchemy** como mapeador objeto-relacional y **SQLite** como base de datos embebida: cero licencias, cero infraestructura.
>
> **(Micro-frase para defensa técnica — importante):** la elección de SQLite responde a los principios de bajo costo y simplicidad. El paradigma "local-first" (Kleppmann et al., 2019) prioriza que la organización sea dueña de sus datos por sobre la conveniencia de la nube. La migración a MySQL queda definida como evolución futura cuando el volumen lo requiera.
>
> **2. El frontend web** — desarrollado en **React + Vite**, con una interfaz de gestión para administradores: dashboard con métricas, alta de productos y clientes, asignaciones y seguimiento de interacciones. Diseñado con un sistema de diseño propio y soporte de modo oscuro.
>
> **3. El motor de orquestación** — **n8n**, herramienta de automatización de código abierto, auto-alojada. Es el "cerebro" que conecta los servicios: toma el mensaje del usuario, decide qué flujo ejecutar y dispara las acciones sobre la API.
>
> **4. El canal de interacción** — **Telegram Bot API**. Un bot con el que el usuario conversa en lenguaje natural y ejecuta operaciones: consultar clientes, crear contactos, pedir reportes.
>
> La clave del diseño es que **la capa de interpretación está desacoplada de la capa de orquestación**: el clasificador actual es determinístico (basado en reglas y un catálogo de intenciones), pero el contrato está definido para que en el futuro un modelo de lenguaje (LLM) lo reemplace sin tocar el resto del sistema. Este es el modelo híbrido que defiende el trabajo.

---

## BLOQUE 5 — DEMO EN VIVO (2:30)

**Qué mostrar:** capturas de pantalla del sistema funcionando (dashboard, creación de cliente/producto, chat del bot en Telegram, workflow de n8n).

**Qué decir (narrando sobre la demo):**

> Ahora veo el sistema en acción:
>
> - **Dashboard:** aquí se ven las métricas del negocio en tiempo real.
> - **Alta de producto:** creo un producto (por ejemplo: *Ladrillo Hueco 8x18x33*, $850,50, stock 100) y queda registrado al instante.
> - **Alta de cliente:** doy de alta a un cliente y le asigno una compra.
> - **Interacción vía Telegram:** una persona escribe en lenguaje natural al bot: *"quiero ver mis clientes"* o *"creame un cliente nuevo"*. El bot interpreta la intención, ejecuta el flujo en n8n, llama a la API y responde con el resultado.
> - **Workflow de n8n:** muestro el flujo real con sus nodos de enrutamiento por intención (Bot Router) y las llamadas a la API.

---

## BLOQUE 6 — RESULTADOS MEDIDOS (2:30)

**Qué mostrar:** las tablas de resultados (Tabla 4, 5 y 6 de la tesis) en pantalla, bien visibles.

**Qué decir:**

> El sistema no se defiende por sí mismo: lo defiendo con **datos medidos**. Metodológicamente definí la muestra, los instrumentos y la técnica; y el tamaño de muestra (n = 30 por endpoint) quedó justificado por el Teorema Central del Límite.
>
> **Resultado funcional:**
> - **128 casos de prueba automatizados sobre la API con 100% de éxito.**
> - **117 interacciones conversacionales sobre el catálogo, con precisión del 100% en las rutas predefinidas.**
> - Los 9 grupos de intención del catálogo reconocidos correctamente (Tabla 6).
>
> **Resultado de rendimiento (n = 30 por endpoint, Tabla 5):**
> - Los 5 endpoints evaluados dentro de los **umbrales de aceptación** de la hipótesis (menos de 5 segundos en consultas simples, menos de 10 en operaciones complejas).
> - **Intervalos de confianza al 95%** calculados sobre los tiempos de respuesta.
> - El análisis de coeficiente de variación muestra que los endpoints de lectura simple tienen mayor variabilidad relativa (CV > 100%) por valores atípicos y por la inicialización de SQLite; las operaciones de escritura son más estables (CV < 81%). Para robustez reporté también la **mediana** como métrica complementaria.
> - Tasa de errores HTTP 5xx inferior al 1% exigido.
>
> **Honestidad metodológica (esto suma muchísimo ante un tribunal):**
> - incluyo un análisis de **casos límite** (§5.7): por ejemplo, "quiero comprar jabón" no está en el catálogo y el sistema responde con el fallback. Reconozco la limitación: el 100% de precisión es **sobre el catálogo predefinido**, no sobre lenguaje libre. Eso es exactamente lo que hace verificable el sistema.

---

## BLOQUE 7 — POR QUÉ ES VIABLE (1:30)

**Qué mostrar:** comparativa de costos (auto-hospedado vs. plataformas).

**Qué decir:**

> La viabilidad es el corazón de la contribución:
>
> **Económica:** el prototipo completo opera con menos de **USD 50 anuales** en infraestructura auto-hospedada, frente a los miles de dólares anuales de licenciamiento de plataformas iPaaS empresariales (Lacity y Willcocks, 2016; Ajimati et al., 2025). La comparación es honesta: asumo la limitación de procesamiento paralelo y robustez ante fallos frente a esas plataformas.
>
> **Técnica:** todas las herramientas elegidas son de código abierto (FastAPI, n8n, SQLite, React), con documentación madura y sin dependencia de proveedores (vendor lock-in).
>
> **Evolutiva:** el modelo híbrido define la interfaz para sustituir el clasificador determinístico por un LLM. Este diseño anticipa la línea de trabajo documentada en la literatura de agentes autónomos (Wang et al., 2024; Yao et al., 2023 — ReAct). La escalabilidad está planificada: migración a MySQL cuando el volumen lo exija.

---

## BLOQUE 8 — CIERRE Y DEFENSA PREVISTA (1:30)

**Qué decir:**

> Mi conclusión es que la hipótesis quedó confirmada: **es viable implementar un sistema de automatización funcional con herramientas accesibles, logrando precisión y rendimiento dentro de umbrales definidos, a una fracción del costo de las alternativas empresariales.**
>
> El trabajo no se detiene acá: las líneas futuras incluyen incorporar el componente de LLM manteniendo el contrato de orquestación estable, ampliar el catálogo de intenciones, y evaluar despliegues multi-usuario.

**(Cierre opcional, si el formato lo pide:)**

> Muchas gracias por su atención, quedo a disposición para las preguntas.

---

## 📋 ANEXO A — LAS 5 PREGUNTAS PROBABLES DEL TRIBUNAL (preparar estas)

Extraídas del dictamen V3. Las hacés antes de grabar para no titubear:

1. **ReAct:** "Su modelo híbrido tiene correspondencia con el enfoque ReAct (Yao et al., 2023). ¿En qué se diferencia conceptualmente de un agente ReAct estándar?"
   - Respuesta clave: ReAct combina razonamiento ("Pensemos...") con acciones en un único bucle del LLM. Mi sistema separa la capa de interpretación (clasificador) de la capa de orquestación (flujos n8n), lo que hace el modelo determinístico, testeable y barato. El LLM, cuando se incorpore, reemplazará solo el clasificador manteniendo los flujos intactos.

2. **Marco de Wang (2024):** "¿Cómo se ubica su sistema en el marco de agentes LLM?"
   - Respuesta clave: Wang define dimensiones (construcción, memoria, planificación, acción). Mi sistema cubre planificación y acción (flujos de n8n); la memoria se implementa en la capa de persistencia (SQLite); quedan fuera las capacidades de razonamiento avanzado del LLM — es justamente la extensión futura.

3. **Precisión limitada al catálogo:** "Si un usuario expresa la misma intención de 10 formas no contempladas, ¿cuántas se reconocerían?"
   - Respuesta clave: el sistema reconocería solo las que matcheen el catálogo; las demás caen al fallback. La cobertura se mejora ampliando el catálogo con sinónimos y variantes, o incorporando el LLM. El criterio para saber cuándo el catálogo es suficiente es la tasa de fallback observada en producción.

4. **Métricas de clasificación:** "¿Por qué no usó precisión/recall/F1 por intención?"
   - Respuesta clave: en un clasificador determinístico, precision = recall = F1 = 1.0 por construcción sobre el catálogo (no hay falsos positivos posibles). Por eso reporté precisión de ejecución (intención vs. resultado ejecutado), que es la métrica que mide algo real en este sistema. Si se incorpora el LLM, ahí sí precision/recall/F1 pasan a ser las métricas correctas.

5. **SQLite con 50 usuarios:** "¿Qué cuellos de botella predice con 50 usuarios simultáneos?"
   - Respuesta clave: SQLite serializa escrituras → el síntoma típico a 50 usuarios concurrentes sería el bloqueo de escrituras (write contention). Lo cuantificaría con una prueba de carga (ej. locust) midiendo latencia p95 y % de operaciones encoladas antes de migrar. La migración está prevista: MySQL 8 con SQLAlchemy ya abstrae el cambio de motor.

---

## 📋 ANEXO B — DATOS CLAVE PARA TENER A MANO (cheat-sheet)

| Dato | Valor |
|---|---|
| Nota del jurado | 9,15/10 — aprobado con observaciones menores |
| Pruebas API | 128 casos, 100% éxito (Tabla 4) |
| Interacciones catálogo | 117 casos, precisión 100% en rutas (Tabla 6) |
| Muestra de rendimiento | n = 30 por endpoint (Tabla 5) |
| Umbral de aceptación | < 5 s simple / < 10 s complejo; error 5xx < 1% |
| Técnica de muestreo | TCL (Wohlin et al., 2012) |
| CV endpoints lectura | CV > 100% (outliers + init SQLite) → reporto mediana |
| CV endpoints escritura | CV < 81% |
| Costo prototipo | < USD 50/año vs. miles/año en iPaaS empresarial |
| Stack | Python 3.13 · FastAPI · SQLAlchemy · SQLite · n8n · React/Vite · Telegram Bot API |
| Arquitectura | En capas, desacoplada; categoría IA = reglas + catálogo; LLM extensión futura |
| Referencias puente | Lacity y Willcocks (2016, 2021) · Venkiteela y Kalluri (2025) · Wang et al. (2024) · Yao et al. (2023) · Kleppmann et al. (2019) |

---

**Regla de oro durante la grabación:** si el tribunal pregunta algo que supera lo probado, la respuesta correcta es reconocerlo y enmarcarlo como extensión futura. El dictamen premió exactamente esa honestidad intelectual (§5.7).