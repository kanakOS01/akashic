from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from akashic.cli import app
from akashic.engine.agent import AgentContext, AgentResult, FakeProvider
from akashic.engine.config import load_config, load_local_config, write_config, write_local_config
from akashic.engine.generate import GenerateError, run_generate
from akashic.engine.workspace import discover_workspace


def test_generate_cli_uses_fake_provider_and_leaves_changes_unstaged(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = _init_source_repo(tmp_path / "source")
    _attach(runner, knowledge, source)
    _set_provider(knowledge, "fake")

    result = runner.invoke(app, ["--knowledge", str(knowledge), "generate"])

    assert result.exit_code == 0, result.stdout
    assert "Changed files:" in result.stdout
    assert "- system/fake-provider.md" in result.stdout
    generated = knowledge / "system" / "fake-provider.md"
    assert "source: " in generated.read_text(encoding="utf-8")
    assert _git(knowledge, "diff", "--cached", "--name-only").stdout == ""
    assert "system/fake-provider.md" in _git(
        knowledge, "status", "--short", "--untracked-files=all"
    ).stdout

    state = json.loads((knowledge / ".akashic" / "cache" / "state.json").read_text(encoding="utf-8"))
    assert state["provider"] == "fake"
    assert state["repos"] == ["source"]
    assert "timestamp" in state
    assert isinstance(state["duration"], float)


def test_generate_records_prompt_with_injected_fake_provider(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = _init_source_repo(tmp_path / "source")
    _attach(runner, knowledge, source)
    workspace = discover_workspace(knowledge=knowledge)
    provider = FakeProvider()

    result = run_generate(workspace, provider=provider)

    assert result.success is True
    assert provider.prompts == [result.prompt]
    assert "### Service Document Template" in provider.prompts[0]
    assert "source: " in provider.prompts[0]


def test_generate_warns_and_skips_missing_paths_but_keeps_valid_repos(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    valid = _init_source_repo(tmp_path / "valid")
    missing = _init_source_repo(tmp_path / "missing")
    _attach(runner, knowledge, valid)
    _attach(runner, knowledge, missing)
    local_path = knowledge / ".akashic" / "config.local.yaml"
    local = load_local_config(local_path)
    local.repositories["missing"] = str(tmp_path / "does-not-exist")
    write_local_config(local_path, local)
    workspace = discover_workspace(knowledge=knowledge)
    provider = FakeProvider()

    result = run_generate(workspace, provider=provider)

    assert result.repos == ("valid",)
    assert any("Skipping missing" in warning for warning in result.warnings)
    assert "valid: " in provider.prompts[0]
    assert "missing: " not in provider.prompts[0]


def test_generate_aborts_when_no_valid_repos_remain(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = _init_source_repo(tmp_path / "source")
    _attach(runner, knowledge, source)
    (knowledge / ".akashic" / "config.local.yaml").unlink()
    workspace = discover_workspace(knowledge=knowledge)

    try:
        run_generate(workspace, provider=FakeProvider())
    except GenerateError as exc:
        assert "No valid attached repositories" in str(exc)
    else:
        raise AssertionError("expected GenerateError")


def test_generate_warns_on_clean_exit_with_no_changes(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    source = _init_source_repo(tmp_path / "source")
    _attach(runner, knowledge, source)
    workspace = discover_workspace(knowledge=knowledge)

    result = run_generate(workspace, provider=NoChangeProvider())

    assert result.success is False
    assert result.changed_files == ()
    assert "produced no knowledge changes" in result.warnings[-1]
    assert (knowledge / ".akashic" / "cache" / "state.json").exists()


class NoChangeProvider:
    def generate(self, context: AgentContext) -> AgentResult:
        return AgentResult(invocation=None, exit_code=0)

    def is_available(self) -> bool:
        return True

    def version(self) -> str:
        return "no-change 0.0"


def _init_knowledge(runner, tmp_path: Path) -> Path:
    knowledge = tmp_path / "knowledge"
    result = runner.invoke(app, ["init", str(knowledge)])
    assert result.exit_code == 0, result.stdout
    return knowledge


def _attach(runner, knowledge: Path, source: Path) -> None:
    result = runner.invoke(app, ["--knowledge", str(knowledge), "attach", str(source)])
    assert result.exit_code == 0, result.stdout


def _set_provider(knowledge: Path, provider: str) -> None:
    config_path = knowledge / ".akashic" / "config.yaml"
    config = load_config(config_path)
    config.agent.provider = provider
    write_config(config_path, config)


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
