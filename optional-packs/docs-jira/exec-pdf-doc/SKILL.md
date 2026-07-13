---
name: exec-pdf-doc
description: >
  Genera documentación técnica en formato ejecutivo PDF — formal, con portada,
  índice automático, redacción humana accesible y estilo visual profesional.
  Convierte markdown técnico en un documento presentable para audiencias mixtas
  (negocio + técnico). Usa pandoc + Chrome headless para el render final.
  Trigger: Cuando el usuario pide generar o mejorar un PDF de documentación,
  "generar PDF ejecutivo", "doc formal", "documentación presentable", "formato ejecutivo".
license: Apache-2.0
metadata:
  author: julio-martinez
  version: "1.0"
allowed-tools: Read, Edit, Write, Bash, mcp__plugin_engram_engram__mem_save
---

## When to Use

- Usuario pide un PDF de documentación de API, arquitectura, ETL, release notes
- El markdown existente es correcto técnicamente pero necesita formato ejecutivo
- El documento irá a stakeholders de negocio, directivos o clientes externos
- Se requiere portada, índice y estilo visual consistente con la marca

---

## Mandatory Document Sections (ALL required)

| # | Sección | Contenido |
|---|---------|-----------|
| 0 | **Portada** | Título, subtítulo, versión, fecha, proyecto/equipo |
| 1 | **Índice** | Generado automáticamente con anclas a cada sección |
| 2 | **Resumen Ejecutivo** | 1-2 párrafos en lenguaje de negocio — qué hace, para qué sirve, quién lo usa |
| 3 | **Cuerpo técnico** | Secciones numeradas del contenido original, reescritas en lenguaje accesible |
| 4 | **Glosario** | Términos técnicos explicados en una línea para no-técnicos |
| 5 | **Información de contacto / soporte** | Dónde ir si algo falla o hay dudas |

---

## Redacción — Reglas de estilo

### Lenguaje
- **No**: "El endpoint retorna un array de objetos JSON serializados con los campos..."
- **Sí**: "La consulta devuelve una lista de registros con la información de cada corrida."
- Evitar siglas sin definir en primera mención: `API (Interfaz de Programación de Aplicaciones)`
- Preferir voz activa: "La API devuelve" en vez de "Los datos son devueltos por la API"
- Oraciones cortas. Sin jerga innecesaria. Sin abreviaciones técnicas sin contexto.

### Estructura visual
- Párrafos cortos (3-4 líneas máximo)
- Bullets para listas de más de 2 ítems
- Tablas para comparaciones y parámetros
- Bloques de código solo cuando el lector necesita copiar-pegar

---

## Execution Flow — Triple Hélice

### Step 1 — Scan (Claude tools)
1. Leer el markdown fuente (repo o Obsidian)
2. Identificar secciones técnicas que requieren reescritura para audiencia mixta
3. Extraer: título, versión, fecha, proyecto, autor, URL base

### Step 2 — Reason (Ollama / gemma4:31b)
```bash
~/local-router reason "Actúa como redactor técnico senior. Tengo este documento de API/arquitectura en markdown técnico. Reescribe el Resumen Ejecutivo y la introducción de cada sección en lenguaje accesible para una audiencia mixta (negocio + técnico). Mantén la precisión técnica pero elimina jerga. Devuelve solo el texto reescrito, sin el resto del documento.
Documento: [contenido markdown]" --agent claude
```

### Step 3 — Write (Claude tools)
1. Combinar contenido original + texto reescrito
2. Aplicar template HTML ejecutivo (`assets/executive-template.html`)
3. Generar PDF con Chrome headless
4. Guardar en `docs/<NOMBRE>_EXECUTIVE.pdf`
5. Llamar `mem_save` con ruta y fecha

---

## Commands

```bash
# Generar PDF ejecutivo desde markdown
# Step 1: Pandoc markdown → HTML con template ejecutivo
pandoc <input.md> \
  --from markdown \
  --to html5 \
  --standalone \
  --template ~/.skills/exec-pdf-doc/assets/executive-template.html \
  --metadata title="<Título>" \
  --metadata subtitle="<Subtítulo>" \
  --metadata version="<v1.x.x>" \
  --metadata date="$(date '+%d de %B de %Y')" \
  --metadata project="<Proyecto>" \
  --toc \
  --toc-depth=3 \
  -o docs/<output>.html

# Step 2: HTML → PDF con Chrome headless
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new \
  --no-sandbox \
  --print-to-pdf="docs/<output>.pdf" \
  --print-to-pdf-no-header \
  --no-pdf-header-footer \
  "file://<ruta-absoluta>/docs/<output>.html"
```

---

## CSS / Visual Style Rules

Ver template completo en `assets/executive-template.html`.

| Elemento | Estilo |
|----------|--------|
| Fuente principal | Inter, system-ui, sans-serif |
| Fuente código | JetBrains Mono, monospace |
| Color primario | `#003366` (navy) |
| Color acento | `#1d6fa4` (azul medio) |
| Fondo tabla header | `#003366` |
| Portada | Fondo navy, texto blanco, logo/proyecto centrado |
| Saltos de página | Antes de cada `<h1>` (nueva sección) |
| Índice | Generado por pandoc `--toc`, estilizado con puntos guía |

---

## Obsidian Rule

Después de generar el PDF, guardar una nota en:
`50-Projects/<project>/Docs/<NOMBRE>_EXECUTIVE_PDF.md`

Con este frontmatter:
```yaml
---
type: doc-artifact
project: <project>
format: pdf-executive
generated: YYYY-MM-DD
path: docs/<output>.pdf
pages: <N>
---
```

---

## Resources

- **Template HTML**: `assets/executive-template.html`
- **Ejemplo de uso**: API Reference de apn-pti26-data-core (2026-06-04)
