#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


AGENTS = [
    "gentle-orchestrator",
    "sdd-explore",
    "sdd-propose",
    "sdd-design",
    "sdd-spec",
    "sdd-tasks",
    "sdd-apply",
    "sdd-verify",
    "sdd-archive",
    "review-risk",
    "jd-judge-a",
]

DEFAULT_SKILLS = [
    "brainstorming",
    "security-review",
    "comment-writer",
    "cognitive-doc-design",
]
OPTIONAL_PACK_SKILLS = {
    "sdd": [
        "sdd-init",
        "sdd-explore",
        "sdd-propose",
        "sdd-spec",
        "sdd-design",
        "sdd-tasks",
        "sdd-apply",
        "sdd-verify",
        "sdd-archive",
        "sdd-architecture",
        "tdd-triple-helice",
        "ollama-task-router",
        "sdd-find-skills",
        "sdd-readme-gen",
    ],
    "docs-jira": [
        "api-doc-gen",
        "confluence-doc",
        "exec-pdf-doc",
        "unified-docs-pipeline",
        "jira-evidence-formatter",
        "jira-ticket-hierarchy",
        "docx",
        "xlsx",
        "llm-wiki",
        "sdd-markitdown",
    ],
    "data-etl": ["python-testing", "etl-sec", "etl-sonar", "systematic-debugging"],
    "frontend": ["webapp-testing", "sdd-front"],
    "git-release": [
        "branch-pr",
        "issue-creation",
        "senior-vcs-commander",
        "git-branch-strategy",
        "gh-repo-bootstrap",
        "gate",
        "chained-pr",
        "using-git-worktrees",
        "work-unit-commits",
    ],
    "advanced-review": [
        "code-reviewer",
        "judgment-day",
        "ponytail-review",
        "ponytail-audit",
        "ponytail-debt",
        "ponytail-help",
        "mcp-builder",
        "skill-creator",
        "skill-improver",
        "senior-skill-architect-master",
    ],
}


def load_pack_manifest(root_dir: Path) -> dict:
    return json.loads((root_dir / "pack-manifest.json").read_text(encoding="utf-8"))


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def check_cmd(name: str) -> None:
    if shutil.which(name):
        print(f"OK   command: {name}")
    else:
        print(f"MISS command: {name}")


def check_python_runtime() -> None:
    for name in ["python3", "python", "py"]:
        if shutil.which(name):
            print(f"OK   python runtime: {name}")
            return
    print("MISS python runtime: python3/python/py")


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    manifest = load_pack_manifest(root_dir)
    env_file = Path(sys.argv[1]) if len(sys.argv) > 1 else root_dir / ".env"
    load_env(env_file)

    opencode_config_dir = Path(os.environ.get("OPENCODE_CONFIG_DIR", Path.home() / ".config" / "opencode"))
    config_file = opencode_config_dir / "opencode.json"

    failures: list[str] = []

    print("Gentle AI workspace smoke test")
    print("================================")

    required_commands = ["opencode", "node", "npm", "git"]
    optional_commands = ["claude", "ollama", "engram", "graphify", "headroom"]

    for command in required_commands:
        check_cmd(command)
        if not shutil.which(command):
            failures.append(f"missing command:{command}")

    for command in optional_commands:
        check_cmd(command)

    python_ok = False
    for name in ["python3", "python", "py"]:
        if shutil.which(name):
            print(f"OK   python runtime: {name}")
            python_ok = True
            break
    if not python_ok:
        print("MISS python runtime: python3/python/py")
        failures.append("missing python runtime")

    claude_enabled = os.environ.get("CLAUDE_CODE_ENABLED", "false").lower() == "true"
    print(f"OK   optional claude code enabled={claude_enabled}")
    if claude_enabled and not shutil.which("claude"):
        failures.append("claude enabled but command missing")
    optional_packs = [item for item in os.environ.get("GENTLE_OPTIONAL_PACKS", "").split(",") if item]
    if optional_packs:
        print(f"OK   optional packs: {', '.join(optional_packs)}")
        vendored_requested = [
            pack for pack in optional_packs if manifest.get("packs", {}).get(pack, {}).get("vendored")
        ]
        if vendored_requested:
            print(f"OK   vendored packs: {', '.join(vendored_requested)}")

    if config_file.exists():
        print(f"OK   config: {config_file}")
        config = json.loads(config_file.read_text(encoding="utf-8"))
        for agent in AGENTS:
            model = config.get("agent", {}).get(agent, {}).get("model", "<missing>")
            print(f"OK   agent: {agent} => {model}")
            if str(model).startswith("ollama/") and not shutil.which("ollama"):
                failures.append(f"ollama required by agent:{agent}")
        for mcp in ["engram", "obsidian", "obsidian-semantic", "jira", "headroom", "playwright"]:
            enabled = config.get("mcp", {}).get(mcp, {}).get("enabled", True)
            print(f"OK   mcp: {mcp} enabled={enabled}")

        skills_dir = opencode_config_dir / "skills"
        selected_skills = list(DEFAULT_SKILLS)
        seen = set(selected_skills)
        for pack_name in optional_packs:
            for skill_name in OPTIONAL_PACK_SKILLS.get(pack_name, []):
                if skill_name not in seen:
                    selected_skills.append(skill_name)
                    seen.add(skill_name)

        for skill_name in selected_skills:
            skill_path = skills_dir / skill_name
            if skill_path.is_symlink() and skill_path.exists():
                print(f"OK   skill link: {skill_name} -> {skill_path.resolve()}")
            elif skill_path.exists():
                print(f"OK   skill copy fallback: {skill_name}")
            else:
                print(f"MISS skill link: {skill_name}")
                failures.append(f"missing skill:{skill_name}")
    else:
        print(f"MISS config: {config_file}")
        failures.append("missing opencode config")

    ollama_path = shutil.which("ollama")
    if ollama_path:
        result = subprocess.run([ollama_path, "list"], capture_output=True, text=True, check=False)
        names = []
        for line in result.stdout.splitlines():
            stripped = line.strip()
            if not stripped or stripped.lower().startswith("name"):
                continue
            names.append(stripped.split()[0])
        if names:
            print("OK   ollama models:")
            for name in names:
                print(f"     - {name}")
        else:
            print("MISS ollama models: none detected")
            if any(str(config.get("agent", {}).get(agent, {}).get("model", "")).startswith("ollama/") for agent in AGENTS) if config_file.exists() else False:
                failures.append("missing ollama models")

    if failures:
        print("FAILURES:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
