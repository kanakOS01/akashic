from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_projects_lifecycle(setup_test_config):
    """
    Test Project register, list, and delete endpoints.
    """
    # 1. Get initial project (which is 'sample' loaded from conftest.py)
    res = client.get("/projects")
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) == 1
    assert projects[0]["name"] == "sample"

    # 2. Register a new project
    new_project = {
        "name": "dummy-project",
        "repo": "https://github.com/akashic/dummy.git",
        "branch": "develop"
    }
    res = client.post("/projects", json=new_project)
    assert res.status_code == 200
    assert res.json()["name"] == "dummy-project"
    assert res.json()["branch"] == "develop"

    # Verify project is listed
    res = client.get("/projects")
    assert len(res.json()) == 2

    # 3. Delete the newly registered project
    res = client.delete("/projects/dummy-project")
    assert res.status_code == 200
    assert "deleted successfully" in res.json()["message"]

    # Verify project is removed
    res = client.get("/projects")
    assert len(res.json()) == 1

def test_sync_and_knowledge_access(setup_test_config):
    """
    Test sync trigger, status check, pages list, and page detail retrieval.
    """
    # 1. Trigger sync background task
    res = client.post("/projects/sample/sync")
    assert res.status_code == 200
    job_id = res.json().get("job_id")
    assert job_id is not None

    # 2. Get status of sync job.
    # Note: FastAPI TestClient executes BackgroundTasks synchronously on return
    res = client.get(f"/sync/{job_id}")
    assert res.status_code == 200
    job_info = res.json()
    assert job_info["status"] == "succeeded"
    assert job_info["page"] is not None
    assert job_info["error"] is None

    # 3. Get knowledge base listing
    res = client.get("/knowledge")
    assert res.status_code == 200
    pages = res.json()
    assert "services/sample.md" in pages

    # 4. Fetch the raw compiled markdown page content
    res = client.get("/knowledge/services/sample.md")
    assert res.status_code == 200
    assert "# sample-service" in res.text
    assert "## Overview" in res.text
    assert "## Dependencies" in res.text
    assert "express" in res.text
    assert "lodash" in res.text
