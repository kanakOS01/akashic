from __future__ import annotations

import subprocess
from pathlib import Path

from akashic.engine.config import write_default_config
from akashic.engine.global_config import register_knowledge_base

KNOWLEDGE_DIRS = ("services", "flows", "system", "adr", "entities", "glossary")
AKASHIC_DIRS = (".akashic/cache", ".akashic/logs")
GITIGNORE_LINES = (
    ".akashic/cache/",
    ".akashic/logs/",
    ".akashic/config.local.yaml",
)


def init_workspace(root: Path, home: Path | None = None) -> Path:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    for dirname in (*KNOWLEDGE_DIRS, *AKASHIC_DIRS):
        (root / dirname).mkdir(parents=True, exist_ok=True)

    readme = root / "README.md"
    if not readme.exists():
        readme.write_text("# Akashic Knowledge Repository\n", encoding="utf-8")

    config = root / ".akashic" / "config.yaml"
    if not config.exists():
        write_default_config(config)

    _merge_gitignore(root / ".gitignore")
    _ensure_git_repo(root)
    _ensure_initial_commit(root)
    register_knowledge_base(root, home=home)
    return root


def _merge_gitignore(path: Path) -> None:
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    merged = list(existing)
    for line in GITIGNORE_LINES:
        if line not in merged:
            merged.append(line)
    path.write_text("\n".join(merged).rstrip() + "\n", encoding="utf-8")


def _ensure_git_repo(root: Path) -> None:
    if (root / ".git").exists():
        return
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)


def _has_commit(root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _ensure_initial_commit(root: Path) -> None:
    if _has_commit(root):
        return

    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Akashic",
            "-c",
            "user.email=akashic@example.invalid",
            "commit",
            "--allow-empty",
            "-m",
            "Initial Akashic repository",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
