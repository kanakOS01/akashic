from __future__ import annotations

import os
from pathlib import Path
import pytest

from akashic.cli import app
from akashic.engine.workspace import discover_workspace
from akashic.engine.doctor import diagnose


def test_doctor_success_flow(runner, tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    from akashic.engine.config import load_config, write_config
    config_path = knowledge / ".akashic" / "config.yaml"
    config = load_config(config_path)
    config.agent.provider = "fake"
    write_config(config_path, config)

    result = runner.invoke(app, ["--knowledge", str(knowledge), "doctor"])

    assert result.exit_code == 0, result.stdout + (result.stderr or "")
    output = result.stdout + (result.stderr or "")
    assert "Checking configuration... Pass" in output
    assert "Checking Git presence... Pass" in output
    assert "Checking attached repositories... Pass" in output
    assert "Checking agent provider... Pass" in output
    assert "Checking writability... Pass" in output


def test_doctor_config_invalid(runner, tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    # Break config
    config_file = knowledge / ".akashic" / "config.yaml"
    config_file.write_text("invalid yaml: [:::", encoding="utf-8")

    result = runner.invoke(app, ["--knowledge", str(knowledge), "doctor"])
    assert result.exit_code != 0
    output = result.stdout + (result.stderr or "")
    assert "Invalid Akashic config" in output


def test_doctor_local_config_invalid(runner, tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    # Break local config
    local_file = knowledge / ".akashic" / "config.local.yaml"
    local_file.write_text("invalid local: [:::", encoding="utf-8")

    workspace = discover_workspace(knowledge=knowledge)
    from akashic.engine.doctor import check_config
    res = check_config(workspace)
    assert not res.passed
    assert "Local config invalid" in res.message


def test_doctor_git_missing(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    monkeypatch.setattr("akashic.engine.doctor.shutil.which", lambda x: None)

    workspace = discover_workspace(knowledge=knowledge)
    from akashic.engine.doctor import check_git
    res = check_git()
    assert not res.passed
    assert "Git executable not found on PATH" in res.message


def test_doctor_repo_validation_failures(runner, tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    # Attach non-existent and non-git repos in config
    config_file = knowledge / ".akashic" / "config.yaml"
    config_file.write_text(
        "version: 1\n"
        "repositories:\n"
        "  - name: missing\n"
        "  - name: non_existent\n"
        "  - name: non_git\n",
        encoding="utf-8"
    )

    # config.local.yaml
    non_git_path = tmp_path / "non_git"
    non_git_path.mkdir()
    local_file = knowledge / ".akashic" / "config.local.yaml"
    local_file.write_text(
        f"repositories:\n"
        f"  non_existent: {tmp_path}/does_not_exist\n"
        f"  non_git: {non_git_path}\n",
        encoding="utf-8"
    )

    workspace = discover_workspace(knowledge=knowledge)
    from akashic.engine.doctor import check_repositories
    res = check_repositories(workspace)
    assert not res.passed
    assert "missing': missing local path mapping" in "".join(res.details)
    assert "non_existent': local path does not exist" in "".join(res.details)
    assert "non_git': local path is not a Git repository" in "".join(res.details)


def test_doctor_agent_missing(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    # Set unknown/missing agent
    config_file = knowledge / ".akashic" / "config.yaml"
    config_file.write_text(
        "version: 1\n"
        "agent:\n"
        "  provider: claude\n"
        "  command: missing-claude-bin\n",
        encoding="utf-8"
    )

    workspace = discover_workspace(knowledge=knowledge)
    from akashic.engine.doctor import check_agent
    res = check_agent(workspace)
    assert not res.passed
    assert "not installed" in res.message


def test_doctor_writability_fails(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    # Mock os.access to return False for writability
    monkeypatch.setattr("akashic.engine.doctor.os.access", lambda path, mode: False)

    workspace = discover_workspace(knowledge=knowledge)
    from akashic.engine.doctor import check_writability
    res = check_writability(workspace)
    assert not res.passed
    assert "not writable" in res.message
