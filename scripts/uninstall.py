#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Uninstall or roll back the Setup Workstation CPE bootstrap")
    parser.add_argument("--opencode-config-dir", default=str(Path.home() / ".config" / "opencode"))
    parser.add_argument("--state-file", default="")
    parser.add_argument("--remove-env", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    opencode_config_dir = Path(args.opencode_config_dir)
    state_file = Path(args.state_file) if args.state_file else opencode_config_dir / ".setup-workstation-cpe-state.json"
    if not state_file.exists():
        raise SystemExit(f"State file not found: {state_file}")

    state = json.loads(state_file.read_text(encoding="utf-8"))
    config_path = Path(state.get("config_path", ""))
    config_backup = Path(state["config_backup"]) if state.get("config_backup") else None

    for skill_name in state.get("installed_skills", []):
        skill_path = opencode_config_dir / "skills" / skill_name
        if skill_path.is_symlink() or skill_path.is_file():
            skill_path.unlink(missing_ok=True)
        elif skill_path.is_dir():
            shutil.rmtree(skill_path, ignore_errors=True)

    if config_backup and config_backup.exists():
        if config_path.exists() or config_path.is_symlink():
            if config_path.is_dir():
                shutil.rmtree(config_path, ignore_errors=True)
            else:
                config_path.unlink(missing_ok=True)
        shutil.move(str(config_backup), str(config_path))
    elif config_path.exists():
        config_path.unlink(missing_ok=True)

    if args.remove_env and state.get("env_created") and state.get("env_file"):
        Path(state["env_file"]).unlink(missing_ok=True)

    state_file.unlink(missing_ok=True)
    print("Uninstall complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
