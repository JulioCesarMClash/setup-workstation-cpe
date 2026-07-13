---
name: confluence-doc
description: >
  Formats and structures documentation for Confluence (DataAnalyst space).
  Converts markdown content (RELEASE_NOTES.md, ARCHITECTURE.md, ADRs) into
  Confluence storage format with proper macros, panels, and layout.
  Trigger: When editing or preparing documentation destined for Confluence,
  when updating RELEASE_NOTES.md or ARCHITECTURE.md, or when publishing
  to the DataAnalyst Confluence space. Now accepts explicit space/page/source
  parameters for use from unified-docs-pipeline.
license: Apache-2.0
metadata:
  author: julio-martinez
  version: "2.0"
---

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `space_key` | `DataAnalys` | Confluence space key |
| `root_page_id` | `4554920` | Parent page ID under which the new page is created |
| `source_dir` | `~/Documents/ELT_analisis_Script/` | Directory containing markdown source files |
| `page_title` | `YYYY-MM-DD — {change_name}` | Title of the created page (auto-generated when not supplied) |

When called without any of these parameters, the ETL defaults above apply so the existing ETL Confluence publish flow continues unchanged.

## Page Creation — MCP

Use `mcp__jira__confluence_create_page` to create pages. Do NOT invoke `publish_to_confluence.py`.

```
mcp__jira__confluence_create_page(
  space_key  = <space_key>,
  parent_id  = <root_page_id>,
  title      = <page_title>,
  body       = <markdown content from source_dir>
)
```

Page title pattern when not explicitly supplied: `YYYY-MM-DD — {change_name}` (today's date + change name, direct child of root_page_id).

**Conflict rule:** If a page with the same title already exists under root_page_id, STOP and report a conflict error. Do NOT silently overwrite.

## When to Use

- Editing `RELEASE_NOTES.md` or `ARCHITECTURE.md` in the ETL project
- Writing a new ADR that will be published to Confluence
- Reviewing documentation before a release
- Called by `unified-docs-pipeline` with explicit `space_key`, `root_page_id`, `source_dir` parameters

---

## Confluence Space (ETL defaults)

- **Space:** DataAnalyst (`DataAnalys`)
- **URL:** `https://capacitateparaelempleo.atlassian.net/wiki/spaces/DataAnalys`
- **Root page ID:** `4554920`
- **Source dir (ETL):** `~/Documents/ELT_analisis_Script/`

---

## Page Structure

```
DataAnalyst (root)
├── Versiones                        ← parent, one sub-page per release
│   ├── v1.6.0 (unreleased)
│   ├── v1.5.1
│   └── v1.x.x ...
└── Arquitectura ETL                 ← full ARCHITECTURE.md content
```

---

## Critical Formatting Rules

### Release Notes pages

Each version page must follow this structure in markdown:

```markdown
## [vX.Y.Z] - YYYY-MM-DD

### Executive Summary
One paragraph. Plain prose, no lists.

### Added
- Item with file path or module name

### Changed
- Item describing what changed and why

### Removed
- Item describing what was removed and where it moved

### Operational Notes
- Breaking changes, import path changes, env var changes
```

**Rules:**
- Executive Summary must be a paragraph — never a list
- File paths in backticks: `etl/infrastructure/database.py`
- Module renames use `→` arrow: `etl.config.database` → `etl.infrastructure.database`
- No emojis in release notes
- Dates in ISO format: `YYYY-MM-DD`

---

### Architecture pages (ARCHITECTURE.md)

- ADRs use the format: `### ADR-XX — Title`
- Each ADR has exactly three fields: **Decisión**, **Motivo**, **Consecuencia**
- Directory trees go in fenced `text` blocks, not `bash`
- Data flow steps are numbered lists, not bullets
- Operational snapshots use tables for env vars and config values

---

### Confluence macro hints (for the publisher script)

The publisher converts these markdown patterns to Confluence macros automatically:

| Markdown | Confluence result |
|---|---|
| ` ```python ` | Code macro with Python highlighting |
| ` ```sql ` | Code macro with SQL highlighting |
| ` ```text ` | Code macro with no highlighting |
| `> text` | Info panel macro |
| Standard table | HTML table |

For admonitions (warnings, notes) that are NOT standard markdown blockquotes,
add a comment in the markdown so the publisher can detect them:

```markdown
<!-- confluence:warning -->
> This is a warning panel in Confluence.
```

---

---

## Checklist before publishing

- [ ] New version section follows the four-section structure (Added / Changed / Removed / Operational Notes)
- [ ] Executive Summary is a paragraph, not a list
- [ ] File paths use backticks
- [ ] Import path changes use the `antes → después` table format
- [ ] ADRs have the three mandatory fields (Decisión, Motivo, Consecuencia)
- [ ] ARCHITECTURE.md directory tree reflects current folder structure
- [ ] `ARCHITECTURE.md` "Estado documentado" date is updated

---

## Resources

- **Legacy fallback script (do NOT invoke from skill):** `~/Documents/data-team-tools/confluence/publish_to_confluence.py`
  - This script is left intact for manual/CLI use outside the skill. The skill uses MCP instead.
- **README:** `~/Documents/data-team-tools/confluence/README.md`
- **Release notes:** `~/Documents/ELT_analisis_Script/RELEASE_NOTES.md`
- **Architecture:** `~/Documents/ELT_analisis_Script/ARCHITECTURE.md`
