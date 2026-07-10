import pytest
import yaml
from pathlib import Path
import backend.app.config as app_config

@pytest.fixture(autouse=True)
def setup_test_config(monkeypatch, tmp_path):
    """
    Set up a temporary environment configuration for running pytest safely
    without polluting workspace repository state.
    """
    knowledge_dir = tmp_path / "knowledge"
    workspace_dir = tmp_path / "workspace"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    test_config_path = tmp_path / "config.yaml"
    
    # Path to the offline sample fixture
    repo_root = Path(__file__).resolve().parent.parent
    sample_repo_path = repo_root / "examples" / "sample-repo"

    config_data = {
        "knowledge_dir": str(knowledge_dir),
        "workspace_dir": str(workspace_dir),
        "projects": {
            "sample": {
                "name": "sample",
                "repo": str(sample_repo_path),
                "branch": "main"
            }
        }
    }
    
    test_config_path.write_text(yaml.safe_dump(config_data), encoding="utf-8")

    # Patch config file target paths inside config module
    monkeypatch.setattr(app_config, "CONFIG_PATH", test_config_path)
    monkeypatch.setattr(app_config, "get_knowledge_dir", lambda: knowledge_dir)
    monkeypatch.setattr(app_config, "get_workspace_dir", lambda: workspace_dir)

    yield test_config_path, knowledge_dir, workspace_dir
