import git
from pathlib import Path

def ensure_repo(knowledge_dir: Path) -> git.Repo:
    """
    Ensure the knowledge directory is a git repository.
    If not, initialize a git repository.
    """
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    try:
        repo = git.Repo(knowledge_dir)
    except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
        repo = git.Repo.init(knowledge_dir)
        # Create an initial commit if empty to ensure repo is in a clean state
        readme = knowledge_dir / "README.md"
        if not readme.exists():
            readme.write_text("# Akashic Knowledge Base\n\nGenerated documentation by Akashic.", encoding="utf-8")
        repo.git.add(A=True)
        repo.index.commit("Initial commit of knowledge base")
    return repo

def commit(knowledge_dir: Path, message: str):
    """
    Add all untracked/modified changes in knowledge_dir and commit them.
    If no changes exist, do nothing.
    """
    repo = ensure_repo(knowledge_dir)
    # Add all files (including untracked ones)
    repo.git.add(A=True)
    
    # Check if there are actual staged differences to commit
    if repo.is_dirty(untracked_files=True) or len(repo.index.diff("HEAD")) > 0:
        repo.index.commit(message)
    else:
        print("No changes to commit in the knowledge base.")
