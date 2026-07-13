#!/usr/bin/env python3
"""
sdd-find-skills/main.py

Fallback skill discovery. Reads the JSON manifest from Skills-Registry.md,
scores each skill against the user query, and returns the best match(es).

Run this BEFORE generating custom code from scratch.

Usage:
    python3 main.py "user query"
    python3 main.py "user query" --top 3
    python3 main.py "user query" --json
    python3 main.py "user query" --threshold 0

Exit codes:
    0 — at least one match found
    1 — error (registry not found / JSON parse failure)
    2 — no match above threshold (safe to proceed without a skill)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ─── Registry path ────────────────────────────────────────────────────────────

REGISTRY_PATH = (
    Path(os.environ.get(
        "CLAUDE_VAULT_PATH",
        str(Path.home() / "Developer" / "BOVEDA MCP CLAUDE-OBSIDIAN"),
    ))
    / "40-AI-Toolkit"
    / "Skills-Registry.md"
)
if not REGISTRY_PATH.exists():
    print(f"[warning] Skills registry not found: {REGISTRY_PATH}", file=sys.stderr)

# ─── Manifest extraction ──────────────────────────────────────────────────────

def load_manifest(path: Path) -> list[dict]:
    """Extract the JSON manifest block from Skills-Registry.md."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON manifest block found in {path}")
    return json.loads(match.group(1))


# ─── Scoring ──────────────────────────────────────────────────────────────────

_STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "for", "of", "in", "to", "with",
    "from", "on", "by", "is", "are", "be", "it", "at",
    "que", "de", "la", "el", "en", "un", "una", "con", "por", "para", "los",
})


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-záéíóúüñA-Z\w]+", text.lower())
    return [w for w in words if w not in _STOP_WORDS and len(w) > 1]


def score_skill(skill: dict, query_tokens: list[str], query_raw: str) -> float:
    corpus = " ".join([
        skill.get("name", ""),
        skill.get("trigger", ""),
        skill.get("routing_tier", ""),
        skill.get("recommended_model", ""),
    ]).lower()

    corpus_tokens = _tokens(corpus)
    score = 0.0

    for qt in query_tokens:
        if qt in corpus_tokens:
            score += 1.0
        elif any(qt in ct for ct in corpus_tokens):
            score += 0.5

    query_lower = query_raw.lower()
    for phrase in re.split(r"[,;/]+", skill.get("trigger", "")):
        phrase = phrase.strip()
        if phrase and phrase in query_lower:
            score += 2.0

    if skill.get("name", "").lower() in query_lower:
        score += 3.0

    return score


def rank_skills(
    manifest: list[dict],
    query: str,
    threshold: float = 0.5,
) -> list[tuple[float, dict]]:
    tokens = _tokens(query)
    scored = [(score_skill(s, tokens, query), s) for s in manifest]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(sc, sk) for sc, sk in scored if sc >= threshold]


# ─── Output formatters ────────────────────────────────────────────────────────

def _format_human(ranked: list[tuple[float, dict]], top: int) -> str:
    if not ranked:
        return (
            "[sdd-find-skills] No match found above threshold.\n"
            "No existing skill covers this query — safe to proceed without one.\n"
        )

    lines = [f"[sdd-find-skills] Top {min(top, len(ranked))} match(es):\n"]
    for i, (sc, sk) in enumerate(ranked[:top], 1):
        lines.append(f"  {i}. {sk['name']}  (score: {sc:.1f})")
        lines.append(f"     path:    {sk['path']}")
        lines.append(f"     trigger: {sk['trigger']}")
        lines.append(f"     tier:    {sk['routing_tier']}  |  model: {sk['recommended_model']}")
        agent = sk["name"]
        lines.append(f"     invoke:  ~/local-router reason \"<task>\" --agent {agent}")
        lines.append("")
    return "\n".join(lines)


def _format_json(ranked: list[tuple[float, dict]], top: int) -> str:
    out = [{"score": round(sc, 2), **sk} for sc, sk in ranked[:top]]
    return json.dumps(out, indent=2, ensure_ascii=False)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sdd-find-skills",
        description=(
            "Fallback skill discovery.\n"
            "Scans Skills-Registry.md JSON manifest and returns the best matching skill.\n"
            "Run this BEFORE generating custom code from scratch."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s 'generate SQL view for registrations'\n"
            "  %(prog)s 'create GitHub issue for bug' --top 1\n"
            "  %(prog)s 'code review SOLID violations' --json\n"
            "  %(prog)s 'my request' --threshold 0"
        ),
    )
    parser.add_argument("query", help="User request or task description.")
    parser.add_argument(
        "--top", type=int, default=3, metavar="N",
        help="Return top N results (default: 3).",
    )
    parser.add_argument(
        "--threshold", type=float, default=0.5, metavar="F",
        help="Minimum score to include a result (default: 0.5).",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit results as JSON array.",
    )
    parser.add_argument(
        "--registry", default=str(REGISTRY_PATH), metavar="PATH",
        help="Override registry file path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = Path(args.registry)

    if not registry.exists():
        print(
            f"[sdd-find-skills] ERROR: registry not found at {registry}",
            file=sys.stderr,
        )
        return 1

    try:
        manifest = load_manifest(registry)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"[sdd-find-skills] ERROR parsing manifest: {exc}", file=sys.stderr)
        return 1

    ranked = rank_skills(manifest, args.query, threshold=args.threshold)

    if args.json:
        print(_format_json(ranked, args.top))
    else:
        print(_format_human(ranked, args.top))

    return 0 if ranked else 2


if __name__ == "__main__":
    raise SystemExit(main())
