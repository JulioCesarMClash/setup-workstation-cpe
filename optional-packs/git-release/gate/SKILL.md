---
name: gate
description: >
  Pre-push validation gate. Runs diff analysis, lint, tests, and AI review
  before pushing. Creates PR automatically on pass.
  Trigger: /gate, "run gate", "validate before push", "gate this branch"
metadata:
  version: "1.0"
  global: true
  script: ~/Developer/AI-OS/gate/gate.sh
---

## When to Use

- Before pushing a branch
- When asked to validate changes before PR
- When `/gate` is invoked

## Execution

Run the gate script directly:

```bash
~/Developer/AI-OS/gate/gate.sh
```

Do NOT summarize what the gate does before running it. Execute immediately.

## Flags

- `--no-pr` — validate only, skip PR creation
- `--tier=trivial|standard|complex` — force tier
- `--pre-push` — hook mode (validate only, no push)

## After Gate Passes

Report: tier, lines changed, AI findings summary, PR URL if created.

## After Gate Blocks

Show the CRITICAL findings from the AI review. Ask the user if they want to:
1. Fix the findings (continue working)
2. Force push anyway with `--no-gate` (not recommended)
3. Override a specific finding
