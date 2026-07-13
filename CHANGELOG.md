# Changelog

## v1.0.1

- Added best-effort Python installation in bootstrap wrappers for first-run machines.
- Added automatic `.env` creation from `.env.example` during bootstrap.
- Relaxed the required integration workflow so this bootstrap repo can promote to `staging` and `main` without a staging database unless integration is explicitly enabled.

## v1.0.0

- Initial public release of the Setup Workstation CPE bootstrap.
- OpenCode-first workstation installer with optional Claude Code installation.
- Portable vendored default skill core.
- Portable vendored optional packs: `sdd`, `git-release`, `docs-jira`, `advanced-review`, `frontend`, `data-etl`.
- Machine-readable `pack-manifest.json` plus smoke-test portability reporting.
