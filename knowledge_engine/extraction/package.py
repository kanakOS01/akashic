import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List

# tomllib is in python 3.11+, fallback to tomli if not present (though project requires >=3.11)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

class PackageExtractor:
    def extract(self, repo_path: Path) -> Dict[str, Any]:
        """
        Extract package name and dependencies from package.json or pyproject.toml.
        """
        package_json_path = repo_path / "package.json"
        pyproject_toml_path = repo_path / "pyproject.toml"

        result: Dict[str, Any] = {}

        # 1. Try package.json
        if package_json_path.exists():
            try:
                data = json.loads(package_json_path.read_text(encoding="utf-8"))
                if "name" in data and isinstance(data["name"], str):
                    result["name"] = data["name"]
                
                depends_on = []
                # Check dependencies
                if "dependencies" in data and isinstance(data["dependencies"], dict):
                    depends_on.extend(data["dependencies"].keys())
                # Check devDependencies (optional, but let's stick to standard dependencies first)
                if depends_on:
                    result["depends_on"] = depends_on
            except Exception as e:
                print(f"Warning: failed to parse package.json: {e}")

        # 2. Try pyproject.toml if package.json was not found or didn't provide everything
        if pyproject_toml_path.exists() and tomllib:
            try:
                data = tomllib.loads(pyproject_toml_path.read_text(encoding="utf-8"))
                project_section = data.get("project", {})
                
                if "name" in project_section and isinstance(project_section["name"], str):
                    if "name" not in result:
                        result["name"] = project_section["name"]
                
                dependencies = project_section.get("dependencies", [])
                if dependencies and isinstance(dependencies, list):
                    depends_on = result.get("depends_on", [])
                    for dep in dependencies:
                        if isinstance(dep, str):
                            # Clean dependency string, e.g. "fastapi>=0.110.0" -> "fastapi"
                            # Matches letters, digits, dashes, underscores, dots at the start
                            match = re.match(r"^([a-zA-Z0-9_\-\.]+)", dep.strip())
                            if match:
                                dep_name = match.group(1)
                                if dep_name not in depends_on:
                                    depends_on.append(dep_name)
                    if depends_on:
                        result["depends_on"] = depends_on
            except Exception as e:
                print(f"Warning: failed to parse pyproject.toml: {e}")

        return result
