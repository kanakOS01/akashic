from fastapi import APIRouter, HTTPException
from typing import List
from knowledge_engine.models.project import Project
from backend.app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=Project)
def create_project(project: Project):
    """
    Register a new project.
    """
    return project_service.add_project(project)

@router.get("", response_model=List[Project])
def list_projects():
    """
    List all registered projects.
    """
    return project_service.list_projects()

@router.delete("/{name}")
def delete_project(name: str):
    """
    Remove a registered project.
    """
    success = project_service.delete_project(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found.")
    return {"message": f"Project '{name}' deleted successfully."}
