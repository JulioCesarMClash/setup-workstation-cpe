#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/.release-artifacts"
mkdir -p "$OUT_DIR"

TARBALL="$OUT_DIR/setup-workstation-cpe-source.tar.gz"
ZIPFILE="$OUT_DIR/setup-workstation-cpe-source.zip"
CHECKSUMS="$OUT_DIR/SHA256SUMS.txt"

tar -czf "$TARBALL" -C "$ROOT_DIR" .
zip -qr "$ZIPFILE" "$ROOT_DIR"

shasum -a 256 "$TARBALL" "$ZIPFILE" > "$CHECKSUMS"
printf 'Generated checksums at %s\n' "$CHECKSUMS"
