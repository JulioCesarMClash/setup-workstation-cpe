# Supported Platforms

## Scope

This matrix reflects the intended and currently tested baseline for the workstation bootstrap.

## Platform Matrix

| OS | Shell | Python bootstrap path | OpenCode install path | Status |
|---|---|---|---|---|
| macOS | zsh/bash | `brew install python` fallback | `npm` or `brew` | Supported |
| Ubuntu/Debian | bash | `apt-get install python3` fallback | `npm` | Supported |
| Fedora/RHEL | bash | `dnf` or `yum` fallback | `npm` | Supported |
| Arch | bash | `pacman` fallback | `npm` | Supported |
| openSUSE | bash | `zypper` fallback | `npm` | Supported |
| Windows | PowerShell | `winget`, `choco`, or `scoop` fallback | `npm`, Chocolatey, or Scoop | Supported |

## Tooling Baseline

| Tool | Expected |
|---|---|
| Python | 3.12+ |
| Node | current LTS |
| npm | current LTS companion |
| Git | current stable |
| OpenCode | installed and runnable |

## Notes

- If a package manager is missing, bootstrap will fail with a clear message instead of pretending installation succeeded.
- Windows may require fallback copies for skill installation when symlink creation is restricted.
- Use `pack-manifest.json` as the portability source of truth for skill packs.
