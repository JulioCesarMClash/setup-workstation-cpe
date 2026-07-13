---
name: llm-wiki
description: "Ingest external content (PDF, URL, transcript, markdown) into the Obsidian vault as typed, frontmatter-tagged notes. Trigger: /ingest"
version: "1.0"
license: MIT
metadata:
  author: juliomartinez
  install_path: ~/.skills/llm-wiki/SKILL.md
  ingest_script: ~/Developer/llm-wiki/ingest.py
---

## Trigger

`/ingest <source> [--type pdf|url|transcript|md] [--tags t1,t2] [--inbox]`

## Purpose

Converts a file path, URL, or Drop-Here inbox into a clean Obsidian note
under `10-Fuentes/llm-wiki/<type>/<slug>.md`. Each note includes:
- YAML frontmatter: title, source, type, ingested_at, tags
- Extracted body content
- `## Connections` section (top-3 keyword-overlap wikilinks)

After each successful ingest, the script emits an ENGRAM_NOTIFY JSON block
to stdout. Parse it and call `mem_save` with the payload to register the
ingestion in Engram under project `juliomartinez`.

## Execution

```bash
python3 ~/Developer/llm-wiki/ingest.py <source> [--type TYPE] [--tags TAGS] [--inbox]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<source>` | File path or HTTP/HTTPS URL to ingest |
| `--type` | Override auto-detected type: pdf, url, transcript, md |
| `--tags` | Comma-separated tags added to frontmatter |
| `--inbox` | Scan `70-Inbox/Drop-Here/` and batch-process all supported files |

## ENGRAM_NOTIFY Contract

After a successful ingest the script prints to stdout:

```
===ENGRAM_NOTIFY_BEGIN===
{"title": "...", "type": "...", "source": "...", "vault_path": "...", "tags": [...], "connections": [...], "status": "ok"}
===ENGRAM_NOTIFY_END===
```

When you see this block, call:

```
mem_save(
  title: payload["title"],
  type: "discovery",
  project: "juliomartinez",
  content: "Ingested <type> from <source> → vault: <vault_path>"
)
```

## Vault Path Resolution

The script resolves the vault root via `CLAUDE_VAULT_PATH` env var.
Fallback: `~/Developer/BOVEDA MCP CLAUDE-OBSIDIAN`.

## Examples

```bash
# Ingest a PDF
/ingest /path/to/paper.pdf --tags research,ml

# Ingest a URL
/ingest https://example.com/article --tags reading

# Ingest Drop-Here inbox batch
/ingest --inbox
```
