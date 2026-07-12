from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from akashic.engine.config import load_local_config
from akashic.engine.workspace import Workspace


@dataclass(frozen=True)
class StatusResult:
    repositories: list[tuple[str, str | None]]
    last_generation: dict[str, any] | None
    pending_changes: list[str]
    document_counts: dict[str, int]


def get_status(workspace: Workspace) -> StatusResult:
    local_path = workspace.root / ".akashic" / "config.local.yaml"
    local_config = load_local_config(local_path)
    repos = []
    for r in sorted(workspace.config.repositories, key=lambda item: item.name):
        path = local_config.repositories.get(r.name)
        repos.append((r.name, path))

    state_path = workspace.root / ".akashic" / "cache" / "state.json"
    last_gen = None
    if state_path.exists():
        try:
            last_gen = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    res = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=workspace.root,
        capture_output=True,
        text=True,
    )
    pending = [line for line in res.stdout.splitlines() if line.strip()] if res.returncode == 0 else []

    counts = {}
    for section in ("services", "flows", "system", "adr", "entities", "glossary"):
        dir_path = workspace.root / section
        if dir_path.exists() and dir_path.is_dir():
            counts[section] = len(list(dir_path.rglob("*.md")))
        else:
            counts[section] = 0

    return StatusResult(
        repositories=repos,
        last_generation=last_gen,
        pending_changes=pending,
        document_counts=counts,
    )
