# Setup Workstation CPE

Portable workstation bootstrap for CPE contributors. It installs an OpenCode-first workspace with vendored skill packs, optional Claude Code, and a validated bootstrap/smoke-test flow for new machines.

This repository packages the reusable workstation architecture only. It does not include personal secrets, local vault paths, Jira tokens, database passwords, or user-specific machine paths.

## Quick Start

```bash
cp .env.example .env
# Linux/macOS
./scripts/bootstrap.sh --pack sdd --pack git-release
./scripts/smoke-test.sh
```

```powershell
# Windows PowerShell
Copy-Item .env.example .env
.\scripts\bootstrap.ps1 --pack sdd --pack git-release
.\scripts\smoke-test.ps1
```

The bootstrap asks whether the user has OpenCode Go access. If not, it falls back to the available local models instead of forcing the exact models used on your machine.

It also asks whether to install Claude Code as an optional secondary agent. OpenCode remains the main configured workspace runtime.

When supported on the host, the bootstrap can attempt to install missing tools such as OpenCode, Claude Code, Graphify, Headroom, and Obsidian. It also scaffolds a lightweight Obsidian workflow structure so teams keep the same way of working even if their vault tree is not identical to yours.

The bootstrap also installs a small default skill core as symlinks into `OPENCODE_CONFIG_DIR/skills` and the smoke test verifies those links resolve correctly. That core is packaged inside this template, so third-party users do not need your personal `~/.skills` tree just to bootstrap successfully.

For fast installer iteration without touching your real profile:

```bash
./scripts/temp-home-test.sh
# or keep the temp HOME to inspect results
KEEP_TEMP_HOME=1 ./scripts/temp-home-test.sh .env
# force the temp test to simulate a non-OpenCode-Go setup
OPENCODE_GO_MODE=no ./scripts/temp-home-test.sh
```

Restart OpenCode after installation. OpenCode loads config at startup.

## Release

- Current version: `v1.0.0`
- Release artifact source of truth: `pack-manifest.json`
- Distribution guide: `docs/distribution-guide.md`

## What This Installs

| Area | Purpose |
|---|---|
| `config/opencode.template.json` | Sanitized OpenCode config with placeholders |
| `prompts/sdd/` | Minimal SDD phase prompts |
| `scripts/bootstrap.py` | Cross-platform bootstrap core |
| `scripts/smoke-test.sh` | Checks dependencies and agent/model routing |
| `pack-manifest.json` | Machine-readable inventory of vendored core/packs |
| `docs/architecture-map.md` | System map and diagrams |
| `docs/replication-audit.md` | Portability and security audit |

## Default Skill Core

| Skill | Why it is default |
|---|---|
| `brainstorming` | Safe pre-work tiering and option framing across many projects |
| `security-review` | Broad defensive value without binding users to one company workflow |
| `comment-writer` | Useful collaboration output with low coupling |
| `cognitive-doc-design` | Improves docs/readmes/guides without assuming Jira, ETL, or Obsidian |

Everything else should be treated as opt-in packs or environment-specific add-ons.

## Optional Packs

| Pack | Purpose |
|---|---|
| `sdd` | Full SDD workflow and its supporting orchestration/testing helpers |
| `docs-jira` | Documentation publishing, Jira evidence, Word/Excel, ingestion helpers |
| `data-etl` | Python testing plus ETL security/quality/debugging skills |
| `frontend` | Frontend-specific testing and UI workflow skills |
| `git-release` | PR, issue, branch, release, and worktree workflow skills |
| `advanced-review` | Heavier review, audit, MCP, and skill-authoring helpers |

Example without personal skill directories:

```bash
./scripts/bootstrap.sh --pack sdd --pack docs-jira
```

Optional packs are installed by symlink too. The bootstrap prefers packaged local skills when present and falls back to additional skill source roots when available.

Today, the default core and the full `sdd`, `git-release`, `docs-jira`, `advanced-review`, `frontend`, and `data-etl` packs are vendored inside this template. The canonical machine-readable source of truth is `pack-manifest.json`.

## Third-Party Onboarding

Recommended flow for a new machine:

1. Copy `.env.example` to `.env`.
2. Run `bootstrap.sh` or `bootstrap.ps1` with the packs you want.
3. Run the smoke test.
4. Confirm the output says which requested packs are `fully vendored`.
5. Restart OpenCode and begin from the installed workspace config.

Example:

```bash
./scripts/bootstrap.sh --pack sdd --pack git-release --pack docs-jira
./scripts/smoke-test.sh
```

## Required Dependencies

| Dependency | Why |
|---|---|
| OpenCode | Primary agent runtime |
| Node/npm | MCP servers and tooling |
| Python 3 | Template rendering and smoke tests |
| Git | Project workflows |
| Ollama | Local models for SDD exploration/tasks |

## Optional Agent

| Agent | Role |
|---|---|
| Claude Code | Optional secondary agent for users who also want Anthropic's terminal workflow installed locally |

## Optional Integrations

| Integration | Required When |
|---|---|
| Engram | Persistent memory is desired |
| Obsidian Semantic | Vault-backed project memory is desired |
| Jira/Confluence MCP | Jira-gated workflows are required |
| Playwright MCP | Browser testing is required |
| Graphify | Codebase graph navigation is required |

## Security Rule

Never commit a rendered `opencode.json` if it contains real credentials. Commit only the template and `.env.example`.
