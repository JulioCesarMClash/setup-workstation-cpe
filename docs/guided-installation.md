# Guided Installation

## Goal

Take a new machine from clone to a working OpenCode workspace with the smallest safe path.

## Before You Start

You need:

- Git
- Internet access for package installs
- A terminal or PowerShell session with permission to install software

You do **not** need to create `.env` manually first. The bootstrap creates it from `.env.example` if missing.

## Basic Install

### Linux/macOS

```bash
git clone https://github.com/JulioCesarMClash/setup-workstation-cpe.git
cd setup-workstation-cpe
./scripts/bootstrap.sh
./scripts/smoke-test.sh
```

### Windows PowerShell

```powershell
git clone https://github.com/JulioCesarMClash/setup-workstation-cpe.git
cd setup-workstation-cpe
.\scripts\bootstrap.ps1
.\scripts\smoke-test.ps1
```

## What the Bootstrap Does

1. Creates `.env` from `.env.example` if it does not exist.
2. Tries to install Python first if the machine does not have it.
3. Tries to install the required workstation tools for the selected profile.
4. Writes `opencode.json` into your OpenCode config directory.
5. Installs the default skill core.
6. Installs any optional packs you requested.
7. Scaffolds a lightweight Obsidian workspace if you enabled it.

## Recommended First Successful Run

1. Start OpenCode:

```bash
opencode
```

2. If provider access is not configured yet, run:

```text
/connect
```

3. Ask one simple prompt to confirm the workspace is alive:

```text
What agent am I using and which skill packs are installed?
```

If that works, the workstation is usable.

## Safe Re-run Rule

If you rerun bootstrap on a machine that already has OpenCode config or installed skill directories, use `--force` only when you intentionally want replacement.

Without `--force`, bootstrap refuses to replace existing config/skill paths.

## Optional Packs

Examples:

```bash
./scripts/bootstrap.sh --pack sdd --pack git-release
./scripts/bootstrap.sh --pack docs-jira --pack advanced-review
./scripts/bootstrap.sh --pack frontend --pack data-etl
```

Use `pack-manifest.json` to see which packs are fully vendored.

## If the Smoke Test Fails

Treat it as a real install failure.

- `MISS command: ...` means a required dependency is still missing.
- `MISS config: ...` means OpenCode config was not generated.
- `MISS skill link: ...` means a selected skill was not installed correctly.
- Non-zero exit means the workstation is not ready yet.
