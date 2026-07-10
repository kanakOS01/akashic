from pydantic import BaseModel
from typing import List
from knowledge_engine.models.api import Api
from knowledge_engine.models.event import Event

class Service(BaseModel):
    name: str
    description: str
    depends_on: List[str]
    emits_events: List[Event]
    consumes_events: List[Event]
    apis: List[Api]
    source_files: List[str]
