from pydantic import BaseModel

class KnowledgePage(BaseModel):
    path: str
    frontmatter: dict
    body: str
