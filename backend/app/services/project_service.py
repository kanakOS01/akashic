from typing import List, Optional
from knowledge_engine.models.project import Project
from backend.app.config import get_projects, load_config, save_config

def list_projects() -> List[Project]:
    """
    List all configured projects.
    """
    return list(get_projects().values())

def get_project(name: str) -> Optional[Project]:
    """
    Retrieve a specific project by name.
    """
    return get_projects().get(name)

def add_project(project: Project) -> Project:
    """
    Add or update a project and save to config.yaml.
    """
    config = load_config()
    config["projects"][project.name] = {
        "name": project.name,
        "repo": project.repo,
        "branch": project.branch
    }
    save_config(config)
    return project

def delete_project(name: str) -> bool:
    """
    Delete a project from config.yaml. Returns True if deleted, False if not found.
    """
    config = load_config()
    if name in config.get("projects", {}):
        del config["projects"][name]
        save_config(config)
        return True
    return False
