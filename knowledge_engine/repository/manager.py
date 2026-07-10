import os
from pathlib import Path
from typing import List
import git
from knowledge_engine.models.project import Project

def prepare(project: Project, workspace_dir: Path) -> Path:
    """
    Prepare the repository.
    If project.repo is a local folder, return it.
    If project.repo is a git URL, clone/pull it into workspace_dir/{name}.
    """
    # 1. Check if it's a local folder
    repo_path = Path(project.repo)
    if not repo_path.is_absolute():
        # Resolve relative to the current directory (which is workspace root)
        repo_path = repo_path.resolve()

    if repo_path.exists() and repo_path.is_dir():
        # It's a local directory, return as-is
        return repo_path

    # 2. Treat as a git URL
    target_dir = workspace_dir / project.name
    # Create the workspace directory if it doesn't exist
    workspace_dir.mkdir(parents=True, exist_ok=True)

    if target_dir.exists():
        # Repository already cloned, pull latest changes
        try:
            repo = git.Repo(target_dir)
            # Checkout the correct branch
            repo.git.checkout(project.branch)
            # Pull latest changes
            # For local tests or git urls, pull might fail if remote doesn't have tracking branch or is offline
            # We wrap it in try-except to be robust.
            repo.git.pull()
        except Exception as e:
            # Log or handle warning
            print(f"Warning: git checkout/pull failed for {target_dir}: {e}")
    else:
        # Clone repo
        git.Repo.clone_from(project.repo, target_dir, branch=project.branch)

    return target_dir

def discover_files(path: Path) -> List[Path]:
    """
    Walk path, surface README, package.json, pyproject.toml.
    """
    target_names = {"readme.md", "package.json", "pyproject.toml"}
    discovered = []
    for root, dirs, files in os.walk(path):
        # Skip common directories like node_modules, .git, etc. to be fast
        if any(ignored in Path(root).parts for ignored in [".git", "node_modules", ".venv", "venv"]):
            continue
        for file in files:
            if file.lower() in target_names:
                discovered.append(Path(root) / file)
    return discovered
