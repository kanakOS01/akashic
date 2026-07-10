import yaml
from pathlib import Path
from typing import Dict, Any
from knowledge_engine.models.project import Project

# Expose repo root directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT_DIR / "config.yaml"

def load_config() -> Dict[str, Any]:
    """
    Read config.yaml from project root. Return a parsed dictionary.
    """
    if not CONFIG_PATH.exists():
        return {
            "knowledge_dir": "./knowledge",
            "workspace_dir": "./workspace",
            "projects": {}
        }
    try:
        content = CONFIG_PATH.read_text(encoding="utf-8")
        data = yaml.safe_load(content) or {}
        # Fill defaults
        data.setdefault("knowledge_dir", "./knowledge")
        data.setdefault("workspace_dir", "./workspace")
        data.setdefault("projects", {})
        return data
    except Exception as e:
        print(f"Warning: failed to read config.yaml: {e}")
        return {
            "knowledge_dir": "./knowledge",
            "workspace_dir": "./workspace",
            "projects": {}
        }

def save_config(config_data: Dict[str, Any]) -> None:
    """
    Write project configuration changes back to config.yaml.
    """
    try:
        CONFIG_PATH.write_text(yaml.safe_dump(config_data, sort_keys=False), encoding="utf-8")
    except Exception as e:
        print(f"Warning: failed to save config.yaml: {e}")

def get_knowledge_dir() -> Path:
    """
    Get absolute path to knowledge folder.
    """
    config = load_config()
    kd = Path(config["knowledge_dir"])
    if not kd.is_absolute():
        kd = (ROOT_DIR / kd).resolve()
    return kd

def get_workspace_dir() -> Path:
    """
    Get absolute path to workspace checkout folder.
    """
    config = load_config()
    wd = Path(config["workspace_dir"])
    if not wd.is_absolute():
        wd = (ROOT_DIR / wd).resolve()
    return wd

def get_projects() -> Dict[str, Project]:
    """
    Get all registered projects from configuration mapped by project name.
    """
    config = load_config()
    projects = {}
    for name, data in config.get("projects", {}).items():
        projects[name] = Project(
            name=data.get("name", name),
            repo=data.get("repo", ""),
            branch=data.get("branch", "main")
        )
    return projects
