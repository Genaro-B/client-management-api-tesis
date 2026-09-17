# Tesis — Flujo de trabajo: SDD + iteración continua con Claude

Documenta **cómo se produjo la tesis** a lo largo de las iteraciones (V1 → V2 → V3) y el mecanismo de revisión que permite cerrar cada ciclo con una devolución de un "jurado".

## Resumen del approach

La tesis **no se escribió de una sola pasada**. Se construyó con el mismo espíritu de los flujos de desarrollo del repo (Spec-Driven Development, OPSX):

1. Se redacta una versión del documento.
2. Un **agent/Claude en rol de jurado académico** emite una *devolución* (dictamen formal) con nota por capítulo, observaciones y preguntas de defensa.
3. Un **agent editor** (yo) verifica cada observación contra el documento real, aplica las correcciones con scripts de `python-docx` sobre una copia temporal, y valida con un checklist automático antes de reemplazar el original.
4. La versión corregida se copia a `Docs/Entrega Final/`.
5. El jurado vuelve a evaluar. Se itera hasta alcanzar el objetivo (≥ 9/10).

## El ciclo de iteración

```
[Versión N del documento]
          │
          ▼
Jurado (Claude) ──► Dictamen (informe con nota + observaciones + preguntas)
          │
          ▼
Agent editor: verificar cada observación contra el .docx real (nunca asumir)
          │
          ▼
Aplicar correcciones en copia temporal (python-docx, solo texto)
          │
          ▼
Checklist automático (presencias/ausencias + checklist de 12-13 puntos del jurado)
          │
          ▼
Reemplazar original + copiar a Docs/Entrega Final/
          │
          ▼
Jurado evalúa la versión siguiente ──► (iterar o APROBADO)
```

## Principios que se respetaron en cada ronda

- **Verificar, nunca asumir**: cada observación del dictamen se contrasta con el texto real del document (índice de párrafo mediante) antes de tocarlo. Hubo un caso donde el jurado marcó como pendiente algo que ya estaba corregido (Lacity & Willcocks, 2021, Obs. 3 del dictamen V3) — se confirmó en el `.docx` y no se modificó nada.
- **Backup obligatorio**: antes de cada edición queda una copia del documento (`BACKUP_*.docx`). Las correcciones se aplican sobre una copia **temporal** y solo se reemplaza el original si el checklist pasa.
- **Edición de texto únicamente con python-docx**: tablas e imágenes (13 figuras y 13 tablas) quedan intactas. Los párrafos se reescriben en `run[0]` y se limpian los demás runs (todos tenían formato uniforme).
- **Checklist automático**: cada ronda termina con un script que valida presencias (citas integradas, DOIs, justificaciones) y ausencias (caracteres corruptos, fórmulas ASCII, citas colgantes).

## Estructura de archivos (carpeta `Docs/`)

| Archivo | Rol |
|---|---|
| `Devoluciones + archivo de tesis/Tesis_Final_UTNV2 (1).docx` | Documento de trabajo actual |
| `Devoluciones + archivo de tesis/*.BACKUP*.docx` | Copias de seguridad por ronda |
| `Devoluciones + archivo de tesis/nuevo informe -claude.txt` | Devolución V2 (nota 8,35) |
| `Devoluciones + archivo de tesis/dictamen_v3_tesis_busto.pdf` | Devolución V3 (nota 9,15) |
| `Entrega Final/` | Versiones listas para evaluación del jurado |
| `instrucciones_agente_tesis_v3.md` | Receta de correcciones de la ronda V3 |
| `referencias_recientes_tesis_v3.md` | Referencias APA verificadas + DOIs |
| `CHANGES_SUMMARY.md` | Resumen de cambios de la parte de código |

## Estado actual

- **Devolución V3**: promedio **9,15** — *"Aprobado con observaciones menores. Defensa habilitada sin restricciones."*
- Observaciones de formato APA aplicadas (separador `y` → `&` en 5 referencias; volumen/páginas de Calvaresi).
- Próximo ciclo: preparación de la **defensa oral** (el dictamen V3 incluye 5 preguntas probables).

## El SDD aplicado también a la tesis

Aunque OpenSpec se usa formalmente en el código (changes `v3` y `v4` del bot y de imagen de productos), el mismo patrón mental se aplicó al documento:

| Fase SDD | Equivalente en la tesis |
|---|---|
| Spec (requerimiento) | Observaciones del dictamen (criterios de aceptación) |
| Design (cómo) | Instrucciones/receta por ronda + verificación de contexto |
| Apply (implementar) | Edición con scripts sobre copia temporal |
| Verify (validar) | Checklist automático de 12-13 puntos + diff de párrafos |
| Archive (cerrar ciclo) | Copia a `Entrega Final/` y nueva iteración con el jurado |