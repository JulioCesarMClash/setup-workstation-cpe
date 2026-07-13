---
name: jira-evidence-formatter
description: >
  Toma la evidencia técnica de un ticket Jira y la convierte en una descripción
  clara, estructurada y comprensible para cualquier persona sin conocimientos técnicos.
  Incluye indicaciones de qué imágenes o diagramas adjuntar.
  Ahora soporta auto-posting del comentario a Jira (Paso 5) cuando se provee ticket_key,
  y mirror a Obsidian (Paso 5b, opcional).
license: Apache-2.0
metadata:
  author: julio-martinez
  version: "2.0"
  tier: MID-HIGH
  model: claude-sonnet-4-6
  obsidian_template: BOVEDA MCP CLAUDE-OBSIDIAN/900_TEMPLATES/JIRA-Ticket-Evidencia.md
  related_skills:
    - jira-ticket-hierarchy
    - ponytail
    - unified-docs-pipeline
---

## Modos de operación

| Modo | Condición | Comportamiento |
|---|---|---|
| **Standalone** | Sin `ticket_key` | Ejecuta Pasos 1–4; entrega markdown para copiar manualmente; Paso 5 omitido |
| **Pipeline** | Con `ticket_key` | Ejecuta Pasos 1–5; postea comentario a Jira automáticamente; retorna `comment_url` |

Para auto-post, proveer `ticket_key` (ej. `DAT-42`) al invocar el skill o desde `unified-docs-pipeline`.

## Cuándo usar este skill

Úsalo cuando:
- Se solicite crear o actualizar la descripción de un ticket Jira con evidencia.
- El usuario proporcione logs, datos, capturas o resultados técnicos que deben ser comunicados a stakeholders no técnicos.
- Se necesite formatear una descripción Jira con secciones de "antes / después", métricas, y sugerencias de imágenes.

---

## Reglas críticas

1. **Lenguaje no técnico obligatorio** — Elimina jerga de código, nombres de funciones, paths de archivos y términos de base de datos de las secciones de texto. Si un detalle técnico es esencial, ponlo en un bloque `> Nota técnica:` separado y claramente etiquetado.
2. **Evidencia siempre soportada con imagen** — Por cada afirmación sobre un estado del sistema (antes/después, error, resultado), incluir una línea `📸 Imagen sugerida:` con una descripción exacta de qué capturar o mostrar.
3. **Nunca inventar métricas** — Si el usuario no provee datos numéricos, marcar la celda de la tabla con `[pendiente]` y pedir el dato explícitamente.
4. **Criterios de aceptación en lenguaje de usuario** — Cada criterio debe poder ser verificado visualmente por alguien que no sea programador.
5. **Resumen ejecutivo máximo 2 oraciones** — Debe responder: "¿qué pasó?" y "¿por qué importa?".
6. **Gate Ponytail antes de cada sección opcional** — Antes de agregar una nota técnica, imagen sugerida extra o fila de métrica, preguntar: "¿esto le sirve al lector no técnico, o es relleno?" Si no aporta, omitir la sección entera en vez de dejarla con texto genérico. Mismo principio que [[ponytail]], aplicado a texto en vez de código.

---

## Proceso de ejecución

### Paso 1 — Recolectar inputs del usuario

Antes de generar el ticket, verificar que tienes:

| Input requerido | Si falta... |
|---|---|
| **Ticket ID** | Usar `[TICKET-??]` como placeholder |
| **Título del ticket** | Derivar del contexto o preguntar |
| **Tipo** | Bug / Feature / Mejora / Configuración / Despliegue |
| **Descripción técnica o contexto** | Obligatorio — sin esto, no generar |
| **Evidencia** (logs, datos, resultado) | Obligatorio — puede ser texto, tabla, número |
| **Estado antes** | Preguntar si no se provee |
| **Estado después** | Preguntar si no se provee |

Si falta el contexto técnico o la evidencia, **detener y preguntar** antes de continuar.

---

### Paso 2 — Clasificar la evidencia recibida

Identificar qué tipo de evidencia proveyó el usuario:

| Tipo de evidencia | Qué hacer |
|---|---|
| Logs / stacktrace | Resumir el error en una oración simple; sugerir captura del log en la consola |
| Datos numéricos / tabla | Colocar en la tabla de métricas; sugerir gráfica de comparación |
| Descripción textual | Reformular sin jerga; sugerir screenshot del flujo afectado |
| Resultado de test / pytest | Traducir a "se verificó que X funciona correctamente"; sugerir captura del output del test |
| Sin evidencia | Marcar como `[pendiente]` y listar exactamente qué se necesita |

---

### Paso 3 — Generar el output usando el template

Completar cada campo del template `JIRA-Ticket-Evidencia.md`:

#### Resumen ejecutivo
- Máximo 2 oraciones.
- Estructura: `"Se [acción realizada] para [resultado/propósito]. Esto [impacto en el usuario o sistema]."`.
- Ejemplo correcto: *"Se corrigió un problema que causaba datos duplicados en el reporte mensual. Ahora los totales mostrados son exactos y confiables."*
- Ejemplo incorrecto: *"Se eliminaron los registros duplicados del query de fetch_gender_rows en la capa de repositorio PostgreSQL."*

#### ¿Por qué importa?
- Responder desde la perspectiva del negocio o del usuario final.
- Evitar mencionar capas técnicas.
- Mencionar qué pasaría si NO se hubiera hecho esto.

