---
name: systematic-debugging
description: >
  Step-by-step debugging protocol for non-obvious bugs. Delegates root-cause
  analysis to gemma4:31b, then applies structured verification. Final step
  requires passing DQS 5 obligations before marking the bug resolved.
  Use when a bug is not immediately obvious from reading the code.
---

Route root-cause analysis to local_router, then apply structured fix.
Do not guess the cause — isolate first, then reason.

## Steps

1. **Reproduce** — confirm the bug is deterministic. Get the exact input
   that triggers it.

2. **Isolate** — narrow to the smallest failing unit:
   ```bash
   ~/local-router reason "<symptom + relevant code + stack trace>" --agent senior-reviewer
   ```

3. **Hypothesize** — from agent output, form one hypothesis. State it
   explicitly before touching code.

4. **Fix minimally** — Ponytail `full`: change only what breaks. No
   opportunistic cleanup.

5. **DQS gate (mandatory before closing)** — verify all 5 obligations:
   - [ ] Exact cardinality — row counts match expected
   - [ ] Reconciliation — totals tie between source and target
   - [ ] Edge cases — NULL, zero, empty set, boundary values tested
   - [ ] Idempotency — running twice produces same result
   - [ ] Orphan-row check — no dangling FK references introduced

   If ANY obligation fails → bug is NOT resolved. Re-enter at step 2.

6. **Document** — if the root cause was non-obvious, call `mem_save` with
   type=decision, include what failed and why.

## Triggers

- "no sé qué falla", "bug extraño", "por qué falla esto"
- "debug", "rastrear el error", "investigate"
- Any bug that survives a first read of the code
