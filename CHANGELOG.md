# Changelog

## v1.0.4

- Added a fresh-host smoke workflow scaffold for Linux, macOS, and Windows.
- Added uninstall and rollback support using installer state.
- Added supported platform documentation, pack presets, and one-command installer entrypoints.
- Added diagnostic install report output and release checksum generation helper.

## v1.0.3

- Added uninstall and rollback scripts based on installer state.
- Added supported platform matrix and fresh-host smoke workflow scaffold.
- Added pack presets and one-command installer entrypoints.
- Added diagnostic install report and release checksum helper.
- Improved bootstrap completion summary with explicit next steps and generated paths.

## v1.0.2

- Added guided installation documentation for first-run setup.
- Added workspace usage documentation covering agents, skill packs, and custom skills.
- Hardened bootstrap replacement behavior with `--force` protection and backups.
- Added copy fallback when skill symlinks cannot be created.
- Made smoke-test failures actionable with non-zero exit codes for missing required pieces.

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
