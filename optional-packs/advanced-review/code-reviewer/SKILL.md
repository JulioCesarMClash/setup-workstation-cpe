---
name: code-reviewer
description: >
  Code review via local Ollama senior-reviewer agent (gemma4:31b). Analyzes
  architecture, detects anti-patterns, SOLID violations, performance issues,
  and suggests refactors with code. Use when the user says "review this code",
  "revisar código", "qué está mal aquí", "code review", or invokes
  /code-reviewer. Complements ponytail-review (which only hunts complexity).
---

Route the review to the local Ollama senior-reviewer agent. Do not generate
the review yourself — delegate and synthesize.

## Steps

1. Identify the target (current diff, a file, or code passed inline).
2. Collect the code as a single context string.
3. Call local_router:
   ```bash
   ~/local-router reason "<code-context>" --agent senior-reviewer
   ```
4. Present the agent output directly. Apply ponytail to trim verbosity.
5. If there are actionable fixes, list them as a numbered checklist.

## Output format

- One finding per line: `<file>:L<N>: <issue> — <fix>`
- Group by severity: 🔴 critical / 🟡 warning / 🟢 suggestion
- If the agent suggests code: show only the changed snippet, not the full file
- End with a checklist of required changes (if any)

## Triggers

- "review this", "revisar", "code review", "qué falla", "qué mejorarías"
- `/code-reviewer`
- Automatically after large code generation sessions when user asks "is this ok?"
