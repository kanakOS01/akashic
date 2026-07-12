from __future__ import annotations

import subprocess
from pathlib import Path

from akashic.engine.agent import (
    AgentContext,
    AgentUnavailableError,
    ClaudeProvider,
    CodexProvider,
    FakeProvider,
)
from akashic.engine.config import AgentConfig


def test_claude_provider_constructs_seeded_session_invocation(tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    api = tmp_path / "api"
    web = tmp_path / "web"
    knowledge.mkdir()
    api.mkdir()
    web.mkdir()
    context = AgentContext(
        prompt="MASTER PROMPT",
        knowledge_root=knowledge,
        source_repositories={"api": api, "web": web},
    )

    invocation = ClaudeProvider().build_invocation(context)

    assert invocation.command == [
        "claude",
        "MASTER PROMPT",
        "--add-dir",
        str(api),
        "--add-dir",
        str(web),
    ]
    assert invocation.cwd == knowledge
    assert invocation.readable_roots == (api, web)
    assert invocation.writable_roots == (knowledge,)


def test_codex_provider_constructs_seeded_session_invocation(tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    api = tmp_path / "api"
    knowledge.mkdir()
    api.mkdir()
    context = AgentContext(
        prompt="MASTER PROMPT",
        knowledge_root=knowledge,
        source_repositories={"api": api},
    )

    invocation = CodexProvider().build_invocation(context)

    assert invocation.command == ["codex", "MASTER PROMPT"]
    assert invocation.cwd == knowledge
    assert invocation.readable_roots == (api,)
    assert invocation.writable_roots == (knowledge,)


def test_availability_respects_command_override_and_which(monkeypatch) -> None:
    seen: list[str] = []

    def fake_which(binary: str) -> str | None:
        seen.append(binary)
        if binary == "/custom/codex":
            return binary
        return None

    monkeypatch.setattr("akashic.engine.agent.shutil.which", fake_which)

    assert CodexProvider(AgentConfig(command="/custom/codex")).is_available() is True
    assert ClaudeProvider().is_available() is False
    assert seen == ["/custom/codex", "claude"]


def test_version_runs_configured_binary(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command, capture_output, text, check):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="codex 1.2.3\n", stderr="")

    monkeypatch.setattr("akashic.engine.agent.subprocess.run", fake_run)

    version = CodexProvider(AgentConfig(command="/custom/codex")).version()

    assert version == "codex 1.2.3"
    assert calls == [["/custom/codex", "--version"]]


def test_claude_provider_generate_hands_tty_to_child_and_reports_exit_code(
    monkeypatch, tmp_path: Path
) -> None:
    knowledge = tmp_path / "knowledge"
    api = tmp_path / "api"
    knowledge.mkdir()
    api.mkdir()
    context = AgentContext(
        prompt="MASTER PROMPT",
        knowledge_root=knowledge,
        source_repositories={"api": api},
    )
    calls: list[dict] = []

    def fake_run(command, cwd):
        calls.append({"command": command, "cwd": cwd})
        return subprocess.CompletedProcess(command, 3)

    monkeypatch.setattr("akashic.engine.agent.shutil.which", lambda binary: binary)
    monkeypatch.setattr("akashic.engine.agent.subprocess.run", fake_run)

    result = ClaudeProvider().generate(context)

    assert calls == [
        {"command": ["claude", "MASTER PROMPT", "--add-dir", str(api)], "cwd": knowledge}
    ]
    assert result.exit_code == 3
    assert result.invocation is not None


def test_provider_generate_raises_when_binary_missing(monkeypatch, tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    context = AgentContext(prompt="MASTER PROMPT", knowledge_root=knowledge)

    monkeypatch.setattr("akashic.engine.agent.shutil.which", lambda binary: None)

    try:
        CodexProvider().generate(context)
    except AgentUnavailableError as exc:
        assert "codex" in str(exc)
    else:
        raise AssertionError("expected AgentUnavailableError")


def test_fake_provider_records_prompt_and_writes_file(tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    provider = FakeProvider(version_text="fake 1.0")
    context = AgentContext(prompt="COMPOSED PROMPT", knowledge_root=knowledge)

    result = provider.generate(context)

    assert provider.is_available() is True
    assert provider.version() == "fake 1.0"
    assert provider.contexts == [context]
    assert provider.prompts == ["COMPOSED PROMPT"]
    assert len(result.written_files) == 1
    assert result.written_files[0].read_text(encoding="utf-8").endswith("COMPOSED PROMPT\n")