#### ¿Qué se realizó?
- Lista numerada, cada ítem en lenguaje de acción simple.
- Máximo 6 ítems. Si hay más, agrupar.
- Formato: verbo en pasado + objeto + resultado breve.
- Ejemplo correcto: *"1. Se identificó el origen del error en el reporte de febrero."*
- Ejemplo incorrecto: *"1. Se debuggeó el método fetch_gender_rows y se removió el join incorrecto en la capa de infraestructura."*

#### Evidencia: estado anterior
- Describir en prosa simple lo que el usuario o sistema veía/recibía antes.
- Si hay números, incluirlos.
- Agregar línea `📸 Imagen sugerida:` con descripción exacta de qué capturar.

#### Evidencia: estado actual
- Describir en prosa simple el resultado esperado y verificado.
- Agregar línea `📸 Imagen sugerida:` con descripción exacta.

#### Tabla de métricas
- Completar solo con datos reales.
- Si no hay datos, marcar `[pendiente]` y listarlo en notas.
- Sugerir un diagrama si los números lo justifican.

**Tipos de imagen/diagrama a sugerir según contexto:**

| Situación | Imagen o diagrama sugerido |
|---|---|
| Comparación de números antes/después | Gráfica de barras dobles (antes vs después) |
| Flujo de usuario corregido | Diagrama de flujo (antes) vs (después) |
| Error en pantalla | Captura de pantalla del mensaje de error original |
| Resultado exitoso | Captura de pantalla del sistema funcionando correctamente |
| Datos en tabla / reporte | Captura del reporte o vista de datos |
| Tests pasando | Captura del output del terminal con ✓ verde |
| Arquitectura modificada | Diagrama de componentes simple (cajas y flechas) |
| Despliegue / CI | Captura del pipeline verde o del log de deployment |

#### Criterios de aceptación
- Cada criterio debe ser verificable visualmente por alguien sin conocimientos técnicos.
- Usar lenguaje: *"Al abrir X, se muestra Y"* / *"El reporte de Z no contiene duplicados"* / *"El usuario puede hacer X sin errores"*.

---

### Paso 4 — Output final

Entregar dos cosas:

1. **Descripción Jira formateada** — Lista para copiar directamente al ticket de Jira. Usar Markdown estándar de Jira (Jira soporta `*negrita*`, `_italica_`, listas con `*` y `#`). Adaptar si el proyecto usa formato wiki de Jira o Atlassian Document Format (ADF).

2. **Lista de imágenes pendientes** — Tabla con cada imagen/diagrama sugerido, quién lo tiene que proveer, y formato recomendado.

**Captura automática (MCP Playwright disponible):** si la evidencia tiene una URL accesible (dashboard, reporte web, app desplegada), tomar la captura directamente con `mcp__playwright__browser_take_screenshot` en vez de pedirla al responsable del ticket — marcar "Quién provee: Claude (Playwright MCP)" en la tabla. Si no hay URL (output de terminal, captura de IDE, diagrama conceptual), sigue siendo manual — "Quién provee: Responsable del ticket".

Ejemplo de lista de imágenes pendientes:
```
| # | Descripción | Quién provee | Formato |
|---|---|---|---|
| 1 | Captura del reporte con datos duplicados (estado anterior) | Responsable del ticket | PNG o GIF |
| 2 | Captura del reporte corregido (estado actual) | Responsable del ticket | PNG |
| 3 | Gráfica de barras: registros antes (1,840) vs después (920) | Claude genera sugerencia / Responsable confirma | PNG o tabla |
```

---

### Paso 5 — Auto-posting del comentario a Jira

Si `ticket_key` está presente:

1. Llamar `mcp__jira__jira_add_comment` con el markdown generado en el Paso 4:

```
mcp__jira__jira_add_comment(
  issue_key = <ticket_key>,
  body      = <markdown del Paso 4>
)
```

2. Capturar la URL del comentario creado y reportarla al usuario.
3. En el contexto de `unified-docs-pipeline`, el `comment_url` se incluye en la tabla de step-status como artefacto del Step 3.

Si `ticket_key` NO está presente:
- Omitir este paso por completo.
- Entregar el markdown del Paso 4 para que el usuario lo copie manualmente.
- Incluir el mensaje: _"Para auto-postear, proveer `ticket_key` al invocar el skill."_

---

### Paso 5b — Mirror a Obsidian (opcional pero recomendado)

Si el usuario confirma guardar el ticket en el vault:

1. Completar el template `BOVEDA MCP CLAUDE-OBSIDIAN/900_TEMPLATES/JIRA-Ticket-Evidencia.md` con los valores reales.
2. Guardar en `BOVEDA MCP CLAUDE-OBSIDIAN/50-Projects/<proyecto>/Tickets/<TICKET-ID>.md`.
3. Llamar `mem_save` con type `pattern` y title `"Ticket Jira formateado: <TICKET-ID>"`.

---

## Anti-patterns (nunca hacer)

- No incluir nombres de funciones, variables, clases o paths en las secciones visibles al no-técnico.
- No generar un ticket si no hay evidencia real — marcar `[pendiente]` y pedir el dato.
- No escribir criterios de aceptación que solo un desarrollador puede verificar (ej: "el unit test pasa").
- No omitir las sugerencias de imagen aunque el usuario no las haya pedido explícitamente.
- No generar métricas ficticias para completar la tabla.
- No agregar secciones o párrafos que no aporten información nueva al lector (gate Ponytail, Regla 6).
