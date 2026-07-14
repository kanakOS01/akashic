from __future__ import annotations

import importlib.resources
from dataclasses import dataclass
from pathlib import Path

from akashic.engine.workspace import Workspace

# Install location for each supported target, relative to the user's home directory.
_TARGET_DIRS = {
    "claude": Path(".claude") / "skills" / "akashic",
    "codex": Path(".codex") / "skills" / "akashic",
}


class UnknownSkillTargetError(ValueError):
    pass


@dataclass(frozen=True)
class SkillInstallResult:
    target: str
    skill_path: Path


def _static_skill_markdown() -> str:
    return (
        importlib.resources.files("akashic.skills.akashic")
        .joinpath("SKILL.md")
        .read_text(encoding="utf-8")
    )


def default_target(workspace: Workspace) -> str | None:
    provider = workspace.config.agent.provider
    return provider if provider in _TARGET_DIRS else None


def install_skill(workspace: Workspace, target: str, home: Path | None = None) -> SkillInstallResult:
    if target not in _TARGET_DIRS:
        raise UnknownSkillTargetError(
            f"Unknown skill target '{target}'. Expected one of: {', '.join(sorted(_TARGET_DIRS))}."
        )

    skill_dir = (home or Path.home()) / _TARGET_DIRS[target]
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(_static_skill_markdown(), encoding="utf-8")
    return SkillInstallResult(target=target, skill_path=skill_path)
