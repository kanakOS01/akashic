from pathlib import Path
from typing import Dict, Any

class ReadmeExtractor:
    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """
        Extract service name and description from README.md.
        Name: First '#' heading.
        Description: First paragraph following that heading.
        """
        readme_path = repo_path / "README.md"
        # Try case-insensitive lookup
        if not readme_path.exists():
            for child in repo_path.iterdir():
                if child.name.lower() == "readme.md":
                    readme_path = child
                    break
        
        if not readme_path.exists():
            return {}

        try:
            content = readme_path.read_text(encoding="utf-8")
        except Exception:
            return {}

        lines = [line.strip() for line in content.splitlines()]
        
        name = None
        description = None
        
        # 1. Find the first `#` heading
        heading_index = -1
        for idx, line in enumerate(lines):
            if line.startswith("# "):
                name = line[2:].strip()
                heading_index = idx
                break
            elif line.startswith("#"):
                name = line.lstrip("#").strip()
                heading_index = idx
                break

        # 2. Find the first paragraph following the heading (or from start)
        start_idx = heading_index + 1 if heading_index != -1 else 0
        paragraph_lines = []
        for line in lines[start_idx:]:
            if line:
                # If we encounter a heading or code block or HTML comment, and we have
                # already started a paragraph, finish it. Otherwise, skip those.
                if line.startswith("#") or line.startswith("```") or line.startswith("<!--"):
                    if paragraph_lines:
                        break
                    continue
                paragraph_lines.append(line)
            else:
                if paragraph_lines:
                    break
        
        if paragraph_lines:
            description = " ".join(paragraph_lines)

        result = {}
        if name:
            result["name"] = name
        if description:
            result["description"] = description
        return result
