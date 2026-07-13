# Replication Audit

## Verdict

The system is replicable after sanitization. The architecture is reusable; the current personal machine profile is not.

## Replicable Core

| Component | Decision |
|---|---|
| Agent routing | Keep as template |
| OpenCode as primary runtime | Keep as default |
| Claude Code install | Offer as optional secondary agent |
| SDD sub-agent model map | Keep as environment-configurable defaults |
| MCP topology | Keep core enabled, optional integrations disabled by default |
| Skills layout | Keep, but package reusable skills explicitly |
| Default skill distribution | Install a minimal core by symlink, not copy |
| Permissions | Keep safety defaults for destructive Git and secret reads |
| Smoke tests | Required after bootstrap |

## Must Not Be Copied Directly

| Item | Risk | Fix |
|---|---|---|
| Jira/Confluence tokens | Credential leak | Move to `.env` and rotate if exposed |
| Obsidian bearer token | Vault access leak | Move to `.env` |
| Postgres DSN/password | Database access leak | Move to `.env`; prefer read-only user |
| `/Users/juliomartinez/...` paths | Non-portable | Replace with `$HOME`/env vars |
| Local vault name | Personal workspace leak | Use `OBSIDIAN_VAULT_PATH` |

## Installability Checklist

- [ ] OpenCode installed
- [ ] Claude Code installed only if the user wants the optional secondary agent
- [ ] Node/npm installed
- [ ] Python 3 installed
- [ ] Git installed
- [ ] Ollama installed when local models are used
- [ ] Required Ollama models pulled
- [ ] `.env` created from `.env.example`
- [ ] Optional MCP credentials configured only when needed
- [ ] `scripts/bootstrap.sh` or `scripts/bootstrap.ps1` completed
- [ ] `scripts/smoke-test.sh` or `scripts/smoke-test.ps1` completed
- [ ] OpenCode restarted

## Smoke Test Expectations

| Check | Expected |
|---|---|
| `gentle-orchestrator` | Stable remote default (`opencode/deepseek-v4-flash-free`) |
| `sdd-explore` | Best available local reasoning model |
| `sdd-propose` | OpenCode Go default when available, else local reasoning fallback |
| `sdd-design` | OpenCode Go or remote/local reasoning fallback |
| `sdd-spec` | OpenCode Go default when available, else local reasoning fallback |
| `sdd-tasks` | Best available local reasoning model |
| `sdd-apply` | OpenCode Go default when available, else local coding fallback |
| `sdd-verify` | OpenCode Go default when available, else local coding fallback |
| `sdd-archive` | Best available local coding model |
| `review-risk` | Reasoning-capable fallback model |
| `jd-judge-a` | Reasoning-capable fallback model |

## Recommended Packaging Rule

Ship three layers:

| Layer | Content |
|---|---|
| Core template | Agents, prompts, permissions, docs, install scripts |
| User profile | `.env`, local paths, provider choices |
| Optional integrations | Jira, Obsidian, Postgres, Graphify, Playwright |

## Machine-Readable Portability Source

- `pack-manifest.json` is the machine-readable source of truth for the default core and optional pack portability state.
- Bootstrap and smoke-test reporting must derive vendored-pack status from this manifest, not from ad hoc path guessing.

## Default Skill Core Decision

- Install only a small default core: `brainstorming`, `security-review`, `comment-writer`, `cognitive-doc-design`.
- Package those four skills inside the template itself and materialize them in `OPENCODE_CONFIG_DIR/skills` as symlinks to the packaged source by default.
- Verify those links in the smoke test so the installer proves the runtime can actually resolve them.
- Keep highly coupled workflow skills, Jira skills, ETL-specific skills, frontend-specific skills, and heavy local-model governance skills out of the default bootstrap.
- Optional packs are selectable and symlinked too, but unless they are separately vendored they remain best-effort and resolve from additional skill source roots (`~/.skills`, `~/.config/opencode/skills`, or explicit `--skill-source-dir`).
- The `sdd` optional pack is now vendored locally under `optional-packs/sdd/`, including `_shared` support files, so it is portable the same way as the default core.
- The `git-release` optional pack is now vendored locally under `optional-packs/git-release/`, including its references/checklists/assets, so release and Git workflow helpers no longer depend on host-level skill roots.
- The `docs-jira` optional pack is now vendored locally under `optional-packs/docs-jira/`, including its assets and helper scripts, so documentation and Jira publishing helpers install portably from the template.
- The `advanced-review` optional pack is now vendored locally under `optional-packs/advanced-review/`, including references, so review/audit/MCP/skill-authoring helpers install portably from the template.
- The `frontend` optional pack is now vendored locally under `optional-packs/frontend/`, so frontend testing and Angular-focused workflow helpers install portably from the template.
- The `data-etl` optional pack is now vendored locally under `optional-packs/data-etl/`, so ETL testing, security, static analysis, and systematic debugging helpers install portably from the template.
