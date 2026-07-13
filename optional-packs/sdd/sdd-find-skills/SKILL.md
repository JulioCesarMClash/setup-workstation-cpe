---
name: sdd-find-skills
description: >
  Fallback skill discovery. When no static skill match is obvious, scans the
  JSON manifest in 40-AI-Toolkit/Skills-Registry.md using semantic keyword
  matching and returns the most relevant existing skill — preventing redundant
  code generation from scratch.
  Trigger: When a user request does not clearly match a known skill, or when
  you need to verify whether a skill already exists before writing custom logic.
license: MIT
metadata:
  author: gentleman-programming
  version: "1.0"
  tier: MID-HIGH
  recommended_model: gemma4:31b
  executable: ~/.skills/sdd-find-skills/main.py
---

# sdd-find-skills

## Purpose

**Contingency shield.** Prevents token waste by discovering existing skills
before falling back to custom code generation.

The script reads the JSON manifest from `40-AI-Toolkit/Skills-Registry.md`,
scores each skill against the user query (keyword + phrase matching), and
returns ranked candidates with their invocation command.

## Inputs

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | ✅ | User request or task description (positional arg) |
| `--top` | int | ❌ | Return top N results (default: 3) |
| `--threshold` | float | ❌ | Minimum score to include a result (default: 0.5) |
| `--json` | flag | ❌ | Emit results as JSON array |
| `--registry` | path | ❌ | Override registry path (default: Obsidian vault) |

## Outputs

- **stdout**: Ranked skill list with path, trigger, tier, model, and invoke command.
- **exit code 0**: At least one match found.
- **exit code 2**: No match above threshold — safe to proceed without a skill.

## Scoring Algorithm

For each skill in the manifest:
1. Token overlap: query words vs. trigger + name tokens → +1.0 per exact match, +0.5 per partial
2. Phrase bonus: full trigger phrase substring in query → +2.0
3. Name exact match bonus → +3.0

## Usage

```bash
# Basic — returns top 3 by default
python3 ~/.skills/sdd-find-skills/main.py "generate a SQL view for registrations"

# Explicit top N
python3 ~/.skills/sdd-find-skills/main.py "create GitHub issue for bug" --top 1

# JSON output for piping to local_router
python3 ~/.skills/sdd-find-skills/main.py "code review with SOLID" --json

# Zero threshold — see ALL skills ranked
python3 ~/.skills/sdd-find-skills/main.py "my query" --threshold 0
```

## Rules

- ALWAYS run this script before generating custom code for an ambiguous request.
- If exit code is 2 (no match), proceed without a skill and note the gap.
- Never auto-execute the discovered skill — return the recommendation and let the orchestrator decide.
- The manifest is the single source of truth. Never hardcode skill names.
- CRITICAL and MID-HIGH tier results should be surfaced even at lower scores (threshold 0.3 override allowed).
