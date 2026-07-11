from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from akashic.engine.config import (
    AkashicConfig,
    AkashicLocalConfig,
    RepositoryConfig,
    load_local_config,
    write_config,
    write_local_config,
)
from akashic.engine.workspace import Workspace


class RepositoryError(RuntimeError):
    pass


@dataclass(frozen=True)
class ListedRepository:
    name: str
    path: Path | None
    missing_local_path: bool
    missing_target: bool


def attach_repository(workspace: Workspace, target: Path, name: str | None = None) -> RepositoryConfig:
    resolved = target.resolve()
    if not _is_git_repository(resolved):
        raise RepositoryError(f"{resolved} is not a Git repository.")

    repo_name = name or resolved.name
    config = workspace.config
    local_path = _local_config_path(workspace)
    local_config = load_local_config(local_path)

    path_matches = [
        existing_name
        for existing_name, existing_path in local_config.repositories.items()
        if Path(existing_path).resolve() == resolved
    ]
    existing_for_path = path_matches[0] if path_matches else None

    for repo in config.repositories:
        if repo.name == repo_name and repo.name != existing_for_path:
            raise RepositoryError(f"Repository name '{repo_name}' is already attached.")

    repositories = [repo for repo in config.repositories if repo.name != existing_for_path and repo.name != repo_name]
    repository = RepositoryConfig(name=repo_name)
    repositories.append(repository)
    config.repositories = sorted(repositories, key=lambda repo: repo.name)

    if existing_for_path and existing_for_path != repo_name:
        local_config.repositories.pop(existing_for_path, None)
    local_config.repositories[repo_name] = str(resolved)

    _write_configs(workspace, config, local_path, local_config)
    return repository


def detach_repository(workspace: Workspace, name: str) -> bool:
    config = workspace.config
    local_path = _local_config_path(workspace)
    local_config = load_local_config(local_path)

    before = len(config.repositories)
    config.repositories = [repo for repo in config.repositories if repo.name != name]
    local_removed = local_config.repositories.pop(name, None) is not None
    removed = len(config.repositories) != before or local_removed

    if removed:
        _write_configs(workspace, config, local_path, local_config)
    return removed


def list_repositories(workspace: Workspace) -> list[ListedRepository]:
    local_config = load_local_config(_local_config_path(workspace))
    rows: list[ListedRepository] = []
    for repo in sorted(workspace.config.repositories, key=lambda item: item.name):
        raw_path = local_config.repositories.get(repo.name)
        path = Path(raw_path) if raw_path else None
        rows.append(
            ListedRepository(
                name=repo.name,
                path=path,
                missing_local_path=path is None,
                missing_target=path is not None and not path.exists(),
            )
        )
    return rows


def _local_config_path(workspace: Workspace) -> Path:
    return workspace.root / ".akashic" / "config.local.yaml"


def _write_configs(
    workspace: Workspace,
    config: AkashicConfig,
    local_path: Path,
    local_config: AkashicLocalConfig,
) -> None:
    write_config(workspace.config_path, config)
    write_local_config(local_path, local_config)


def _is_git_repository(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"
