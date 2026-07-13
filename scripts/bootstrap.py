#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
from typing import Iterable


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = ROOT_DIR / ".env"
DEFAULT_SOURCE_ENV = ROOT_DIR / ".env.example"
DEFAULT_OPENCODE_CONFIG_DIR = Path.home() / ".config" / "opencode"
DEFAULT_SKILLS_DIR = Path.home() / ".skills"
DEFAULT_TEMPLATE_SKILLS_DIR = ROOT_DIR / "default-skills"
OPTIONAL_PACKS_DIR = ROOT_DIR / "optional-packs"
PACK_MANIFEST_PATH = ROOT_DIR / "pack-manifest.json"
BOOTSTRAP_STATE_DIR = ROOT_DIR / ".bootstrap-state"
BOOTSTRAP_REPORT_PATH = BOOTSTRAP_STATE_DIR / "latest-install.json"
DEFAULT_SYSTEM_SKILLS = [
    "brainstorming",
    "security-review",
    "comment-writer",
    "cognitive-doc-design",
]
OPTIONAL_SKILL_PACKS = {
    "sdd": [
        "_shared",
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
    "data-etl": [
        "python-testing",
        "etl-sec",
        "etl-sonar",
        "systematic-debugging",
    ],
    "frontend": [
        "webapp-testing",
        "sdd-front",
    ],
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
PACK_PRESETS = {
    "basic": ["git-release"],
    "data": ["data-etl", "docs-jira"],
    "frontend": ["frontend", "git-release"],
    "full": ["sdd", "git-release", "docs-jira", "advanced-review", "frontend", "data-etl"],
}


def load_pack_manifest(path: Path = PACK_MANIFEST_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


PACK_MANIFEST = load_pack_manifest()

REASONING_MODEL_PREFERENCES = [
    "gemma4:31b",
    "llama3:8b",
    "llama3.1:8b",
    "mistral:7b",
]
CODING_MODEL_PREFERENCES = [
    "qwen2.5-coder:14b",
    "qwen2.5-coder:latest",
    "codellama:13b",
    "deepseek-coder:6.7b",
]


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def merge_env_text(template_text: str, updates: dict[str, str]) -> str:
    lines: list[str] = []
    seen: set[str] = set()
    for raw_line in template_text.splitlines():
        stripped = raw_line.strip()
        if stripped and not stripped.startswith("#") and "=" in raw_line:
            key, _ = raw_line.split("=", 1)
            key = key.strip()
            if key in updates:
                lines.append(f'{key}="{updates[key]}"')
                seen.add(key)
                continue
        lines.append(raw_line)

    for key, value in updates.items():
        if key not in seen:
            lines.append(f'{key}="{value}"')
    return "\n".join(lines) + "\n"


def ensure_env_file(env_file: Path, source_env: Path) -> bool:
    if env_file.exists():
        return False
    env_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_env, env_file)
    return True


def ensure_replaceable_path(path: Path, force: bool) -> Path | None:
    if not path.exists() and not path.is_symlink():
        return None

    if not force:
        raise RuntimeError(f"Refusing to replace existing path without --force: {path}")

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup = path.parent / f"{path.name}.backup-{timestamp}"
    shutil.move(str(path), str(backup))
    return backup


def detect_command_paths() -> dict[str, str | None]:
    names = [
        "claude",
        "opencode",
        "node",
        "npm",
        "git",
        "python3",
        "py",
        "python",
        "uv",
        "pipx",
        "ollama",
        "engram",
        "graphify",
        "headroom",
        "brew",
        "winget",
        "choco",
        "scoop",
        "flatpak",
        "obsidian",
        "bash",
        "curl",
        "pwsh",
        "powershell",
    ]
    return {name: shutil.which(name) for name in names}


def list_ollama_models(ollama_path: str | None) -> list[str]:
    if not ollama_path:
        return []

    result = subprocess.run(
        [ollama_path, "list"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []

    models: list[str] = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("name"):
            continue
        parts = stripped.split()
        if parts:
            models.append(parts[0].removesuffix(":latest"))
            if parts[0].endswith(":latest"):
                models.append(parts[0])
    deduped: list[str] = []
    seen: set[str] = set()
    for model in models:
        if model not in seen:
            deduped.append(model)
            seen.add(model)
    return deduped


def pick_model(available: Iterable[str], preferred: list[str]) -> str | None:
    available_list = list(available)
    for name in preferred:
        if name in available_list:
            return name
    return available_list[0] if available_list else None


def build_model_profile(has_opencode_go: bool, available_ollama_models: list[str]) -> dict[str, str]:
    reasoning_model = pick_model(available_ollama_models, REASONING_MODEL_PREFERENCES)
    coding_model = pick_model(available_ollama_models, CODING_MODEL_PREFERENCES)
    default_local = reasoning_model or coding_model
    default_small = coding_model or reasoning_model
    fallback_remote = "opencode/deepseek-v4-flash-free"

    def local_ref(model: str | None, fallback: str) -> str:
        if model:
            return f"ollama/{model}"
        return fallback

    profile = {
        "GENTLE_DEFAULT_MODEL": local_ref(default_local, fallback_remote),
        "GENTLE_SMALL_MODEL": local_ref(default_small, fallback_remote),
        "GENTLE_ORCHESTRATOR_MODEL": fallback_remote,
        "SDD_EXPLORE_MODEL": local_ref(reasoning_model, fallback_remote),
        "SDD_TASKS_MODEL": local_ref(reasoning_model, fallback_remote),
        "SDD_ARCHIVE_MODEL": local_ref(coding_model, fallback_remote),
        "REVIEW_RISK_MODEL": local_ref(reasoning_model, fallback_remote),
        "JD_JUDGE_A_MODEL": local_ref(reasoning_model, fallback_remote),
    }

    if has_opencode_go:
        profile.update(
            {
                "SDD_PROPOSE_MODEL": "opencode-go/glm-5.2",
                "SDD_DESIGN_MODEL": fallback_remote,
                "SDD_SPEC_MODEL": "opencode-go/qwen3.7-plus",
                "SDD_APPLY_MODEL": "opencode-go/deepseek-v4-pro",
                "SDD_VERIFY_MODEL": "opencode-go/deepseek-v4-pro",
            }
        )
    else:
        local_reasoning = local_ref(reasoning_model, fallback_remote)
        local_coding = local_ref(coding_model or reasoning_model, fallback_remote)
        profile.update(
            {
                "SDD_PROPOSE_MODEL": local_reasoning,
                "SDD_DESIGN_MODEL": local_reasoning,
                "SDD_SPEC_MODEL": local_reasoning,
                "SDD_APPLY_MODEL": local_coding,
                "SDD_VERIFY_MODEL": local_coding,
            }
        )

    return profile


def build_ollama_models_json(available_ollama_models: list[str]) -> str:
    models = available_ollama_models or ["gemma4:31b", "qwen2.5-coder:14b", "llama3:8b"]
    payload = {name: {"tool_call": True} for name in models}
    return json.dumps(payload, indent=8, sort_keys=True)


def build_mcp_flags(
    command_paths: dict[str, str | None],
    obsidian_vault_path: str,
    obsidian_semantic_token: str,
    jira_configured: bool,
) -> dict[str, str]:
    return {
        "HEADROOM_ENABLED_JSON": "true" if command_paths.get("headroom") else "false",
        "HEADROOM_BIN": command_paths.get("headroom") or "headroom",
        "HEADROOM_PROXY_URL": "http://127.0.0.1:8787",
        "OBSIDIAN_ENABLED_JSON": "true" if obsidian_vault_path else "false",
        "OBSIDIAN_SEMANTIC_ENABLED_JSON": "true" if obsidian_semantic_token else "false",
        "JIRA_ENABLED_JSON": "true" if jira_configured else "false",
    }


def render_template(template_path: Path, output_path: Path, values: dict[str, str]) -> None:
    template_text = template_path.read_text(encoding="utf-8")
    pattern = re.compile(r"\$\{([A-Z0-9_]+)\}")

    def replace(match: re.Match[str]) -> str:
        return values.get(match.group(1), "")

    rendered = pattern.sub(replace, template_text)
    parsed = json.loads(rendered)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(parsed, indent=2) + "\n", encoding="utf-8")


def copy_tree_contents(source: Path, target: Path) -> None:
    if not source.exists():
        return
    target.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        destination = target / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)


def resolve_skill_source(skill_name: str, source_roots: Iterable[Path]) -> Path | None:
    for root in source_roots:
        candidate_dir = root / skill_name
        if candidate_dir.is_dir() and (candidate_dir / "SKILL.md").exists():
            return candidate_dir
        candidate_file = root / f"{skill_name}.md"
        if candidate_file.is_file():
            return candidate_file
    return None


def install_skill_symlinks(
    target_dir: Path,
    skill_names: list[str],
    source_roots: list[Path],
    force: bool = False,
) -> dict[str, list[str]]:
    target_dir.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    missing: list[str] = []
    failed: list[str] = []
    copied: list[str] = []
    conflicts: list[str] = []
    backups: list[str] = []

    for skill_name in skill_names:
        source = resolve_skill_source(skill_name, source_roots)
        if not source:
            missing.append(skill_name)
            continue

        link_path = target_dir / skill_name
        if link_path.exists() or link_path.is_symlink():
            if link_path.is_symlink() and link_path.resolve() == source.resolve():
                installed.append(skill_name)
                continue
            try:
                backup = ensure_replaceable_path(link_path, force=force)
                if backup:
                    backups.append(str(backup))
            except RuntimeError:
                conflicts.append(skill_name)
                continue

        try:
            os.symlink(source, link_path, target_is_directory=source.is_dir())
            installed.append(skill_name)
        except OSError:
            try:
                if source.is_dir():
                    shutil.copytree(source, link_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source, link_path)
                copied.append(skill_name)
            except OSError:
                failed.append(skill_name)

    return {
        "installed": installed,
        "missing": missing,
        "failed": failed,
        "copied": copied,
        "conflicts": conflicts,
        "backups": backups,
    }


def resolve_skill_selection(optional_packs: list[str]) -> list[str]:
    selected: list[str] = []
    seen: set[str] = set()

    for skill_name in DEFAULT_SYSTEM_SKILLS:
        if skill_name not in seen:
            selected.append(skill_name)
            seen.add(skill_name)

    for pack_name in optional_packs:
        for skill_name in OPTIONAL_SKILL_PACKS.get(pack_name, []):
            if skill_name not in seen:
                selected.append(skill_name)
                seen.add(skill_name)

    return selected


def resolve_selected_packs(presets: list[str], explicit_packs: list[str]) -> list[str]:
    selected: list[str] = []
    seen: set[str] = set()

    for preset in presets:
        for pack_name in PACK_PRESETS.get(preset, []):
            if pack_name not in seen:
                selected.append(pack_name)
                seen.add(pack_name)

    for pack_name in explicit_packs:
        if pack_name not in seen:
            selected.append(pack_name)
            seen.add(pack_name)

    return selected


def get_vendored_pack_names() -> list[str]:
    return sorted(
        pack_name
        for pack_name, config in PACK_MANIFEST.get("packs", {}).items()
        if config.get("vendored")
    )


def build_skill_source_roots(
    optional_packs: list[str],
    explicit_skill_source_roots: list[Path],
    gentle_skills_dir: str,
) -> list[Path]:
    roots: list[Path] = [DEFAULT_TEMPLATE_SKILLS_DIR]

    for pack_name in optional_packs:
        pack_root = OPTIONAL_PACKS_DIR / pack_name
        if pack_root.exists():
            roots.append(pack_root)

    roots.extend(explicit_skill_source_roots)
    roots.extend(
        [
            Path(gentle_skills_dir).expanduser(),
            DEFAULT_SKILLS_DIR,
            Path.home() / ".config" / "opencode" / "skills",
        ]
    )

    deduped: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        normalized = root.expanduser().resolve() if root.exists() else root.expanduser()
        if normalized not in seen:
            deduped.append(root)
            seen.add(normalized)
    return deduped


def write_bootstrap_report(root_dir: Path, payload: dict) -> Path:
    report_dir = root_dir / ".bootstrap-state"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "latest-install.json"
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return report_path


def build_uninstall_state(
    opencode_config_dir: Path,
    config_backup: Path | None,
    skill_link_result: dict[str, list[str]],
    env_file: Path | None = None,
    env_created: bool = False,
) -> dict:
    installed_skills = list(skill_link_result.get("installed", [])) + list(skill_link_result.get("copied", []))
    return {
        "opencode_config_dir": str(opencode_config_dir),
        "config_path": str(opencode_config_dir / "opencode.json"),
        "config_backup": str(config_backup) if config_backup else "",
        "installed_skills": installed_skills,
        "env_file": str(env_file) if env_file else "",
        "env_created": env_created,
    }


def write_uninstall_state(opencode_config_dir: Path, state: dict) -> Path:
    state_path = opencode_config_dir / ".setup-workstation-cpe-state.json"
    opencode_config_dir.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return state_path


def validate_required_tools(command_paths: dict[str, str | None], updates: dict[str, str]) -> list[str]:
    required = ["opencode", "node", "npm", "git"]
    missing = [name for name in required if not command_paths.get(name)]

    model_values = [value for key, value in updates.items() if key.endswith("_MODEL") or key == "GENTLE_DEFAULT_MODEL"]
    if any(value.startswith("ollama/") for value in model_values) and not command_paths.get("ollama"):
        missing.append("ollama")

    seen: set[str] = set()
    deduped: list[str] = []
    for item in missing:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def scaffold_obsidian_workspace(vault_path: Path) -> None:
    files = {
        "00-MOC/MOC-Master.md": "# MOC Master\n\n- [[00-MOC/MOC-Proyectos]]\n- [[50-Projects/_TEMPLATE/Index]]\n",
        "00-MOC/MOC-Proyectos.md": "# MOC Proyectos\n\nUsa `50-Projects/<project>/` para memoria por proyecto.\n",
        "50-Projects/_TEMPLATE/Index.md": "# Project Index\n\n## Goal\n\n## Current State\n\n## Active Threads\n",
        "50-Projects/_TEMPLATE/Decisions.md": "# Decisions\n\n- Document durable technical decisions here.\n",
        "50-Projects/_TEMPLATE/Sessions/README.md": "# Sessions\n\nCreate one note per meaningful work session.\n",
    }
    for relative_path, content in files.items():
        file_path = vault_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")


def print_skill_link_summary(result: dict[str, list[str]], optional_packs: list[str]) -> None:
    if optional_packs:
        print(f"- Optional packs requested: {', '.join(optional_packs)}")
        vendored_requested = [pack for pack in optional_packs if pack in get_vendored_pack_names()]
        if vendored_requested:
            print(f"- Optional packs fully vendored: {', '.join(vendored_requested)}")
    if result["installed"]:
        print(f"- Skill symlinks installed: {', '.join(result['installed'])}")
    if result.get("copied"):
        print(f"- Skill directories copied as fallback: {', '.join(result['copied'])}")
    if result.get("backups"):
        print(f"- Backups created: {', '.join(result['backups'])}")
    if result.get("conflicts"):
        print(f"- Skill conflicts requiring --force: {', '.join(result['conflicts'])}")
    if result["missing"]:
        print(f"- Skills missing from source roots: {', '.join(result['missing'])}")
    if result["failed"]:
        print(f"- Skills failed to symlink: {', '.join(result['failed'])}")


def detect_platform_name() -> str:
    raw = platform.system().lower()
    if raw.startswith("darwin"):
        return "darwin"
    if raw.startswith("windows"):
        return "windows"
    return "linux"


def build_python_install_command(platform_name: str, command_paths: dict[str, str | None]) -> list[str] | None:
    brew_path = command_paths.get("brew")
    winget_path = command_paths.get("winget")
    choco_path = command_paths.get("choco")
    scoop_path = command_paths.get("scoop")

    if platform_name == "darwin" and brew_path:
        return [brew_path, "install", "python"]

    if platform_name == "windows":
        if winget_path:
            return [winget_path, "install", "-e", "--id", "Python.Python.3.12"]
        if choco_path:
            return [choco_path, "install", "python", "-y"]
        if scoop_path:
            return [scoop_path, "install", "python"]

    return None


def build_install_command(tool: str, platform_name: str, command_paths: dict[str, str | None]) -> list[str] | None:
    uv_path = command_paths.get("uv")
    pipx_path = command_paths.get("pipx")
    npm_path = command_paths.get("npm")
    brew_path = command_paths.get("brew")
    winget_path = command_paths.get("winget")
    choco_path = command_paths.get("choco")
    scoop_path = command_paths.get("scoop")
    flatpak_path = command_paths.get("flatpak")
    bash_path = command_paths.get("bash")
    curl_path = command_paths.get("curl")
    pwsh_path = command_paths.get("pwsh") or command_paths.get("powershell")

    if tool == "opencode":
        if npm_path:
            return [npm_path, "install", "-g", "opencode-ai"]
        if platform_name in {"darwin", "linux"} and brew_path:
            return [brew_path, "install", "anomalyco/tap/opencode"]
        if platform_name == "windows" and choco_path:
            return [choco_path, "install", "opencode", "-y"]
        if platform_name == "windows" and scoop_path:
            return [scoop_path, "install", "opencode"]

    if tool == "claude":
        if platform_name in {"darwin", "linux"} and brew_path:
            return [brew_path, "install", "--cask", "claude-code"]
        if platform_name in {"darwin", "linux"} and bash_path and curl_path:
            return [bash_path, "-lc", "curl -fsSL https://claude.ai/install.sh | bash"]
        if platform_name == "windows" and winget_path:
            return [winget_path, "install", "Anthropic.ClaudeCode"]
        if platform_name == "windows" and pwsh_path:
            return [pwsh_path, "-NoProfile", "-Command", "irm https://claude.ai/install.ps1 | iex"]

    if tool == "graphify":
        if uv_path:
            return [uv_path, "tool", "install", "graphifyy"]
        if pipx_path:
            return [pipx_path, "install", "graphifyy"]
        return [sys.executable, "-m", "pip", "install", "graphifyy"]

    if tool == "headroom":
        if uv_path:
            return [uv_path, "tool", "install", "headroom-ai[all]"]
        if pipx_path:
            return [pipx_path, "install", "headroom-ai[all]"]
        return [sys.executable, "-m", "pip", "install", "headroom-ai[all]"]

    if tool == "obsidian":
        if platform_name == "darwin" and brew_path:
            return [brew_path, "install", "--cask", "obsidian"]
        if platform_name == "windows" and winget_path:
            return [winget_path, "install", "-e", "--id", "Obsidian.Obsidian"]
        if platform_name == "linux" and flatpak_path:
            return [flatpak_path, "install", "-y", "flathub", "md.obsidian.Obsidian"]

    return None


def prompt_yes_no(message: str, default: bool, assume_yes: bool) -> bool:
    if assume_yes:
        return default

    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{message} {suffix} ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes", "s", "si"}


def prompt_text(message: str, default: str, assume_yes: bool) -> str:
    if assume_yes:
        return default
    answer = input(f"{message} [{default}] ").strip()
    return answer or default


def ensure_tool(
    tool: str,
    platform_name: str,
    command_paths: dict[str, str | None],
    assume_yes: bool,
    skip_installs: bool,
) -> dict[str, str | None]:
    if command_paths.get(tool):
        return command_paths

    if skip_installs:
        return command_paths

    install_command = build_install_command(tool, platform_name, command_paths)
    if not install_command:
        print(f"SKIP {tool}: no known automatic installer for this machine.")
        return command_paths

    if not prompt_yes_no(f"Install missing tool '{tool}'?", default=True, assume_yes=assume_yes):
        return command_paths

    print("RUN ", " ".join(install_command))
    result = subprocess.run(install_command, check=False)
    if result.returncode != 0:
        print(f"WARN {tool}: installation command failed with exit code {result.returncode}")
        return command_paths

    command_paths.update(detect_command_paths())
    return command_paths


def maybe_run_post_install_hooks(
    command_paths: dict[str, str | None],
    workspace_root: Path,
    enable_graphify_hooks: bool,
) -> None:
    if not enable_graphify_hooks:
        return

    graphify_path = command_paths.get("graphify")
    if graphify_path:
        subprocess.run([graphify_path, "install", "--platform", "opencode"], cwd=workspace_root, check=False)


def build_env_updates(
    base_env: dict[str, str],
    command_paths: dict[str, str | None],
    has_opencode_go: bool,
    enable_claude_code: bool,
    obsidian_vault_path: str,
    available_ollama_models: list[str],
    opencode_config_dir: str,
    gentle_skills_dir: str,
) -> dict[str, str]:
    jira_configured = bool(base_env.get("JIRA_URL") and base_env.get("JIRA_API_TOKEN"))
    obsidian_semantic_token = base_env.get("OBSIDIAN_SEMANTIC_TOKEN", "")

    updates = {
        "GENTLE_HOME": str(Path.home()),
        "OPENCODE_CONFIG_DIR": opencode_config_dir,
        "GENTLE_SKILLS_DIR": gentle_skills_dir,
        "OLLAMA_API": base_env.get("OLLAMA_API") or "http://localhost:11434/v1",
        "OBSIDIAN_VAULT_PATH": obsidian_vault_path,
        "OBSIDIAN_SEMANTIC_URL": base_env.get("OBSIDIAN_SEMANTIC_URL", "http://localhost:3001/mcp"),
        "OBSIDIAN_SEMANTIC_TOKEN": obsidian_semantic_token,
        "MCP_ATLASSIAN_BIN": base_env.get("MCP_ATLASSIAN_BIN", "mcp-atlassian"),
        "HEADROOM_BIN": command_paths.get("headroom") or base_env.get("HEADROOM_BIN", "headroom"),
        "CLAUDE_CODE_ENABLED": "true" if enable_claude_code else "false",
        "CLAUDE_CODE_PATH": command_paths.get("claude") or base_env.get("CLAUDE_CODE_PATH", "claude"),
        "POSTGRES_MCP_DSN": base_env.get("POSTGRES_MCP_DSN", ""),
        "POSTGRES_MCP_SSH_HOST": base_env.get("POSTGRES_MCP_SSH_HOST", ""),
        "OLLAMA_MODELS_JSON": build_ollama_models_json(available_ollama_models),
    }
    updates.update(build_model_profile(has_opencode_go, available_ollama_models))
    updates.update(
        build_mcp_flags(
            command_paths=command_paths,
            obsidian_vault_path=obsidian_vault_path,
            obsidian_semantic_token=obsidian_semantic_token,
            jira_configured=jira_configured,
        )
    )
    return updates


def install_workspace_files(opencode_config_dir: Path) -> None:
    render_template(
        ROOT_DIR / "config" / "opencode.template.json",
        opencode_config_dir / "opencode.json",
        parse_env_file(DEFAULT_ENV_FILE),
    )
    copy_tree_contents(ROOT_DIR / "prompts", opencode_config_dir / "prompts")
    copy_tree_contents(ROOT_DIR / "commands", opencode_config_dir / "commands")
    copy_tree_contents(ROOT_DIR / "skills", opencode_config_dir / "skills")


def print_summary(
    opencode_config_dir: Path,
    env_file: Path,
    obsidian_vault_path: str,
    enable_claude_code: bool,
    skill_link_result: dict[str, list[str]],
    optional_packs: list[str],
    report_path: Path | None,
    uninstall_state_path: Path | None,
) -> None:
    print("\nBootstrap complete")
    print(f"- Env file: {env_file}")
    print(f"- OpenCode config: {opencode_config_dir / 'opencode.json'}")
    print("- Primary agent runtime: OpenCode")
    print(f"- Optional Claude Code enabled for this setup: {enable_claude_code}")
    print_skill_link_summary(skill_link_result, optional_packs)
    if report_path:
        print(f"- Diagnostic report: {report_path}")
    if uninstall_state_path:
        print(f"- Uninstall state: {uninstall_state_path}")
    if obsidian_vault_path:
        print(f"- Obsidian vault scaffolded at: {obsidian_vault_path}")
    print("- Next steps:")
    print("  1. Restart OpenCode after installation.")
    print("  2. Run /connect inside OpenCode if provider access is not configured yet.")
    print("  3. Ask one simple prompt to confirm the workstation is alive.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-platform Gentle AI workspace bootstrapper")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE))
    parser.add_argument("--source-env", default=str(DEFAULT_SOURCE_ENV))
    parser.add_argument("--opencode-go", choices=["auto", "yes", "no"], default="auto")
    parser.add_argument("--claude-code", choices=["auto", "yes", "no"], default="auto")
    parser.add_argument("--vault-path", default="")
    parser.add_argument("--opencode-config-dir", default="")
    parser.add_argument("--skills-dir", default="")
    parser.add_argument("--skill-source-dir", action="append", default=[])
    parser.add_argument("--pack", action="append", default=[], choices=sorted(OPTIONAL_SKILL_PACKS.keys()))
    parser.add_argument("--preset", action="append", default=[], choices=sorted(PACK_PRESETS.keys()))
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--skip-installs", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    env_file = Path(args.env_file)
    source_env = Path(args.source_env)
    if not source_env.exists():
        print(f"Missing source env file: {source_env}", file=sys.stderr)
        return 1

    env_created = ensure_env_file(env_file, source_env)
    if env_created:
        print(f"Created env file from template: {env_file}")

    selected_packs = resolve_selected_packs(args.preset, args.pack)

    platform_name = detect_platform_name()
    command_paths = detect_command_paths()
    base_env = parse_env_file(source_env)
    if env_file.exists():
        base_env.update(parse_env_file(env_file))

    for tool in ["opencode", "graphify", "headroom", "obsidian"]:
        command_paths = ensure_tool(tool, platform_name, command_paths, args.yes, args.skip_installs)

    if args.claude_code == "yes":
        command_paths = ensure_tool("claude", platform_name, command_paths, args.yes, args.skip_installs)
        enable_claude_code = True
    elif args.claude_code == "no":
        enable_claude_code = False
    else:
        enable_claude_code = prompt_yes_no(
            "Install Claude Code as an optional secondary agent?",
            default=False,
            assume_yes=args.yes,
        )
        if enable_claude_code:
            command_paths = ensure_tool("claude", platform_name, command_paths, args.yes, args.skip_installs)

    available_ollama_models = list_ollama_models(command_paths.get("ollama"))

    if args.opencode_go == "yes":
        has_opencode_go = True
    elif args.opencode_go == "no":
        has_opencode_go = False
    else:
        has_opencode_go = prompt_yes_no("Do you have OpenCode Go access?", default=False, assume_yes=args.yes)

    obsidian_vault_path = args.vault_path or base_env.get("OBSIDIAN_VAULT_PATH", "")
    opencode_config_dir = args.opencode_config_dir or base_env.get("OPENCODE_CONFIG_DIR") or str(DEFAULT_OPENCODE_CONFIG_DIR)
    gentle_skills_dir = args.skills_dir or base_env.get("GENTLE_SKILLS_DIR") or str(DEFAULT_SKILLS_DIR)
    explicit_skill_source_roots = [Path(path).expanduser() for path in args.skill_source_dir]
    skill_source_roots = build_skill_source_roots(selected_packs, explicit_skill_source_roots, gentle_skills_dir)
    if not obsidian_vault_path and prompt_yes_no("Configure an Obsidian vault scaffold?", default=True, assume_yes=args.yes):
        default_vault = str(Path.home() / "Obsidian" / "Gentle-AI-Workspace")
        obsidian_vault_path = prompt_text("Obsidian vault path", default_vault, args.yes)

    updates = build_env_updates(
        base_env=base_env,
        command_paths=command_paths,
        has_opencode_go=has_opencode_go,
        enable_claude_code=enable_claude_code,
        obsidian_vault_path=obsidian_vault_path,
        available_ollama_models=available_ollama_models,
        opencode_config_dir=opencode_config_dir,
        gentle_skills_dir=gentle_skills_dir,
    )
    updates["GENTLE_OPTIONAL_PACKS"] = ",".join(selected_packs)
    env_text = merge_env_text(source_env.read_text(encoding="utf-8"), updates)
    env_file.write_text(env_text, encoding="utf-8")

    missing_required_tools = validate_required_tools(command_paths, updates)
    if missing_required_tools:
        print(f"Missing required tools for selected profile: {', '.join(missing_required_tools)}", file=sys.stderr)
        return 1

    opencode_config_dir = Path(updates["OPENCODE_CONFIG_DIR"])
    config_backup: Path | None = None
    config_path = opencode_config_dir / "opencode.json"
    if config_path.exists():
        try:
            current_text = config_path.read_text(encoding="utf-8")
            candidate_text = (ROOT_DIR / "config" / "opencode.template.json").read_text(encoding="utf-8")
            rendered_candidate = re.compile(r"\$\{([A-Z0-9_]+)\}").sub(lambda match: updates.get(match.group(1), ""), candidate_text)
            candidate_json = json.dumps(json.loads(rendered_candidate), indent=2) + "\n"
            if current_text != candidate_json:
                config_backup = ensure_replaceable_path(config_path, force=args.force)
                if config_backup:
                    print(f"Backed up existing OpenCode config to: {config_backup}")
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    render_template(ROOT_DIR / "config" / "opencode.template.json", opencode_config_dir / "opencode.json", updates)
    copy_tree_contents(ROOT_DIR / "prompts", opencode_config_dir / "prompts")
    copy_tree_contents(ROOT_DIR / "commands", opencode_config_dir / "commands")
    copy_tree_contents(ROOT_DIR / "skills", opencode_config_dir / "skills")
    selected_skills = resolve_skill_selection(selected_packs)
    skill_link_result = install_skill_symlinks(
        target_dir=opencode_config_dir / "skills",
        skill_names=selected_skills,
        source_roots=skill_source_roots,
        force=args.force,
    )
    if skill_link_result.get("conflicts"):
        print("Refusing to replace existing skill directories without --force.", file=sys.stderr)
        return 1

    if obsidian_vault_path:
        scaffold_obsidian_workspace(Path(obsidian_vault_path))

    uninstall_state = build_uninstall_state(
        opencode_config_dir=opencode_config_dir,
        config_backup=config_backup,
        skill_link_result=skill_link_result,
        env_file=env_file,
        env_created=env_created,
    )
    uninstall_state_path = write_uninstall_state(opencode_config_dir, uninstall_state)
    report_path = write_bootstrap_report(
        ROOT_DIR,
        {
            "status": "success",
            "packs": selected_packs,
            "vendored_packs": [pack for pack in selected_packs if pack in get_vendored_pack_names()],
            "env_file": str(env_file),
            "env_created": env_created,
            "opencode_config": str(opencode_config_dir / "opencode.json"),
            "skill_result": skill_link_result,
        },
    )

    enable_graphify_hooks = (not args.skip_installs) and prompt_yes_no(
        "Install Graphify OpenCode hooks in this workspace?",
        default=True,
        assume_yes=args.yes,
    )
    maybe_run_post_install_hooks(command_paths, ROOT_DIR, enable_graphify_hooks)
    print_summary(opencode_config_dir, env_file, obsidian_vault_path, enable_claude_code, skill_link_result, selected_packs, report_path, uninstall_state_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
