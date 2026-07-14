from __future__ import annotations

import os
import subprocess
from pathlib import Path

from akashic.cli import app
from akashic.engine.config import load_config, load_local_config


def test_attach_path_registers_git_repo_with_default_name(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = _init_source_repo(tmp_path / "source")

    result = runner.invoke(app, ["--knowledge", str(knowledge), "attach", str(source)])

    assert result.exit_code == 0, result.stdout
    assert "Attached source" in result.stdout
    config = load_config(knowledge / ".akashic" / "config.yaml")
    local = load_local_config(knowledge / ".akashic" / "config.local.yaml")
    assert [repo.name for repo in config.repositories] == ["source"]
    assert local.repositories == {"source": str(source.resolve())}


def test_attach_without_path_registers_cwd(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = _init_source_repo(tmp_path / "current")
    monkeypatch.chdir(source)

    result = runner.invoke(app, ["--knowledge", str(knowledge), "attach"])

    assert result.exit_code == 0, result.stdout
    local = load_local_config(knowledge / ".akashic" / "config.local.yaml")
    assert local.repositories == {"current": str(source.resolve())}


def test_attach_rejects_non_git_target(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = tmp_path / "plain"
    source.mkdir()

    result = runner.invoke(app, ["--knowledge", str(knowledge), "attach", str(source)])

    assert result.exit_code != 0
    assert "not a Git repository" in _combined_output(result)


def test_attach_name_override_dedupe_and_name_collision(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = _init_source_repo(tmp_path / "source")
    other = _init_source_repo(tmp_path / "other")

    first = runner.invoke(app, ["--knowledge", str(knowledge), "attach", str(source), "--name", "docs"])
    second = runner.invoke(app, ["--knowledge", str(knowledge), "attach", str(source), "--name", "docs-renamed"])
    collision = runner.invoke(app, ["--knowledge", str(knowledge), "attach", str(other), "--name", "docs-renamed"])

    assert first.exit_code == 0, first.stdout
    assert second.exit_code == 0, second.stdout
    assert collision.exit_code != 0
    assert "already attached" in _combined_output(collision)
    config = load_config(knowledge / ".akashic" / "config.yaml")
    local = load_local_config(knowledge / ".akashic" / "config.local.yaml")
    assert [repo.name for repo in config.repositories] == ["docs-renamed"]
    assert local.repositories == {"docs-renamed": str(source.resolve())}


def test_detach_removes_configs_and_deletes_no_files(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = _init_source_repo(tmp_path / "source")
    generated = knowledge / "services" / "source.md"
    generated.write_text("generated", encoding="utf-8")
    runner.invoke(app, ["--knowledge", str(knowledge), "attach", str(source)])

    result = runner.invoke(app, ["--knowledge", str(knowledge), "detach", "source"])

    assert result.exit_code == 0, result.stdout
    assert "Generated docs remain" in result.stdout
    assert generated.exists()
    config = load_config(knowledge / ".akashic" / "config.yaml")
    local = load_local_config(knowledge / ".akashic" / "config.local.yaml")
    assert config.repositories == []
    assert local.repositories == {}


def test_list_marks_missing_local_path(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = _init_source_repo(tmp_path / "source")
    runner.invoke(app, ["--knowledge", str(knowledge), "attach", str(source)])
    (knowledge / ".akashic" / "config.local.yaml").unlink()

    result = runner.invoke(app, ["--knowledge", str(knowledge), "list"])

    assert result.exit_code == 0, result.stdout
    assert "source" in result.stdout
    assert "[missing local path]" in result.stdout


def test_attach_does_not_modify_source_repo(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = _init_source_repo(tmp_path / "source")
    before = _git(source, "status", "--short").stdout

    result = runner.invoke(app, ["--knowledge", str(knowledge), "attach", str(source)])

    assert result.exit_code == 0, result.stdout
    assert _git(source, "status", "--short").stdout == before


def _init_knowledge(runner, tmp_path: Path) -> Path:
    knowledge = tmp_path / "knowledge"
    result = runner.invoke(app, ["init", str(knowledge)])
    assert result.exit_code == 0, result.stdout
    return knowledge


def _init_source_repo(path: Path) -> Path:
    path.mkdir()
    readme = path / "README.md"
    readme.write_text("source\n", encoding="utf-8")
    _git(path, "init", check=True)
    _git(path, "add", "README.md", check=True)
    _git(
        path,
        "-c",
        "user.name=Source",
        "-c",
        "user.email=source@example.invalid",
        "commit",
        "-m",
        "Initial source",
        check=True,
    )
    return path


def _git(cwd: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
        check=check,
    )


def _combined_output(result) -> str:
    return result.output
