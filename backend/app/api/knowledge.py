import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from backend.app.config import get_knowledge_dir

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.get("")
def list_knowledge_pages():
    """
    List all generated markdown documentation pages inside the knowledge base.
    """
    knowledge_dir = get_knowledge_dir()
    if not knowledge_dir.exists():
        return []
    
    pages = []
    for root, dirs, files in os.walk(knowledge_dir):
        # Skip git directory structure
        if ".git" in Path(root).parts:
            continue
        for file in files:
            if file.endswith(".md"):
                full_path = Path(root) / file
                try:
                    rel_path = full_path.relative_to(knowledge_dir)
                    pages.append(str(rel_path))
                except ValueError:
                    continue
    return pages

@router.get("/{path:path}", response_class=PlainTextResponse)
def get_knowledge_page(path: str):
    """
    Retrieve the raw markdown content of a generated page.
    Supports paths with or without .md extension.
    """
    knowledge_dir = get_knowledge_dir()
    
    # Resolve target file path
    target_path = knowledge_dir / path
    if not target_path.exists() and not path.endswith(".md"):
        target_path = knowledge_dir / f"{path}.md"
        
    # Standard security directory traversal guard
    try:
        resolved_target = target_path.resolve()
        resolved_knowledge_dir = knowledge_dir.resolve()
        # Verify target is nested inside knowledge directory
        if not str(resolved_target).startswith(str(resolved_knowledge_dir)):
            raise HTTPException(status_code=403, detail="Access denied.")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid page path.")
        
    if not resolved_target.exists() or not resolved_target.is_file():
        raise HTTPException(status_code=404, detail="Knowledge page not found.")
        
    try:
        return resolved_target.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read knowledge file: {e}")
