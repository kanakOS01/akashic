from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from akashic.engine.config import AgentConfig


@dataclass(frozen=True)
class AgentContext:
    prompt: str
    knowledge_root: Path
    source_repositories: dict[str, Path] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentInvocation:
    command: list[str]
    cwd: Path
    readable_roots: tuple[Path, ...] = ()
    writable_roots: tuple[Path, ...] = ()


@dataclass(frozen=True)
class AgentResult:
    invocation: AgentInvocation | None
    exit_code: int = 0
    written_files: tuple[Path, ...] = ()


class AgentProvider(Protocol):
    def generate(self, context: AgentContext) -> AgentResult:
        ...

    def is_available(self) -> bool:
        ...

    def version(self) -> str:
        ...


class AgentUnavailableError(RuntimeError):
    pass


class CommandAgentProvider:
    default_command: str

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()

    @property
    def binary(self) -> str:
        return self.config.command or self.default_command

    def is_available(self) -> bool:
        return shutil.which(self.binary) is not None

    def version(self) -> str:
        result = subprocess.run(
            [self.binary, "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        return (result.stdout or result.stderr).strip()

    def run_invocation(self, invocation: AgentInvocation) -> AgentResult:
        """Hand the TTY to the agent CLI and wait for the interactive session to exit."""
        if not self.is_available():
            raise AgentUnavailableError(
                f"Agent binary '{self.binary}' not found on PATH."
            )
        completed = subprocess.run(invocation.command, cwd=invocation.cwd)
        return AgentResult(invocation=invocation, exit_code=completed.returncode)


class ClaudeProvider(CommandAgentProvider):
    default_command = "claude"

    def generate(self, context: AgentContext) -> AgentResult:
        return self.run_invocation(self.build_invocation(context))

    def build_invocation(self, context: AgentContext) -> AgentInvocation:
        command = [self.binary, context.prompt]
        for repo in context.source_repositories.values():
            command.extend(["--add-dir", str(repo)])
        return AgentInvocation(
            command=command,
            cwd=context.knowledge_root,
            readable_roots=tuple(context.source_repositories.values()),
            writable_roots=(context.knowledge_root,),
        )


class CodexProvider(CommandAgentProvider):
    default_command = "codex"

    def generate(self, context: AgentContext) -> AgentResult:
        return self.run_invocation(self.build_invocation(context))

    def build_invocation(self, context: AgentContext) -> AgentInvocation:
        return AgentInvocation(
            command=[self.binary, context.prompt],
            cwd=context.knowledge_root,
            readable_roots=tuple(context.source_repositories.values()),
            writable_roots=(context.knowledge_root,),
        )


class FakeProvider:
    def __init__(self, available: bool = True, version_text: str = "fake-agent 0.0.0") -> None:
        self.available = available
        self.version_text = version_text
        self.contexts: list[AgentContext] = []
        self.prompts: list[str] = []

    def generate(self, context: AgentContext) -> AgentResult:
        self.contexts.append(context)
        self.prompts.append(context.prompt)
        output = context.knowledge_root / "system" / "fake-provider.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            "---\n"
            "title: Fake Provider Output\n"
            "type: system\n"
            "source_repositories: []\n"
            "generated_at: fake\n"
            "akashic_version: test\n"
            "---\n\n"
            f"{context.prompt}\n",
            encoding="utf-8",
        )
        return AgentResult(invocation=None, written_files=(output,))

    def is_available(self) -> bool:
        return self.available

    def version(self) -> str:
        return self.version_text


def provider_from_config(config: AgentConfig) -> AgentProvider:
    if config.provider == "claude":
        return ClaudeProvider(config)
    if config.provider == "codex":
        return CodexProvider(config)
    if config.provider == "fake":
        return FakeProvider()
    raise ValueError(f"Unknown agent provider '{config.provider}'.")
