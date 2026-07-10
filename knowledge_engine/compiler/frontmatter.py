import yaml
from typing import Tuple, Dict, Any

def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Split YAML frontmatter from markdown body.
    Returns (frontmatter_dict, body_text).
    """
    stripped_content = content.lstrip()
    if stripped_content.startswith("---"):
        # Split on the first two '---' markers
        parts = stripped_content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body_text = parts[2]
            try:
                fm_data = yaml.safe_load(fm_text)
                if isinstance(fm_data, dict):
                    return fm_data, body_text
            except Exception as e:
                print(f"Warning: failed to parse YAML frontmatter: {e}")
    return {}, content

def to_frontmatter(frontmatter: Dict[str, Any]) -> str:
    """
    Serialize dictionary to YAML frontmatter block.
    """
    # Return safely dumped yaml without extra line breaks
    return yaml.safe_dump(frontmatter, sort_keys=False).strip()
