from pydantic import BaseModel

class Project(BaseModel):
    name: str
    repo: str
    branch: str = "main"
