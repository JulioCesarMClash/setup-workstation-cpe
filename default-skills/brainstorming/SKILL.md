---
name: brainstorming
description: >
  Structured pre-SDD ideation and tier classification. Use before committing
  to an SDD change or a lighter flow on any non-trivial dev task: explore
  options, surface tradeoffs, and classify the task tier (trivial /
  non-trivial / complex) so the right delivery path is chosen. This is the
  formal "Triple Hélice" step. Trigger on "brainstorm", "let's think
  through", "ideate", "tier this", "qué enfoque", before large refactors or
  new features.
license: MIT
metadata:
  tier: MEDIUM
---

# brainstorming (Triple Hélice)

## 0. Ponytail gate — ask this first

Does this task need to exist at all? Can it be skipped, deleted, or radically simplified before any tier classification happens? If yes, stop here, document the simplification, don't proceed to classification.

## 1. Tier classification

| Tier | Delivery path | Criteria / example |
|---|---|---|
| Trivial | Direct action | Single-file change, no side effects. E.g. fixing a typo in a log message. |
| Non-trivial | Light flow or SDD | Touches 2+ files, or modifies a shared internal API. Light flow if the how is clear but tedious; SDD if it needs architectural alignment. E.g. adding a field to a DTO and updating its mapping. |
| Complex | Full SDD pipeline | Crosses domain boundaries, needs a new pattern or dependency. E.g. a new distributed-locking mechanism for the ETL. |

## 2. Option-generation rule

For non-trivial and complex tasks, produce at least 2 genuinely distinct approaches before recommending one:

- **Approach A** — [description] → tradeoff: [one line]
- **Approach B** — [description] → tradeoff: [one line]

## 3. Delegation hook

- Trivial: reason directly, no delegation.
- Non-trivial / complex: route the actual deliberation through the local routing workflow if available. Consolidate the router's output, do not re-derive the reasoning from scratch.

## 4. Handoff

End with an explicit statement:

1. **Chosen tier**: trivial / non-trivial / complex
2. **Next skill**:
   - Trivial → proceed directly
   - Non-trivial, research-heavy → `sdd-explore`
   - Non-trivial, implementation-ready → light flow
   - Complex → `sdd-propose`

## Out of scope

Writing specs or proposals (that's `sdd-explore`/`sdd-propose`'s job), writing code, inventing tiers beyond trivial/non-trivial/complex, or running as a persistent always-on mode.
