import uuid
from typing import Dict, Any, Optional
from fastapi import BackgroundTasks, HTTPException
from knowledge_engine.pipeline import run as run_pipeline
from backend.app.config import get_projects, get_workspace_dir, get_knowledge_dir

# In-memory job state store
jobs: Dict[str, Dict[str, Any]] = {}

def sync_task(job_id: str, project_name: str) -> None:
    """
    Background worker function that runs the compilation pipeline.
    """
    projects = get_projects()
    project = projects.get(project_name)
    if not project:
        jobs[job_id] = {
            "status": "failed",
            "page": None,
            "error": f"Project '{project_name}' not found."
        }
        return

    try:
        workspace_dir = get_workspace_dir()
        knowledge_dir = get_knowledge_dir()
        page = run_pipeline(project, workspace_dir, knowledge_dir)
        # Convert page to dict for response safety/serialization
        jobs[job_id] = {
            "status": "succeeded",
            "page": page.model_dump(),
            "error": None
        }
    except Exception as e:
        jobs[job_id] = {
            "status": "failed",
            "page": None,
            "error": str(e)
        }

def start_sync(project_name: str, background_tasks: BackgroundTasks) -> str:
    """
    Initialize and spawn a background sync job.
    """
    projects = get_projects()
    if project_name not in projects:
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found.")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "running",
        "page": None,
        "error": None
    }
    background_tasks.add_task(sync_task, job_id, project_name)
    return job_id

def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Check the status of a sync job.
    """
    return jobs.get(job_id)
