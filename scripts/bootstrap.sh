#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ensure_env_file() {
  if [[ ! -f "$ROOT_DIR/.env" && -f "$ROOT_DIR/.env.example" ]]; then
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    printf 'Created .env from .env.example\n'
  fi
}

install_python() {
  if command -v brew >/dev/null 2>&1; then
    brew install python
    return
  fi
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y python3
    return
  fi
  if command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3
    return
  fi
  if command -v yum >/dev/null 2>&1; then
    sudo yum install -y python3
    return
  fi
  if command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm python
    return
  fi
  if command -v zypper >/dev/null 2>&1; then
    sudo zypper install -y python3
    return
  fi

  printf 'Python is required and no supported package manager was found to install it automatically.\n' >&2
  exit 1
}

resolve_python() {
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
    return
  fi
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
    return
  fi

  printf 'Python not found. Attempting installation...\n'
  install_python

  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
    return
  fi
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
    return
  fi

  printf 'Python installation did not produce an executable on PATH.\n' >&2
  exit 1
}

ensure_env_file
resolve_python
"$PYTHON_BIN" "$ROOT_DIR/scripts/bootstrap.py" "$@"
