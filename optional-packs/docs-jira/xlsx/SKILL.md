---
name: xlsx
description: >
  Produce real Excel (.xlsx) deliverables for non-technical stakeholders:
  multiple sheets, header formatting, column widths, number/date formats, and
  simple formulas. Use when turning query results or CSV exports (e.g. from
  `Daily task/exports_csv/`) into a polished workbook, when a stakeholder asks
  for "an Excel", "spreadsheet", "reporte en Excel", or when CSV output needs
  formatting a non-technical reader expects.
license: MIT
metadata:
  tier: MID-HIGH
---

# xlsx

## Library

`openpyxl`. No alternatives — don't shop around.

## Minimal recipe — CSV to formatted sheet

```python
import csv
from openpyxl import Workbook
from openpyxl.styles import Font

wb = Workbook()
ws = wb.active

with open('input.csv', 'r') as f:
    for row in csv.reader(f):
        ws.append(row)

for cell in ws[1]:
    cell.font = Font(bold=True)
ws.freeze_panes = "A2"

for col in ws.columns:
    max_length = max(len(str(cell.value or "")) for cell in col)
    ws.column_dimensions[col[0].column_letter].width = max_length + 2

wb.save('output.xlsx')
```

## Multi-sheet pattern

```python
data_payload = {
    "Registered": registered_rows,
    "Certified": certified_rows,
    "Beneficiaries": ben_rows,
}

wb = Workbook()
wb.remove(wb.active)
for sheet_name, rows in data_payload.items():
    ws = wb.create_sheet(title=sheet_name)
    for row in rows:
        ws.append(row)
```

## Format codes stakeholders expect

Apply via `cell.number_format = 'CODE'`.

| Data type | Code | Example |
|---|---|---|
| Currency | `"$#,##0.00"` | $1,250.50 |
| Date | `"yyyy-mm-dd"` | 2026-05-20 |
| Percentage | `"0.00%"` | 85.25% |
| Big integer | `"#,##0"` | 1,000,000 |

## Totals row via formula injection

```python
row_idx = ws.max_row + 1
ws.cell(row=row_idx, column=1).value = f"=SUM(A2:A{ws.max_row})"
ws.cell(row=row_idx, column=1).font = Font(bold=True)
ws.cell(row=row_idx, column=2).value = f"=AVERAGE(B2:B{ws.max_row})"
```

## Output placement

Save in `~/Developer/Daily task/exports_csv/` or a sibling ad-hoc folder. **Never inside a git repo** — per the project's ad-hoc-script policy.

## Out of scope

Pivot tables, charts, macros/VBA, live DB connections (consumes CSV or in-memory data only — pairs with existing export scripts), cross-workbook linking, a configurable styling framework beyond the helpers above.
