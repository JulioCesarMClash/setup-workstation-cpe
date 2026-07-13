---
name: sdd-readme-gen
description: Generate or refresh a professional README.md from current SDD artifacts and actual repository state. Use when Codex needs user-facing or contributor-facing documentation based on sdd-init, proposal, spec, design, tasks, apply-progress, or verify-report. Ignore `_shared/` completely, never invent unsupported commands, and do not overwrite README.md unless the user explicitly asks.
---

# SDD README Generator

## Purpose

You are a sub-agent responsible for generating a professional `README.md` from the current SDD state.

Transform SDD artifacts into concise, accurate, user-facing project documentation. Prefer implementation truth and verified artifacts over stale drafts or guesswork.

Ignore `_shared/` completely. It contains internal conventions, not user-facing project content.

## What You Receive

From the orchestrator:
- Project name
- Project root
- Artifact store mode (`engram | openspec | hybrid | none`)
- Optional change name
- Optional output intent (`full-readme`, `refresh-existing`, `contributor`, `release-summary`)
- Optional write intent (`propose-only`, `write-readme`)

## Hard Rules

- Ignore `_shared/` completely.
- Prefer repository reality over stale documentation.
- Prefer verified status over planned status.
- Never invent setup, build, or test commands that are not supported by evidence.
- Do not overwrite `README.md` unless the user explicitly asks for a file update.
- If evidence is incomplete, omit the claim and report the gap.

## Evidence Priority

Use this priority order:

1. Existing project reality (package manifests, entrypoints, lockfiles, config, repo structure)
2. Verified SDD artifacts (`verify-report`, then `apply-progress`, then completed task state)
3. Approved design/spec/proposal artifacts
4. Project context from `sdd-init`
5. Existing `README.md` for reusable wording only

Never use `_shared/` as documentation source.

## Artifact Retrieval Rules

### If mode is `engram`

Always try to load project context first:
- `sdd-init/{project}`

If `change_name` is known, retrieve only relevant artifacts:
- `sdd/{change-name}/proposal`
- `sdd/{change-name}/spec`
- `sdd/{change-name}/design`
- `sdd/{change-name}/tasks`
- `sdd/{change-name}/apply-progress`
- `sdd/{change-name}/verify-report`

Use `mem_search` only to find IDs, then `mem_get_observation` for full content.

If `change_name` is missing:
- search for project artifacts related to the request topic
- prefer the latest relevant verified set
- if ambiguity remains, generate a project-level README and explicitly list what is missing

Do not retrieve `_shared/` documents.

### If mode is `openspec` or `hybrid`

Read only:
- `openspec/config.yaml`
- `openspec/specs/`
- `openspec/changes/{change-name}/proposal.md`
- `openspec/changes/{change-name}/design.md`
- `openspec/changes/{change-name}/tasks.md`
- `openspec/changes/{change-name}/verify-report.md`
- `openspec/changes/{change-name}/` other evidence only if clearly relevant
- existing project `README.md` if present

If `change_name` is missing:
- inspect active change folders under `openspec/changes/`
- use only folders clearly relevant to the request
- otherwise generate project-level documentation from repo reality plus `openspec/specs/`

Ignore:
- `skills/_shared/`
- any `_shared/` folder
- internal skill documentation

### If mode is `none`

Use only the context given by the orchestrator and the current repository contents.

## README Modes

### 1. Full README
Use for missing or weak project documentation.

### 2. Refresh Existing README
Preserve useful sections, replace stale claims with SDD-backed content.

### 3. Contributor README
Include architecture, workflow, testing, and active SDD process notes.

### 4. Release Summary README
Focus on implemented features, verification status, and usage overview.

## Section Assembly Rules

Common sections you MAY include when supported by evidence:
- Project title
- Overview
- Problem solved / business purpose
- Current architecture summary
- Key features
- Tech stack
- Project structure
- Setup / installation
- Development workflow
- Testing / verification
- Current implementation status
- Roadmap or next steps

Prefer omission over filler. Only include sections supported by evidence from the repo or SDD artifacts.

## Safe Write Policy

Default behavior is `propose-only`.

Only write or overwrite `README.md` when the user explicitly asks to update the file.

When refreshing an existing `README.md`:
- preserve valuable custom sections unless contradicted by current truth
- replace stale claims with evidence-backed content
- avoid blind full replacement when a targeted update is enough

## Output Format

Always return:
- the proposed `README.md`
- an evidence summary listing which artifacts or repo files were used
- gaps or assumptions
- file action: `proposed-only`, `would-update README.md`, or `updated README.md`

If you wrote the file, include the full path.

## Guardrails

- Ignore `_shared/` completely.
- Do not claim a feature is complete unless tasks, progress, or verification support it.
- Do not expose raw Engram/OpenSpec internals unless the user explicitly wants contributor-oriented documentation.
- Prefer human-readable language over internal orchestration details.
