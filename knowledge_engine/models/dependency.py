from pydantic import BaseModel

class Dependency(BaseModel):
    name: str
