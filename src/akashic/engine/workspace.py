from __future__ import annotations

import os
from typing import Any
from dataclasses import dataclass
from pathlib import Path

from akashic.engine.config import AkashicConfig, load_config


class WorkspaceNotFoundError(RuntimeError):
    pass


@dataclass(frozen=True)
class Workspace:
    root: Path
    config_path: Path
    config: AkashicConfig


def discover_workspace(
    cwd: Path | None = None,
    knowledge: Path | None = None,
    env: dict[str, str] | None | Any = None,
) -> Workspace:
    if env is None:
        env = os.environ

    if knowledge is not None:
        return _workspace_from_root(knowledge)

    home = env.get("AKASHIC_HOME")
    if home:
        return _workspace_from_root(Path(home))

    start = (cwd or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        config_path = candidate / ".akashic" / "config.yaml"
        if config_path.exists():
            return Workspace(candidate, config_path, load_config(config_path))

    raise WorkspaceNotFoundError(
        f"No Akashic knowledge repo found from {start}. Run 'akashic init' first or pass --knowledge."
    )


def _workspace_from_root(root: Path) -> Workspace:
    root = root.resolve()
    config_path = root / ".akashic" / "config.yaml"
    if not config_path.exists():
        raise WorkspaceNotFoundError(f"No Akashic config found at {config_path}.")
    return Workspace(root, config_path, load_config(config_path))

