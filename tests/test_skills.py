from __future__ import annotations

from pathlib import Path

import pytest

from akashic.cli import app
from akashic.engine.skills import (
    UnknownSkillTargetError,
    default_target,
    install_skill,
)
from akashic.engine.registry import register_knowledge_base
from akashic.engine.workspace import discover_workspace


def _init_workspace(runner, tmp_path: Path, name: str = "knowledge") -> Path:
    knowledge = tmp_path / name
    runner.invoke(app, ["init", str(knowledge)])
    return knowledge


def _bundled_skill_text() -> str:
    from akashic.skills.akashic import __path__ as skill_pkg_path

    return (Path(skill_pkg_path[0]) / "SKILL.md").read_text(encoding="utf-8")


def test_install_skill_writes_static_content_for_claude(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_workspace(runner, tmp_path)
    workspace = discover_workspace(knowledge=knowledge)
    home = tmp_path / "home-claude"
    monkeypatch.delenv("AKASHIC_GLOBAL_HOME", raising=False)

    result = install_skill(workspace, "claude", home=home)

    assert result.target == "claude"
    assert result.skill_path == home / ".claude" / "skills" / "akashic" / "SKILL.md"
    skill_text = result.skill_path.read_text(encoding="utf-8")
    assert skill_text.startswith("---\nname: akashic-knowledge")
    assert skill_text.index("## Runtime knowledge base selection") < skill_text.index("# Akashic Knowledge Base")
    assert "# Akashic Knowledge Base" in _bundled_skill_text()
    assert f"Global Akashic folder: `{home / 'akashic'}`" in skill_text
    assert f"Machine-level registry: `{home / 'akashic' / 'knowledge-bases.yaml'}`" in skill_text
    assert "Scan the global folder for child directories that contain `.akashic/config.yaml`" in skill_text
    assert "Keep only paths that exist and contain `.akashic/config.yaml`" in skill_text
    assert "Your first user-visible response must be the discovered reference list" in skill_text
    assert "Do not use an install-time snapshot" in skill_text


def test_install_skill_writes_static_content_for_codex(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_workspace(runner, tmp_path)
    workspace = discover_workspace(knowledge=knowledge)
    home = tmp_path / "home-codex"
    monkeypatch.delenv("AKASHIC_GLOBAL_HOME", raising=False)
    register_knowledge_base(knowledge, home=home)

    result = install_skill(workspace, "codex", home=home)

    assert result.target == "codex"
    assert result.skill_path == home / ".codex" / "skills" / "akashic" / "SKILL.md"
    skill_text = result.skill_path.read_text(encoding="utf-8")
    assert skill_text.startswith("---\nname: akashic-knowledge")
    assert skill_text.index("## Runtime knowledge base selection") < skill_text.index("# Akashic Knowledge Base")
    assert f"- `{knowledge.resolve()}` (knowledge)" not in skill_text


def test_install_skill_does_not_embed_snapshot_of_hidden_global_bases(
    runner,
    tmp_path: Path,
    monkeypatch,
) -> None:
    knowledge = _init_workspace(runner, tmp_path)
    workspace = discover_workspace(knowledge=knowledge)
    home = tmp_path / "home-hidden"
    monkeypatch.delenv("AKASHIC_GLOBAL_HOME", raising=False)
    hidden_base = home / "akashic" / ".checkout"
    (hidden_base / ".akashic").mkdir(parents=True)
    (hidden_base / ".akashic" / "config.yaml").write_text("version: 1\n", encoding="utf-8")

    result = install_skill(workspace, "claude", home=home)

    skill_text = result.skill_path.read_text(encoding="utf-8")
    assert f"- `{hidden_base.resolve()}` (checkout)" not in skill_text
    assert "Do not use an install-time snapshot" in skill_text


def test_install_skill_unknown_target_raises(runner, tmp_path: Path) -> None:
    knowledge = _init_workspace(runner, tmp_path)
    workspace = discover_workspace(knowledge=knowledge)

    with pytest.raises(UnknownSkillTargetError):
        install_skill(workspace, "cursor", home=tmp_path / "home")


def test_default_target_uses_configured_provider(runner, tmp_path: Path) -> None:
    knowledge = _init_workspace(runner, tmp_path)
    config_file = knowledge / ".akashic" / "config.yaml"
    config_file.write_text(
        "version: 1\n"
        "agent:\n"
        "  provider: claude\n",
        encoding="utf-8",
    )
    workspace = discover_workspace(knowledge=knowledge)

    assert default_target(workspace) == "claude"


def test_default_target_returns_none_for_unrecognized_provider(runner, tmp_path: Path) -> None:
    knowledge = _init_workspace(runner, tmp_path)
    config_file = knowledge / ".akashic" / "config.yaml"
    config_file.write_text(
        "version: 1\n"
        "agent:\n"
        "  provider: fake\n",
        encoding="utf-8",
    )
    workspace = discover_workspace(knowledge=knowledge)

    assert default_target(workspace) is None


def test_cli_add_skill_with_explicit_target(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_workspace(runner, tmp_path)
    home = tmp_path / "home"
    monkeypatch.delenv("AKASHIC_GLOBAL_HOME", raising=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))

    result = runner.invoke(app, ["--knowledge", str(knowledge), "add", "skill", "--to", "claude"])

    assert result.exit_code == 0
    skill_path = home / ".claude" / "skills" / "akashic" / "SKILL.md"
    assert skill_path.exists()
    assert "Every time this skill is invoked, discover knowledge bases before answering" in skill_path.read_text(encoding="utf-8")
    assert "Each knowledge base reference is the absolute path" in skill_path.read_text(encoding="utf-8")
    assert "Installed claude skill" in result.stdout


def test_cli_add_skill_prompts_with_config_default(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_workspace(runner, tmp_path)
    config_file = knowledge / ".akashic" / "config.yaml"
    config_file.write_text(
        "version: 1\n"
        "agent:\n"
        "  provider: codex\n",
        encoding="utf-8",
    )
    home = tmp_path / "home"
    monkeypatch.delenv("AKASHIC_GLOBAL_HOME", raising=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))

    result = runner.invoke(
        app, ["--knowledge", str(knowledge), "add", "skill"], input="\n"
    )

    assert result.exit_code == 0
    assert (home / ".codex" / "skills" / "akashic" / "SKILL.md").exists()


def test_cli_add_skill_rejects_unknown_target(runner, tmp_path: Path) -> None:
    knowledge = _init_workspace(runner, tmp_path)

    result = runner.invoke(app, ["--knowledge", str(knowledge), "add", "skill", "--to", "cursor"])

    assert result.exit_code != 0
