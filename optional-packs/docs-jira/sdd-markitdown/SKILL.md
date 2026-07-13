---
name: sdd-markitdown
description: >
  Wrapper local para Microsoft MarkItDown. Convierte documentos pesados
  (PDF, docx, xlsx, pptx, html, imágenes) a Markdown de forma local,
  los persiste en Obsidian bajo 10-Fuentes/Ingesta-MarkItDown/ y emite
  un bloque de notificación para que Engram los indexe.
  Costo de conversión: $0 — procesamiento 100% local.
  Trigger: Cuando el usuario pide revisar, resumir o analizar un documento
  pesado y quiere que quede disponible para consultas posteriores sin
  consumir tokens cloud.
license: MIT
metadata:
  author: gentleman-programming
  version: "1.0"
  tier: MID-HIGH
  recommended_model: gemma4:31b
  executable: ~/.skills/sdd-markitdown/main.py
  depends_on: markitdown>=0.1.0
---

# sdd-markitdown

## Purpose

Convierte documentos a Markdown localmente usando `markitdown` de Microsoft,
los almacena en el vault de Obsidian y notifica a Engram para indexación.

**Flujo:**
```
Archivo origen → MarkItDown (local, $0) → .md
                                        → 10-Fuentes/Ingesta-MarkItDown/<stem>.md
                                        → Bloque ENGRAM_NOTIFY para indexación
```

Una vez ingestado, cualquier consulta posterior sobre ese documento
se procesa con Qwen/Gemma a costo $0 — no vuelve a consumir tokens cloud.

## Inputs

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `file` | path | ✅ | Ruta al archivo a convertir (PDF, docx, xlsx, pptx, html, img) |
| `--output` / `-o` | path | ❌ | Override de ruta de salida (default: vault Obsidian) |
| `--title` | string | ❌ | Título para Engram (default: nombre del archivo) |
| `--project` | string | ❌ | Proyecto Engram para indexar (default: juliomartinez) |
| `--dry-run` | flag | ❌ | Muestra el markdown convertido sin guardar |

## Outputs

- **Archivo:** `~/Documents/BOVEDA MCP CLAUDE-OBSIDIAN/10-Fuentes/Ingesta-MarkItDown/<stem>.md`
- **stdout:** Ruta del archivo guardado + bloque `ENGRAM_NOTIFY` para que Claude ejecute `mem_save`
- **exit 0:** Conversión y guardado exitosos
- **exit 1:** Error (archivo no encontrado, formato no soportado, markitdown no instalado)

## Formatos soportados

PDF, docx, xlsx, pptx, html, htm, csv, json, xml, zip, imágenes (jpg, png, gif, webp)

## Auto-instalación

Si `markitdown` no está instalado, el script lo instala automáticamente via pip
e informa al usuario antes de continuar.

## Usage

```bash
# PDF
python3 ~/.skills/sdd-markitdown/main.py ~/Documents/informe.pdf

# Con proyecto explícito
python3 ~/.skills/sdd-markitdown/main.py ~/Downloads/datos.xlsx --project Sandbox-ETL

# Dry-run (preview sin guardar)
python3 ~/.skills/sdd-markitdown/main.py ~/Documents/deck.pptx --dry-run
```

## Rules

- SIEMPRE guardar en `10-Fuentes/Ingesta-MarkItDown/` — nunca en otro directorio del vault.
- Después de guardar, Claude DEBE ejecutar `mem_save` con el bloque `ENGRAM_NOTIFY` impreso.
- No re-convertir si ya existe el `.md` en Obsidian — verificar primero.
- La conversión es local: nunca enviar el contenido del documento a la API cloud.
- Archivos > 50 MB: advertir al usuario y proceder solo con confirmación explícita.
