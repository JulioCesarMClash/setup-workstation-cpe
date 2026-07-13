---
name: tdd-triple-helice
description: >
  Mandates TDD (tests written and confirmed RED before any implementation)
  combined with the Triple Hélice delegation flow (Gemma4 plans, Qwen writes
  tests-then-code, Claude applies and verifies RED→GREEN). Global — applies
  to any non-trivial development task (new logic, complex refactor, DB
  design, abstract bug fixing) in any project under ~/Developer, not just
  the current one. Use automatically before writing implementation code for
  such tasks; also trigger on "TDD", "triple hélice", "gentle ai workflow".
license: MIT
---

# TDD + Triple Hélice (global)

## Skills requeridos (orchestrator debe inyectar vía skill-resolver)
- `ollama-task-router` — clasificación de tier antes de ejecutar

Canonical source — keep in sync if either changes:
- `/Users/juliomartinez/Developer/AI-OS/Claude-Global/workflows/triple-helice.md`
- Obsidian mirror: `000_SISTEMA_OPERATIVO/031_Reglas_Co_Presidencia_IA.md`

## Activation

Applies to ANY project under `~/Developer`, not just the one currently open.
Skip only for the exceptions listed below.

## Critical pattern — TDD is non-negotiable

Tests are written and confirmed **RED** before a single line of
implementation exists. Never write the implementation first and backfill
tests. Never edit a test just to make it pass.

## The flow

1. **Tier first** — cargar `ollama-task-router` (inyectado vía skill-resolver o `<available_skills>` self-check) y clasificar el tier antes de hacer nada.
2. **Plan (Gemma4)** — local model designs the logic, validations, and exact
   DQS rules:
   ```bash
   ~/local-router reason "Actúa como Arquitecto de Software. Diseña la lógica conceptual, validaciones, consultas óptimas y grain exacto para: [prompt/bug]" --agent claude
   ```
3. **Tests, then code (Qwen)** — strictly in this order:
   ```bash
   # 3a. Tests ONLY — must cover the 5 DQS obligations, no implementation
   ~/local-router code "Actúa como Senior Developer. Escribe SOLO la suite pytest (sin implementación) que cubra las 5 obligaciones DQS, basándote exclusivamente en este plano: [output paso 2]" --agent claude

   # 3b. Minimal implementation to pass those tests, without touching them
   ~/local-router code "Actúa como Senior Developer. Escribe la implementación mínima en Python/SQL, estricta y tipada, que haga pasar esta suite pytest sin modificarla: [tests del paso 3a]" --agent claude
   ```
4. **Apply and verify (Claude)**:
   - Apply the tests from 3a with File I/O. Run `pytest` — must be **RED**
     (fails for missing implementation, not syntax/import errors).
   - Apply the implementation from 3b.
   - Run `pytest` again — must be **GREEN** (0 failures). If still red, the
     plan or implementation has a real bug — never modify the test to force
     a pass.
   - Only then hand the task back to the user.

## DQS 5 obligations the tests must cover

Exact cardinality per grain · dimensional reconciliation (sum of segments ==
total) · real edge cases (empty/null/zero) · destructive idempotency (run
twice, no duplicates/orphans) · zero orphan rows after replace/upsert. Full
detail: `domains/data-quality.md` in the same AI-OS tree.

## Gentle-AI execution order

For substantial tasks, in this order:

1. Recover context/memory if the task references prior work.
2. Classify the tier (cargar `ollama-task-router` vía skill-resolver o `<available_skills>` self-check).
3. Decide direct execution vs formal SDD.
4. Load only the specific skills actually needed.
5. Keep changes reversible when touching global/shared config.

## Exceptions — skip this skill entirely

- Git control (commits, branches, status, log)
- Reading existing notes/files (Obsidian, repo)
- Running an existing pytest suite (no new code)
- Mechanical tasks with no analytical reasoning (renames, formatting, config)
