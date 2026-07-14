from __future__ import annotations

import importlib.resources
from dataclasses import dataclass
from pathlib import Path

from akashic.engine.registry import (
    global_akashic_dir,
    register_knowledge_base,
    registry_path,
)
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


def _skill_markdown(home: Path | None = None) -> str:
    base_text = _static_skill_markdown().rstrip()
    global_dir = global_akashic_dir(home=home)
    registry = registry_path(home=home)

    return (
        _inject_runtime_discovery_section(
            base_text,
            "## Runtime knowledge base selection\n\n"
            "Before answering any Akashic question or describing any repository, you must\n"
            "discover the user's knowledge bases and let the user choose one.\n\n"
            f"Global Akashic folder: `{global_dir}`\n"
            f"Machine-level registry: `{registry}`\n\n"
            "Each knowledge base reference is the absolute path to that knowledge base.\n"
            "Every time this skill is invoked, discover knowledge bases before answering.\n"
            "Your first user-visible response must be the discovered reference list or a\n"
            "question asking the user to choose from that list.\n\n"
            "Discovery steps:\n\n"
            "1. Read the registry if it exists.\n"
            "2. Scan the global folder for child directories that contain `.akashic/config.yaml`.\n"
            "3. Keep only paths that exist and contain `.akashic/config.yaml`.\n"
            "4. Show the combined list of reference paths to the user, with display names.\n"
            "5. If more than one reference exists and the user has not already provided one,\n"
            "   ask the user which knowledge base path to use.\n"
            "6. Use only the selected reference path as the knowledge repo root before reading docs.\n\n"
            "Do not use an install-time snapshot. The list must come from the current\n"
            "registry and global folder contents at runtime.\n"
            "Do not infer the knowledge base from the current working directory or current\n"
            "source code repository. Do not describe the folder structure or answer from a\n"
            "knowledge repo until the user has selected a reference path.\n"
        )
    )


def _inject_runtime_discovery_section(base_text: str, section: str) -> str:
    if "---\n\n" not in base_text:
        return f"{section}\n\n{base_text}"
    frontmatter, body = base_text.split("---\n\n", 1)
    return (
        f"{frontmatter}---\n\n"
        f"{section}\n\n"
        f"{body}"
    )


def default_target(workspace: Workspace) -> str | None:
    provider = workspace.config.agent.provider
    return provider if provider in _TARGET_DIRS else None


def install_skill(workspace: Workspace, target: str, home: Path | None = None) -> SkillInstallResult:
    if target not in _TARGET_DIRS:
        raise UnknownSkillTargetError(
            f"Unknown skill target '{target}'. Expected one of: {', '.join(sorted(_TARGET_DIRS))}."
        )

    register_knowledge_base(workspace.root, home=home)
    skill_dir = (home or Path.home()) / _TARGET_DIRS[target]
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(_skill_markdown(home=home), encoding="utf-8")
    return SkillInstallResult(target=target, skill_path=skill_path)
