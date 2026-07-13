---
name: ollama-task-router
description: Deliberate task complexity and choose whether to keep work in native Claude Code or execute a local Ollama command. Use for coding, refactoring, documentation, test generation, or analysis requests where cost-sensitive local routing may help. Prefer Claude for critical architecture/security/SDD design, gemma4:31b for mid-high local reasoning and refactors, qwen2.5-coder:14b for boilerplate and repetitive code (including Go-specific tier mapping), and Haiku for quick frontend structuring.
---

# Ollama Task Router

Use this workflow before solving non-trivial implementation, analysis, refactor, test, or documentation tasks.

## 1) Classify the task

Choose one tier:

- **CRITICAL** → architecture, SDD propose/spec/design, security/auth, production RCA, critical bugs
- **MID-HIGH** → multi-file refactors, heavy local reasoning, broad code digestion, non-critical analysis
- **QUICK-FRONTEND** → fast UI/component structuring, CSS/templates, light frontend logic
- **BOILERPLATE** → repetitive tests, docstrings, docs, renames, type stubs, simple scaffolding

## 2) Route by default

- **CRITICAL** → stay in Claude (`opus` or `sonnet`)
- **MID-HIGH** → use local Ollama `gemma4:31b` when a local draft/analysis is sufficient
- **QUICK-FRONTEND** → stay in Claude `haiku`
- **BOILERPLATE** → use local Ollama `qwen2.5-coder:14b`
- **Uncertain** → stay in Claude `sonnet`

## 3) Mandatory Ollama protocol

If routing to Ollama:

1. Before running the command, state which local model you will use and why.
2. Run `ollama run <model> "<prompt>"`.
3. After it finishes, explicitly say it was a **local Ollama execution**.
4. Always report **API cost: $0**.
5. If token counts are not shown by Ollama, say exactly: **"Token count not exposed by Ollama in this run."**
6. Never imply an Ollama command used Anthropic API tokens.

## 4) Output format

### If using Claude directly

- State the chosen tier
- State why it stays in Claude instead of Ollama
- Then perform the task normally

### If using Ollama

Use this structure:

- **Tier:** <tier>
- **Routing decision:** Using local Ollama with `<model>` because <reason>
- Run the command
- Return the result
- End with:
  - **Execution:** Local Ollama
  - **API cost:** $0
  - **Tokens:** Token count not exposed by Ollama in this run.

## 5) Safety rule

Do not use local Ollama for SDD propose/spec/design, security/auth, or production bug RCA unless the user explicitly asks for a local-only draft.

## 6) Go-specific routing

When the task is Go (writing Go code, Go tests, Go refactors, Go boilerplate), apply this Go-specific tier mapping INSTEAD of the general one in §2. Go's strong typing makes delegated boilerplate safer (the compiler catches errors), but concurrency is CRITICAL and must not be delegated.

### Tier mapping Go → installed model

| Tier Go | Model | Router mode | When |
|---|---|---|---|
| CRITICAL | (stay in Claude) | — | concurrency (goroutines/channels/select), interface design, architecture, SDD propose/spec/design, security/auth, production RCA |
| MID-HIGH | `gemma4:31b` | `reason --full` | package reorg, error strategy review, Bubbletea `Model.Update()` state transitions, non-trivial algorithms, multi-file refactors |
| BOILERPLATE | `qwen2.5-coder:14b` | `code --full` | table-driven tests, mock implementations, type stubs, getters/setters, doc comments, renames |
| QUICK-FRONTEND | (stay in Claude) | — | Bubbletea component structuring, TUI layout, CSS/templates |

### Invocation (Go)

```bash
# BOILERPLATE — Go tests / stubs / mocks
python3 ~/local-wrapper/local_router.py code \
  "<prompt>" --agent go-testing --full

# MID-HIGH — analysis / refactor reasoning
python3 ~/local-wrapper/local_router.py reason \
  "<prompt>" --agent senior-reviewer --full
```

Rules:

- `--full` is MANDATORY for `code` mode (structs/tests must not be truncated at 500 chars).
- `--agent go-testing` injects the `go-testing/SKILL.md` as prompt context.
- `--agent senior-reviewer` injects the senior reviewer prompt for MID-HIGH analysis.
- If Ollama is unreachable (`127.0.0.1:11434` down), say so explicitly and stay in Claude.

### TDD Triple Helice (Go)

When Strict TDD Mode is active (per `sdd-apply` / `tdd-triple-helice`):

- Step 2a (tests-first) → `qwen2.5-coder:14b` via `code --agent go-testing --full` (BOILERPLATE tier).
- Step 2b (minimal implementation) → stay in Claude if CRITICAL; `qwen2.5-coder:14b` if BOILERPLATE.
- Step 3 (verify RED→GREEN) → Claude runs `go test ./...` (NOT delegable — verification is human-in-the-loop).

### Post-Ollama verification gate (MANDATORY for Go)

Ollama output is a DRAFT, never final. Before accepting any Ollama-generated Go code:

```bash
gofmt -l <file>      # must return empty
go vet ./...         # must pass
go build ./...       # must compile
go test ./...        # must pass (if it generated tests)
```

If any check fails → Claude corrects inline (do NOT re-delegate blindly).

### Report format (Go, extends §4)

After every Go delegation, add the verification gate status:

```
- Tier: <tier>
- Routing decision: <model> via <mode> because <reason>
- [output]
- Execution: Local Ollama
- API cost: $0
- Tokens: Token count not exposed by Ollama in this run.
- Verification: gofmt <status> / go vet <status> / go build <status> / go test <status>
```

### Installed models reference (verified 2026-06-20)

- `gemma4:31b` (19 GB) — MID-HIGH reasoning
- `qwen2.5-coder:14b` (9 GB) — BOILERPLATE code generation
- `qwen3-coder:30b` is NOT installed — do not reference it.
