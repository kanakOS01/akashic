from fastapi import APIRouter, BackgroundTasks, HTTPException
from backend.app.services import sync_service

router = APIRouter(tags=["sync"])

@router.post("/projects/{name}/sync")
def sync_project(name: str, background_tasks: BackgroundTasks):
    """
    Trigger compilation sync pipeline in the background.
    Returns the generated job_id to track execution.
    """
    job_id = sync_service.start_sync(name, background_tasks)
    return {"job_id": job_id}

@router.get("/sync/{job_id}")
def get_sync_status(job_id: str):
    """
    Query the status and results of a sync job.
    """
    status = sync_service.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Sync job '{job_id}' not found.")
    return status
