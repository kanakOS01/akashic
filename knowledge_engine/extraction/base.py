from typing import Protocol, Dict, Any
from pathlib import Path

class Extractor(Protocol):
    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """
        Extract facts from repository and return a dictionary of partial facts.
        """
        ...
