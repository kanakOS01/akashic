from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from akashic.engine.agent import AgentContext, AgentProvider, provider_from_config
from akashic.engine.config import AkashicLocalConfig, load_local_config
from akashic.engine.prompt_builder import build_master_prompt, load_workspace_prompt_templates
from akashic.engine.workspace import Workspace


class GenerateError(RuntimeError):
    pass


@dataclass(frozen=True)
class GenerateResult:
    changed_files: tuple[Path, ...]
    warnings: tuple[str, ...] = ()
    state_path: Path | None = None
    success: bool = False
    prompt: str = ""
    repos: tuple[str, ...] = ()


def run_generate(workspace: Workspace, provider: AgentProvider | None = None) -> GenerateResult:
    started = time.monotonic()
    warnings: list[str] = []
    local_config_path = workspace.root / ".akashic" / "config.local.yaml"
    local_config = load_local_config(local_config_path)
    valid_repos: dict[str, Path] = {}

    for repository in sorted(workspace.config.repositories, key=lambda item: item.name):
        raw_path = local_config.repositories.get(repository.name)
        if not raw_path:
            warnings.append(f"Skipping {repository.name}: missing local path.")
            continue
        path = Path(raw_path)
        if not path.exists():
            warnings.append(f"Skipping {repository.name}: local path does not exist: {path}.")
            continue
        valid_repos[repository.name] = path

    if not valid_repos:
        raise GenerateError("No valid attached repositories found.")

    prompt_config = workspace.config.model_copy(
        update={
            "repositories": [
                repository
                for repository in workspace.config.repositories
                if repository.name in valid_repos
            ]
        }
    )
    prompt_local_config = AkashicLocalConfig(
        repositories={name: str(path) for name, path in valid_repos.items()}
    )
    prompt = build_master_prompt(
        prompt_config,
        prompt_local_config,
        load_workspace_prompt_templates(workspace.root),
    )
    provider = provider or provider_from_config(workspace.config.agent)
    provider_name = workspace.config.agent.provider
    context = AgentContext(
        prompt=prompt,
        knowledge_root=workspace.root,
        source_repositories=valid_repos,
    )

    agent_result = provider.generate(context)
    changed_files = _changed_files(workspace.root)
    success = agent_result.exit_code == 0 and bool(changed_files)
    if agent_result.exit_code == 0 and not changed_files:
        warnings.append("Agent exited cleanly but produced no knowledge changes.")

    state_path = _write_state(
        workspace.root,
        provider_name=provider_name,
        repos=tuple(valid_repos),
        duration_seconds=time.monotonic() - started,
    )
    return GenerateResult(
        changed_files=changed_files,
        warnings=tuple(warnings),
        state_path=state_path,
        success=success,
        prompt=prompt,
        repos=tuple(valid_repos),
    )


def _changed_files(root: Path) -> tuple[Path, ...]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    files: list[Path] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        raw_path = line[3:]
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1]
        path = Path(raw_path)
        if path.parts and path.parts[0] != ".akashic":
            files.append(path)
    return tuple(sorted(files))


def _write_state(
    root: Path,
    provider_name: str,
    repos: tuple[str, ...],
    duration_seconds: float,
) -> Path:
    cache_dir = root / ".akashic" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    state_path = cache_dir / "state.json"
    state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider_name,
        "repos": list(repos),
        "duration": duration_seconds,
    }
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state_path
