from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import bootstrap  # noqa: E402


def test_build_model_profile_prefers_local_models_without_opencode_go():
    profile = bootstrap.build_model_profile(
        has_opencode_go=False,
        available_ollama_models=["qwen2.5-coder:14b", "llama3:8b"],
    )

    assert profile["SDD_EXPLORE_MODEL"] == "ollama/llama3:8b"
    assert profile["SDD_PROPOSE_MODEL"] == "ollama/llama3:8b"
    assert profile["SDD_APPLY_MODEL"] == "ollama/qwen2.5-coder:14b"
    assert profile["SDD_VERIFY_MODEL"] == "ollama/qwen2.5-coder:14b"


def test_build_model_profile_keeps_go_defaults_when_available():
    profile = bootstrap.build_model_profile(
        has_opencode_go=True,
        available_ollama_models=["gemma4:31b", "qwen2.5-coder:14b"],
    )

    assert profile["SDD_PROPOSE_MODEL"] == "opencode-go/glm-5.2"
    assert profile["SDD_SPEC_MODEL"] == "opencode-go/qwen3.7-plus"
    assert profile["SDD_APPLY_MODEL"] == "opencode-go/deepseek-v4-pro"
    assert profile["SDD_EXPLORE_MODEL"] == "ollama/gemma4:31b"
    assert profile["SDD_ARCHIVE_MODEL"] == "ollama/qwen2.5-coder:14b"


def test_build_mcp_flags_enable_only_available_optional_tools():
    flags = bootstrap.build_mcp_flags(
        command_paths={
            "engram": "/usr/local/bin/engram",
            "headroom": "/usr/local/bin/headroom",
            "graphify": None,
        },
        obsidian_vault_path="/vault",
        obsidian_semantic_token="",
        jira_configured=False,
    )

    assert flags["HEADROOM_ENABLED_JSON"] == "true"
    assert flags["OBSIDIAN_ENABLED_JSON"] == "true"
    assert flags["OBSIDIAN_SEMANTIC_ENABLED_JSON"] == "false"
    assert flags["JIRA_ENABLED_JSON"] == "false"


def test_scaffold_obsidian_workspace_creates_workflow_shape(tmp_path):
    bootstrap.scaffold_obsidian_workspace(tmp_path)

    assert (tmp_path / "00-MOC" / "MOC-Master.md").exists()
    assert (tmp_path / "00-MOC" / "MOC-Proyectos.md").exists()
    assert (tmp_path / "50-Projects" / "_TEMPLATE" / "Index.md").exists()
    assert (tmp_path / "50-Projects" / "_TEMPLATE" / "Decisions.md").exists()
    assert (tmp_path / "50-Projects" / "_TEMPLATE" / "Sessions" / "README.md").exists()


def test_build_install_command_for_claude_code_prefers_winget_on_windows():
    command = bootstrap.build_install_command(
        tool="claude",
        platform_name="windows",
        command_paths={"winget": "winget", "pwsh": "pwsh"},
    )

    assert command == ["winget", "install", "Anthropic.ClaudeCode"]


def test_build_install_command_for_claude_code_uses_bash_script_on_linux_when_needed():
    command = bootstrap.build_install_command(
        tool="claude",
        platform_name="linux",
        command_paths={"bash": "/bin/bash", "curl": "/usr/bin/curl", "brew": None},
    )

    assert command == ["/bin/bash", "-lc", "curl -fsSL https://claude.ai/install.sh | bash"]


def test_resolve_skill_source_prefers_first_matching_directory(tmp_path):
    source_a = tmp_path / "skills-a"
    source_b = tmp_path / "skills-b"
    (source_b / "brainstorming").mkdir(parents=True)
    (source_b / "brainstorming" / "SKILL.md").write_text("# brainstorming\n", encoding="utf-8")

    resolved = bootstrap.resolve_skill_source("brainstorming", [source_a, source_b])

    assert resolved == source_b / "brainstorming"


def test_install_skill_symlinks_creates_valid_links(tmp_path):
    source_root = tmp_path / "skills"
    target_root = tmp_path / "installed"
    (source_root / "brainstorming").mkdir(parents=True)
    (source_root / "brainstorming" / "SKILL.md").write_text("# brainstorming\n", encoding="utf-8")

    result = bootstrap.install_skill_symlinks(
        target_dir=target_root,
        skill_names=["brainstorming"],
        source_roots=[source_root],
    )

    link_path = target_root / "brainstorming"
    assert link_path.is_symlink()
    assert link_path.resolve() == source_root / "brainstorming"
    assert result["installed"] == ["brainstorming"]
    assert result["missing"] == []


def test_resolve_skill_selection_includes_default_and_optional_pack_skills():
    selected = bootstrap.resolve_skill_selection(["sdd", "git-release"])

    assert "brainstorming" in selected
    assert "sdd-init" in selected
    assert "sdd-verify" in selected
    assert "branch-pr" in selected
    assert "gate" in selected


def test_resolve_skill_selection_deduplicates_skills():
    selected = bootstrap.resolve_skill_selection(["sdd", "sdd"])

    assert selected.count("sdd-init") == 1
    assert selected.count("brainstorming") == 1


def test_pack_manifest_marks_all_current_packs_as_vendored():
    manifest = bootstrap.load_pack_manifest()

    assert manifest["default_core"]["vendored"] is True
    assert manifest["packs"]["sdd"]["vendored"] is True
    assert manifest["packs"]["git-release"]["vendored"] is True
    assert manifest["packs"]["docs-jira"]["vendored"] is True
    assert manifest["packs"]["advanced-review"]["vendored"] is True
    assert manifest["packs"]["frontend"]["vendored"] is True
    assert manifest["packs"]["data-etl"]["vendored"] is True


def test_ensure_env_file_copies_example_when_missing(tmp_path):
    source_env = tmp_path / ".env.example"
    target_env = tmp_path / ".env"
    source_env.write_text('FOO="bar"\n', encoding="utf-8")

    created = bootstrap.ensure_env_file(target_env, source_env)

    assert created is True
    assert target_env.read_text(encoding="utf-8") == 'FOO="bar"\n'


def test_build_python_install_command_prefers_winget_on_windows():
    command = bootstrap.build_python_install_command(
        platform_name="windows",
        command_paths={"winget": "winget", "choco": None, "scoop": None},
    )

    assert command == ["winget", "install", "-e", "--id", "Python.Python.3.12"]


def test_build_python_install_command_prefers_brew_on_darwin():
    command = bootstrap.build_python_install_command(
        platform_name="darwin",
        command_paths={"brew": "brew"},
    )

    assert command == ["brew", "install", "python"]
