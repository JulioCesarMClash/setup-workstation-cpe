# Distribution Guide

## Purpose

Use this repository as the public distribution source for the CPE workstation bootstrap.

## What a consumer gets

- OpenCode-first workstation bootstrap.
- Optional Claude Code installation.
- Vendored skill core and vendored optional packs.
- Machine-readable pack inventory in `pack-manifest.json`.
- Bootstrap and smoke-test scripts for Linux/macOS and Windows PowerShell.

## Recommended install flow

### Linux/macOS

```bash
git clone https://github.com/JulioCesarMClash/setup-workstation-cpe.git
cd setup-workstation-cpe
./install.sh --preset basic
```

### Windows PowerShell

```powershell
git clone https://github.com/JulioCesarMClash/setup-workstation-cpe.git
cd setup-workstation-cpe
.\install.ps1 --preset basic
```

## How to verify a release

1. Check `VERSION`.
2. Check `CHANGELOG.md`.
3. Check `pack-manifest.json` for vendored pack truth.
4. Run the smoke test and confirm vendored-pack reporting matches the manifest.
5. Generate release checksums if you are preparing downloadable artifacts: `./scripts/release-checksums.sh`

## Branch model

- `main` — public release line
- `staging` — QA and release candidate line
- `develop` — integration line

## Release process

1. Update `VERSION`.
2. Update `CHANGELOG.md`.
3. Push through `develop -> staging -> main`.
4. Create tag and GitHub release from `main`.
