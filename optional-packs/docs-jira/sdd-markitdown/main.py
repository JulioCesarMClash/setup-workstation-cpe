#!/usr/bin/env python3
"""
sdd-markitdown/main.py

Local document ingestion wrapper for Microsoft MarkItDown.
Converts PDF/docx/xlsx/pptx/html/images to Markdown, saves to Obsidian,
and prints an ENGRAM_NOTIFY block for Claude to call mem_save.

Cost: $0 — 100% local processing.

Usage:
    python3 main.py <file>
    python3 main.py <file> --project Sandbox-ETL
    python3 main.py <file> --dry-run
    python3 main.py <file> --output /custom/path.md
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Constants ────────────────────────────────────────────────────────────────

VAULT = Path.home() / "Documents" / "BOVEDA MCP CLAUDE-OBSIDIAN"
INGESTA_DIR = VAULT / "10-Fuentes" / "Ingesta-MarkItDown"

SUPPORTED_EXT = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
    ".html", ".htm", ".csv", ".json", ".xml", ".zip",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp",
}

SIZE_WARN_MB = 50


# ─── markitdown bootstrap ─────────────────────────────────────────────────────

def _ensure_markitdown() -> None:
    try:
        import markitdown  # noqa: F401
    except ImportError:
        print("[sdd-markitdown] markitdown not found — installing via pip...", file=sys.stderr)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "markitdown[all]", "-q"],
            check=True,
        )
        print("[sdd-markitdown] markitdown installed.", file=sys.stderr)


# ─── Conversion ───────────────────────────────────────────────────────────────

def convert(file_path: Path) -> str:
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(str(file_path))
    return result.text_content


# ─── Output path ──────────────────────────────────────────────────────────────

def resolve_output(file_path: Path, override: str | None) -> Path:
    if override:
        return Path(override).expanduser()
    INGESTA_DIR.mkdir(parents=True, exist_ok=True)
    return INGESTA_DIR / f"{file_path.stem}.md"


# ─── Engram notify block ──────────────────────────────────────────────────────

def engram_notify_block(file_path: Path, output: Path, project: str, title: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        "\n"
        "─── ENGRAM_NOTIFY (Claude: ejecuta mem_save con este bloque) ───\n"
        f"title   : {title}\n"
        f"type    : discovery\n"
        f"project : {project}\n"
        f"topic_key: ingesta/{file_path.stem}\n"
        "content :\n"
        f"  **What**: Documento '{file_path.name}' convertido a Markdown e ingestado en Obsidian.\n"
        f"  **Why**: Indexación local para consultas $0 via Qwen/Gemma sin re-enviar a cloud.\n"
        f"  **Where**: {output}\n"
        f"  **Learned**: Ingestado el {ts}. Tamaño original: {file_path.stat().st_size // 1024} KB.\n"
        "─────────────────────────────────────────────────────────────────\n"
    )


# ─── Validations ──────────────────────────────────────────────────────────────

def validate(file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"[sdd-markitdown] Archivo no encontrado: {file_path}")
    if file_path.suffix.lower() not in SUPPORTED_EXT:
        raise ValueError(
            f"[sdd-markitdown] Formato no soportado: '{file_path.suffix}'. "
            f"Formatos válidos: {', '.join(sorted(SUPPORTED_EXT))}"
        )
    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > SIZE_WARN_MB:
        print(
            f"[sdd-markitdown] ADVERTENCIA: el archivo pesa {size_mb:.1f} MB (> {SIZE_WARN_MB} MB). "
            "Continuando de todas formas — puede tardar.",
            file=sys.stderr,
        )


# ─── CLI ──────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sdd-markitdown",
        description=(
            "Convierte documentos pesados a Markdown localmente (costo $0).\n"
            "Guarda en Obsidian 10-Fuentes/Ingesta-MarkItDown/ y notifica a Engram."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  %(prog)s ~/Downloads/informe.pdf\n"
            "  %(prog)s ~/Documents/datos.xlsx --project Sandbox-ETL\n"
            "  %(prog)s ~/deck.pptx --dry-run"
        ),
    )
    parser.add_argument("file", help="Ruta al archivo a convertir.")
    parser.add_argument("--output", "-o", default=None, metavar="PATH", help="Override de ruta de salida.")
    parser.add_argument("--title", default=None, help="Título para Engram (default: nombre del archivo).")
    parser.add_argument("--project", default="juliomartinez", help="Proyecto Engram (default: juliomartinez).")
    parser.add_argument("--dry-run", action="store_true", help="Muestra el markdown sin guardar.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    file_path = Path(args.file).expanduser().resolve()

    try:
        validate(file_path)
    except (FileNotFoundError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1

    output = resolve_output(file_path, args.output)

    if not args.dry_run and output.exists():
        print(
            f"[sdd-markitdown] Ya existe: {output}\n"
            "Usa --output para especificar otra ruta, o elimina el archivo existente.",
            file=sys.stderr,
        )
        return 1

    print(f"[sdd-markitdown] Convirtiendo '{file_path.name}' → Markdown (local, $0)...", file=sys.stderr)

    _ensure_markitdown()

    try:
        markdown_content = convert(file_path)
    except Exception as exc:  # noqa: BLE001
        print(f"[sdd-markitdown] Error en conversión: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(markdown_content)
        return 0

    output.write_text(markdown_content, encoding="utf-8")
    title = args.title or file_path.stem.replace("_", " ").replace("-", " ").title()

    print(f"[sdd-markitdown] Guardado en: {output}")
    print(engram_notify_block(file_path, output, args.project, title))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
