# Workspace Usage

## Goal

Explain how to use the installed workstation once bootstrap is complete.

## Start OpenCode

```bash
opencode
```

The installed config is OpenCode-first. `gentle-orchestrator` is the primary agent in this workstation.

## How Agent Selection Works

- By default, the workspace starts around the configured primary agent.
- You can explicitly start the TUI with an agent using:

```bash
opencode --agent gentle-orchestrator
```

- The hidden SDD/review agents in `opencode.json` are subagents. They are not the normal entry point. The orchestrator delegates to them when needed.

## How Skills Work

- Skills are discovered from:
  - `GENTLE_SKILLS_DIR`
  - `OPENCODE_CONFIG_DIR/skills`
- The agent can load skills on demand through OpenCode's native skill tool.
- Skills are **not** slash commands by default unless the skill defines slash support explicitly.

## What Loads Automatically vs On Demand

### Automatic behavior

- The primary agent configuration is always active.
- Installed skill packs are available for discovery.
- The agent may decide to load a relevant skill when the task matches it.

### On-demand behavior

- Hidden subagents like `sdd-explore`, `sdd-apply`, `review-risk`, or `jd-judge-a` are invoked by the orchestrator when the workflow calls for them.
- Skills are loaded only when relevant. Having a skill installed does not mean it always runs.

## Basic Usage Pattern

Use plain language first:

```text
Review this bootstrap flow for onboarding risks.
```

```text
Create an SDD proposal for adding a new optional pack.
```

```text
Generate docs for this release.
```

The orchestrator should choose the right subagent or skill path when the config and skills are installed correctly.

## Quick Map of Packs

- `sdd` — structured design and implementation workflow
- `git-release` — PR, branch, release, and workflow operations
- `docs-jira` — publishing, Jira evidence, doc generation, Word/Excel helpers
- `advanced-review` — audits, review helpers, MCP/skill authoring support
- `frontend` — frontend-specific helpers
- `data-etl` — ETL/testing/security helpers

## How to Add Your Own Skills

Recommended path:

1. Create a new folder under your user skill directory or project skill directory.
2. Add `SKILL.md`.
3. Keep the skill self-contained when possible.
4. Re-run bootstrap only if you want the skill linked into `OPENCODE_CONFIG_DIR/skills`.

Example layout:

```text
~/.skills/my-new-skill/
  SKILL.md
```

Or inside the project/template itself:

```text
optional-packs/my-pack/my-new-skill/
  SKILL.md
```

## Minimal `SKILL.md`

```markdown
---
name: my-new-skill
description: Short trigger-first description of what the skill is for.
---

# My New Skill

## When to Use

Describe when the agent should load it.

## Rules

- Keep instructions concrete.
- Prefer exact behavior over vague advice.
```

## When to Rerun Bootstrap

Rerun bootstrap when:

- you want to install new optional packs
- you changed the vendored skill set
- you intentionally want to replace the OpenCode config

Use `--force` only when you want bootstrap to replace existing config/skills after taking backups.
