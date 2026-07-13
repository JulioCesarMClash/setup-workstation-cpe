#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path


def render(text: str) -> str:
    pattern = re.compile(r"\$\{([A-Z0-9_]+)\}")

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        return os.environ.get(name, "")

    return pattern.sub(replace, text)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: render-template.py <template> <output>", file=sys.stderr)
        return 2

    template_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    rendered = render(template_path.read_text())

    parsed = json.loads(rendered)
    output_path.write_text(json.dumps(parsed, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
