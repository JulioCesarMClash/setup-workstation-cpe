#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-$ROOT_DIR/.env}"
TEMPLATE_FILE="$ROOT_DIR/config/opencode.template.json"

if [[ ! -f "$ENV_FILE" ]]; then
  printf 'Missing env file: %s\n' "$ENV_FILE" >&2
  printf 'Copy .env.example to .env, fill local values, then rerun.\n' >&2
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

: "${OPENCODE_CONFIG_DIR:=$HOME/.config/opencode}"
: "${GENTLE_SKILLS_DIR:=$HOME/.skills}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    return 1
  fi
}

require_cmd node
require_cmd npm
require_cmd python3
require_cmd git

if ! command -v opencode >/dev/null 2>&1; then
  printf 'Warning: opencode command not found. Install opencode before using the generated config.\n' >&2
fi

if ! command -v ollama >/dev/null 2>&1; then
  printf 'Warning: ollama command not found. Local Ollama models will not work until installed.\n' >&2
fi

mkdir -p "$OPENCODE_CONFIG_DIR" "$OPENCODE_CONFIG_DIR/prompts/sdd" "$OPENCODE_CONFIG_DIR/commands" "$OPENCODE_CONFIG_DIR/skills" "$GENTLE_SKILLS_DIR"

TARGET="$OPENCODE_CONFIG_DIR/opencode.json"
if [[ -f "$TARGET" ]]; then
  BACKUP="$TARGET.backup-$(date +%Y%m%d_%H%M%S)"
  cp "$TARGET" "$BACKUP"
  printf 'Backed up existing config to %s\n' "$BACKUP"
fi

python3 "$ROOT_DIR/scripts/render-template.py" "$TEMPLATE_FILE" "$TARGET"

if [[ -d "$ROOT_DIR/prompts" ]]; then
  cp -R "$ROOT_DIR/prompts/." "$OPENCODE_CONFIG_DIR/prompts/"
fi

if [[ -d "$ROOT_DIR/commands" ]]; then
  cp -R "$ROOT_DIR/commands/." "$OPENCODE_CONFIG_DIR/commands/"
fi

if [[ -d "$ROOT_DIR/skills" ]]; then
  cp -R "$ROOT_DIR/skills/." "$OPENCODE_CONFIG_DIR/skills/"
fi

printf 'Installed Gentle AI OpenCode template at %s\n' "$OPENCODE_CONFIG_DIR"
printf 'Restart opencode so it reloads the new config.\n'
