---
name: unified-docs-pipeline
description: >
  Thin orchestrator skill that sequences exec-pdf-doc → confluence-doc →
  jira-evidence-formatter → jira_update_issue from a single invocation,
  delivering documentation to PDF, Confluence, and Jira without manual steps
  between them.
  Trigger: "documentar este cambio", "generar docs para AUD-N", "pipeline documentación",
  "documentar cambio end-to-end", "docs unificados", "pdf confluence jira".
license: Apache-2.0
metadata:
  author: julio-martinez
  version: "2.0"
  tier: MID-HIGH
  model: claude-sonnet-4-6
  related_skills:
    - exec-pdf-doc
    - confluence-doc
    - jira-evidence-formatter
---

## Required Inputs

| Parameter | Default | Required | Description |
|---|---|---|---|
| `change_name` | — | YES | Name of the change/feature being documented (e.g. `add-unified-docs-pipeline`) |
| `docs_dir` | `docs/` | YES | Directory where documentation files live |
| `confluence_space` | — | YES | Confluence space key (e.g. `DataAnalys`) |
| `confluence_root_page_id` | — | YES | Parent page ID under which the Confluence page is created |
| `jira_ticket_key` | — | YES | Jira ticket key (e.g. `DAT-42`) |

### Missing-Parameter Guard

Before executing Step 1, verify all five parameters are present. If any is missing:

1. STOP immediately — do not attempt any step.
2. List each missing parameter by name.
3. Exit with a clear error message.

Example:
```
ERROR: Missing required parameters:
  - confluence_root_page_id
  - jira_ticket_key
Provide all five parameters and invoke again.
```

---

## Execution — 4-Step Fail-Fast Sequence

Steps run in strict order. On any failure, STOP and emit the step-status table (see Output section).

### Step 1 — Generate Executive PDF

Load skill `exec-pdf-doc`.

- Input: `change_name`, `docs_dir`
- Expected artifact: `docs/{change_name}_EXECUTIVE.pdf`
- On failure: STOP. Report step=exec-pdf-doc, status=FAILED.

### Step 2 — Publish to Confluence

Load skill `confluence-doc` with explicit parameters:

```
confluence-doc(
  space_key          = confluence_space,
  root_page_id       = confluence_root_page_id,
  source_dir         = docs_dir,
  page_title         = "YYYY-MM-DD — {change_name}"
)
```

- Expected artifact: Confluence page URL (capture for Step 4).
- On failure (including duplicate title conflict): STOP. Report step=confluence-doc, status=FAILED.
- Capture: `confluence_page_url` — required for Step 4.

### Step 3 — Post Evidence to Jira

Load skill `jira-evidence-formatter` with `ticket_key=jira_ticket_key`.

This triggers the Pipeline mode of `jira-evidence-formatter` (Steps 1–5), which:
1. Generates formatted markdown evidence.
2. Calls `mcp__jira__jira_add_comment(issue_key=jira_ticket_key, body=<markdown>)`.
3. Returns `comment_url`.

- Expected artifact: Jira comment URL.
- On failure: STOP. Report step=jira-evidence-formatter, status=FAILED.

### Step 4 — Update Jira Description with Docs Link

Call `mcp__jira__jira_update_issue` to append or replace the `## Docs` section in the ticket description:

```
mcp__jira__jira_update_issue(
  issue_key = jira_ticket_key,
  fields    = {
    description: <existing_description with ## Docs section appended or replaced>
  }
)
```

Logic:
- If the ticket description already contains a `## Docs` section: replace it.
- If not: append it at the end.

Content to insert/replace:
```markdown
## Docs

- [View documentation on Confluence](<confluence_page_url>)
- PDF: `docs/{change_name}_EXECUTIVE.pdf`
```

- Expected artifact: Updated Jira ticket URL.
- On failure: STOP. Report step=jira_update_issue, status=FAILED.

---

## Output — Step-Status Table

Always return a step-status table after every run, whether successful or partial:

```markdown
| Step | Status | Artifact |
|---|---|---|
| exec-pdf-doc | ✅ SUCCESS | docs/{change_name}_EXECUTIVE.pdf |
| confluence-doc | ✅ SUCCESS | https://...atlassian.net/wiki/... |
| jira-evidence-formatter | ✅ SUCCESS | https://...atlassian.net/browse/DAT-42?focusedCommentId=... |
| jira_update_issue | ✅ SUCCESS | https://...atlassian.net/browse/DAT-42 |
```

Status values:
- `✅ SUCCESS` — step completed, artifact produced.
- `❌ FAILED` — step failed; include reason in the Artifact column.
- `⏭ SKIPPED` — step not reached due to prior failure.

Example of partial failure (Step 2 fails):

```markdown
| Step | Status | Artifact |
|---|---|---|
| exec-pdf-doc | ✅ SUCCESS | docs/my-change_EXECUTIVE.pdf |
| confluence-doc | ❌ FAILED | Page already exists: "2026-07-13 — my-change" under root_page_id 4554920 |
| jira-evidence-formatter | ⏭ SKIPPED | — |
| jira_update_issue | ⏭ SKIPPED | — |
```

---

## Optional — P02 Project Logging

If running in the P02 project context (`/Users/juliomartinez/Developer/P02 - apn-pti26-audit-memory`), append the pipeline run result to `bunker_devops.log`:

```
[YYYY-MM-DD HH:MM] unified-docs-pipeline | change={change_name} | ticket={jira_ticket_key} | status={overall}
```

This is optional — if `bunker_devops.log` does not exist or is outside the project, skip silently.

---

## Rules

- This skill is an ORCHESTRATOR — it calls other skills by name, never inlines their logic.
- All five required inputs must be present before Step 1 executes.
- Fail-fast is mandatory — do NOT continue after a step failure.
- The step-status table is the OUTPUT CONTRACT — always produce it, even on failure.
- `confluence_page_url` from Step 2 MUST be forwarded to Step 4.
- `jira_ticket_key` MUST be forwarded to both Step 3 and Step 4.
- Do not call `publish_to_confluence.py` — use MCP tools only.

---

## Anti-patterns

- Do not skip the missing-param guard and assume defaults for required fields.
- Do not continue to Step 3 if Step 2 failed (fail-fast).
- Do not inline the logic of `exec-pdf-doc`, `confluence-doc`, or `jira-evidence-formatter`.
- Do not use `confluence_space` ETL defaults (DataAnalys/4554920) if explicit values were supplied.
