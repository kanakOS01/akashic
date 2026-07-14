from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from akashic.engine.agent import provider_from_config
from akashic.engine.config import load_config, load_local_config
from akashic.engine.workspace import Workspace


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    message: str
    details: list[str] = field(default_factory=list)


def check_config(workspace: Workspace) -> CheckResult:
    try:
        load_config(workspace.config_path)
    except Exception as exc:
        return CheckResult("Configuration Schema", False, f"Committed config invalid: {exc}")

    local_path = workspace.root / ".akashic" / "config.local.yaml"
    if local_path.exists():
        try:
            load_local_config(local_path)
        except Exception as exc:
            return CheckResult("Configuration Schema", False, f"Local config invalid: {exc}")
    return CheckResult("Configuration Schema", True, "Configuration schema is valid.")


def check_git() -> CheckResult:
    git_path = shutil.which("git")
    if not git_path:
        return CheckResult("Git Presence", False, "Git executable not found on PATH.")
    try:
        res = subprocess.run(["git", "--version"], capture_output=True, text=True)
        version = res.stdout.strip() if res.returncode == 0 else "unknown version"
        return CheckResult("Git Presence", True, f"Git is installed ({version}).")
    except Exception as exc:
        return CheckResult("Git Presence", False, f"Failed to check Git version: {exc}")


def _is_git_repository(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def check_repositories(workspace: Workspace) -> CheckResult:
    local_path = workspace.root / ".akashic" / "config.local.yaml"
    try:
        local_config = load_local_config(local_path)
    except Exception:
        return CheckResult("Attached Repositories", False, "Cannot verify repositories due to local config load failure.")

    details: list[str] = []
    failed = False

    if not workspace.config.repositories:
        return CheckResult("Attached Repositories", True, "No repositories attached.")

    for repo in workspace.config.repositories:
        raw_path = local_config.repositories.get(repo.name)
        if not raw_path:
            failed = True
            details.append(f"'{repo.name}': missing local path mapping in config.local.yaml.")
            continue
        path = Path(raw_path)
        if not path.exists():
            failed = True
            details.append(f"'{repo.name}': local path does not exist: {path}.")
            continue

        if not _is_git_repository(path):
            failed = True
            details.append(f"'{repo.name}': local path is not a Git repository: {path}.")
            continue
        details.append(f"'{repo.name}': local path is valid Git repository ({path}).")

    if failed:
        return CheckResult("Attached Repositories", False, "One or more attached repositories are invalid.", details)
    return CheckResult("Attached Repositories", True, "All attached repositories are valid.", details)


def check_agent(workspace: Workspace) -> CheckResult:
    try:
        provider = provider_from_config(workspace.config.agent)
    except Exception as exc:
        return CheckResult("Agent Provider", False, f"Invalid agent configuration: {exc}")

    if not provider.is_available():
        name = workspace.config.agent.provider
        cmd = workspace.config.agent.command or name
        return CheckResult("Agent Provider", False, f"Agent '{name}' is not installed (command '{cmd}' not found on PATH).")

    try:
        ver = provider.version()
        return CheckResult("Agent Provider", True, f"Agent '{workspace.config.agent.provider}' is installed (version: {ver}).")
    except Exception as exc:
        return CheckResult("Agent Provider", False, f"Failed to get agent version: {exc}")


def check_node() -> CheckResult:
    node_path = shutil.which("node")
    if not node_path:
        return CheckResult("Node Runtime", False, "Node.js executable not found on PATH. Required for akashic serve/build-site.")
    npm_path = shutil.which("npm")
    if not npm_path:
        return CheckResult("Node Runtime", False, "npm executable not found on PATH. Required for akashic serve/build-site.")
    return CheckResult("Node Runtime", True, "Node.js and npm are installed.")


def check_writability(workspace: Workspace) -> CheckResult:
    root = workspace.root
    if not root.exists():
        return CheckResult("Writability", False, f"Knowledge repository directory does not exist: {root}.")
    if not root.is_dir():
        return CheckResult("Writability", False, f"Knowledge repository path is not a directory: {root}.")

    if not os.access(root, os.W_OK):
        return CheckResult("Writability", False, f"Knowledge repository directory is not writable: {root}.")

    test_file = root / ".akashic" / "doctor_write_test"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        test_file.write_text("write_test", encoding="utf-8")
        test_file.unlink()
    except Exception as exc:
        return CheckResult("Writability", False, f"Cannot write to knowledge repository: {exc}")
    return CheckResult("Writability", True, "Knowledge repository is writable.")


def diagnose(workspace: Workspace) -> list[CheckResult]:
    return [
        check_config(workspace),
        check_git(),
        check_repositories(workspace),
        check_agent(workspace),
        check_writability(workspace),
        check_node(),
    ]
