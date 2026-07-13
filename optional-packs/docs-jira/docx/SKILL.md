---
name: docx
description: >
  Produce Word (.docx) document deliverables: headings, styled paragraphs,
  tables, and basic lists for reports aimed at non-technical stakeholders.
  Use when a stakeholder asks for "a Word doc", "documento", "informe en
  Word", or when prose/report content needs Word format rather than PDF or
  Confluence. Complements `exec-pdf-doc` (PDF) and `confluence-doc`
  (Confluence).
license: MIT
metadata:
  tier: MEDIUM
---

# docx

## Library

`python-docx`. No alternatives.

## Recipe — title → headings → paragraphs → table → save

```python
from docx import Document

doc = Document()
doc.add_heading('Executive Report: Project X', 0)   # Title
doc.add_heading('Analysis Overview', level=1)        # Section
doc.add_paragraph('This document details the latest quality metrics...')
# ... add table here (see helper below) ...
doc.save('report_v1.docx')
```

## Heading hierarchy and style

Match `exec-pdf-doc`'s look so deliverables read as one family:

- **Level 0** — main title (centered, bold)
- **Level 1** — primary sections (bold, larger)
- **Level 2** — sub-sections (bold)
- **Level 3** — detail blocks (italic/bold)

Use the built-in `Normal` / `Heading X` styles — no external `.dotx` template files, keeps compatibility across Word versions.

## Table-from-data helper

```python
def add_data_table(doc, data: list[dict]):
    if not data:
        return
    headers = list(data[0].keys())
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header.replace('_', ' ').title()
    for item in data:
        row_cells = table.add_row().cells
        for i, value in enumerate(item.values()):
            row_cells[i].text = str(value)
```

## Output placement

Save outside any git repo, naming pattern `[PROJECT]_[DELIVERABLE]_[YYYYMMDD].docx` — same policy as `xlsx` and `exec-pdf-doc`.

## Scope boundary

This skill only creates documents. No format conversion (docx → pdf, etc.) — that's `sdd-markitdown`'s job.

## Out of scope

Templates/themes beyond the single default style set, track-changes/comments/mail-merge, embedded charts or an image pipeline (plain tables and text only), any docx-to-other-format conversion.
