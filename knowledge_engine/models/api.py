from pydantic import BaseModel

class Api(BaseModel):
    name: str
    method: str
    path: str
    description: str
