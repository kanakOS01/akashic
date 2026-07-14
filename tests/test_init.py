from __future__ import annotations

import os
import subprocess
from pathlib import Path

from akashic.cli import app
from akashic.engine.config import load_config
from akashic.engine.global_config import load_global_config
from akashic.engine.workspace import WorkspaceNotFoundError, discover_workspace


def test_init_scaffolds_repo_and_initial_commit(runner, tmp_path: Path) -> None:
    repo = tmp_path / "knowledge"

    result = runner.invoke(app, ["init", str(repo)])

    assert result.exit_code == 0, result.stdout
    for dirname in ("services", "flows", "system", "adr", "entities", "glossary"):
        assert (repo / dirname).is_dir()
    assert (repo / ".akashic" / "cache").is_dir()
    assert (repo / ".akashic" / "logs").is_dir()
    assert (repo / ".akashic" / "config.yaml").exists()
    assert (repo / ".git").exists()
    assert _git(repo, "rev-parse", "--verify", "HEAD").returncode == 0


def test_init_registers_knowledge_base_in_global_config(
    runner, tmp_path: Path, monkeypatch
) -> None:
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    repo = tmp_path / "knowledge"

    result = runner.invoke(app, ["init", str(repo)])

    assert result.exit_code == 0, result.stdout
    global_config = load_global_config(home / ".akashic" / "config.yaml")
    assert global_config.knowledge_bases["knowledge"].path == str(repo.resolve())


def test_init_global_registry_is_idempotent_for_same_path(
    runner, tmp_path: Path, monkeypatch
) -> None:
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    repo = tmp_path / "knowledge"

    first = runner.invoke(app, ["init", str(repo)])
    second = runner.invoke(app, ["init", str(repo)])

    assert first.exit_code == 0, first.stdout
    assert second.exit_code == 0, second.stdout
    global_config = load_global_config(home / ".akashic" / "config.yaml")
    assert list(global_config.knowledge_bases) == ["knowledge"]
    assert global_config.knowledge_bases["knowledge"].path == str(repo.resolve())


def test_init_global_registry_suffixes_name_collisions(
    runner, tmp_path: Path, monkeypatch
) -> None:
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    first_repo = tmp_path / "first" / "knowledge"
    second_repo = tmp_path / "second" / "knowledge"

    first = runner.invoke(app, ["init", str(first_repo)])
    second = runner.invoke(app, ["init", str(second_repo)])
    repeated = runner.invoke(app, ["init", str(second_repo)])

    assert first.exit_code == 0, first.stdout
    assert second.exit_code == 0, second.stdout
    assert repeated.exit_code == 0, repeated.stdout
    global_config = load_global_config(home / ".akashic" / "config.yaml")
    assert global_config.knowledge_bases["knowledge"].path == str(first_repo.resolve())
    assert global_config.knowledge_bases["knowledge-2"].path == str(second_repo.resolve())
    assert list(global_config.knowledge_bases) == ["knowledge", "knowledge-2"]


def test_init_is_idempotent_and_preserves_content(runner, tmp_path: Path) -> None:
    repo = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(repo)])
    note = repo / "services" / "note.md"
    note.write_text("keep me", encoding="utf-8")

    result = runner.invoke(app, ["init", str(repo)])

    assert result.exit_code == 0, result.stdout
    assert note.read_text(encoding="utf-8") == "keep me"


def test_discovery_walks_up_from_nested_dir(runner, tmp_path: Path) -> None:
    repo = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(repo)])
    nested = repo / "services" / "nested"
    nested.mkdir()

    workspace = discover_workspace(cwd=nested)

    assert workspace.root == repo.resolve()


def test_knowledge_option_and_env_override_discovery(runner, tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(repo)])

    by_arg = runner.invoke(app, ["--knowledge", str(repo), "root"])
    assert by_arg.exit_code == 0, by_arg.stdout
    assert Path(by_arg.stdout.strip()) == repo.resolve()

    monkeypatch.setenv("AKASHIC_HOME", str(repo))
    by_env = runner.invoke(app, ["root"])
    assert by_env.exit_code == 0, by_env.stdout
    assert Path(by_env.stdout.strip()) == repo.resolve()


def test_missing_workspace_has_clear_error(tmp_path: Path) -> None:
    try:
        discover_workspace(cwd=tmp_path, env={})
    except WorkspaceNotFoundError as exc:
        assert "Run 'akashic init' first" in str(exc)
    else:
        raise AssertionError("expected WorkspaceNotFoundError")


def test_config_loads_and_gitignore_contains_akashic_ignores(runner, tmp_path: Path) -> None:
    repo = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(repo)])

    config = load_config(repo / ".akashic" / "config.yaml")
    assert config.version == 1
    assert config.knowledge.path == "."
    assert config.repositories == []

    gitignore = (repo / ".gitignore").read_text(encoding="utf-8")
    assert ".akashic/cache/" in gitignore
    assert ".akashic/logs/" in gitignore
    assert ".akashic/config.local.yaml" in gitignore


def test_invalid_config_reports_clear_validation_error(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("version: wrong\nunknown: true\n", encoding="utf-8")

    try:
        load_config(config_path)
    except ValueError as exc:
        message = str(exc)
        assert "Invalid Akashic config" in message
        assert "version" in message
    else:
        raise AssertionError("expected config validation error")


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=env)
