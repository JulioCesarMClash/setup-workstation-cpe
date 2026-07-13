#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_ENV_FILE="${1:-$ROOT_DIR/.env.example}"
KEEP_TEMP_HOME="${KEEP_TEMP_HOME:-0}"
TMP_BASE="${TMPDIR:-/tmp}"
TMP_BASE="${TMP_BASE%/}"
TMP_HOME="$(mktemp -d "$TMP_BASE/gentle-ai-home.XXXXXX")"
TMP_ENV_FILE="$TMP_HOME/test.env"

if [[ ! -f "$SOURCE_ENV_FILE" ]]; then
  printf 'Missing source env file: %s\n' "$SOURCE_ENV_FILE" >&2
  exit 1
fi

cleanup() {
  local exit_code=$?

  if [[ "$KEEP_TEMP_HOME" == "1" || $exit_code -ne 0 ]]; then
    printf '\nTemp HOME kept at %s\n' "$TMP_HOME"
    printf 'Temp env file: %s\n' "$TMP_ENV_FILE"
    return
  fi

  rm -rf "$TMP_HOME"
}

trap cleanup EXIT

cp "$SOURCE_ENV_FILE" "$TMP_ENV_FILE"

printf 'Temporary HOME: %s\n' "$TMP_HOME"
printf 'Using env file: %s\n\n' "$SOURCE_ENV_FILE"

HOME="$TMP_HOME" python3 "$ROOT_DIR/scripts/bootstrap.py" \
  --skip-installs \
  --yes \
  --opencode-go "${OPENCODE_GO_MODE:-no}" \
  --env-file "$TMP_ENV_FILE" \
  --opencode-config-dir "$TMP_HOME/.config/opencode" \
  --skills-dir "$TMP_HOME/.skills" \
  --vault-path "$TMP_HOME/Obsidian/Gentle-AI-Workspace"

printf '\n'
HOME="$TMP_HOME" "$ROOT_DIR/scripts/smoke-test.sh" "$TMP_ENV_FILE"

printf '\nRendered config: %s\n' "$TMP_HOME/.config/opencode/opencode.json"

if [[ "$KEEP_TEMP_HOME" != "1" ]]; then
  printf 'Set KEEP_TEMP_HOME=1 to inspect the temp HOME after the run.\n'
fi
