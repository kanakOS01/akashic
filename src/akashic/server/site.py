from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import yaml

from akashic.engine.workspace import Workspace


class SiteError(RuntimeError):
    pass


class SiteProvider(Protocol):
    def serve(self, workspace: Workspace) -> subprocess.Popen:
        ...

    def build_site(self, workspace: Workspace) -> Path:
        ...


@dataclass(frozen=True)
class MkDocsSiteProvider:
    executable: str = "mkdocs"

    def serve(self, workspace: Workspace) -> subprocess.Popen:
        config_path = self._write_config(workspace)
        try:
            return subprocess.Popen(
                [
                    self.executable,
                    "serve",
                    "--config-file",
                    str(config_path),
                    "--dev-addr",
                    f"127.0.0.1:{workspace.config.site.port}",
                ],
                cwd=workspace.root,
            )
        except FileNotFoundError as exc:
            raise SiteError(
                f"Failed to start documentation server: '{self.executable}' executable not found on PATH. "
                "Please ensure MkDocs is installed."
            ) from exc

    def build_site(self, workspace: Workspace) -> Path:
        config_path = self._write_config(workspace)
        dist = workspace.root / "dist"
        try:
            subprocess.run(
                [
                    self.executable,
                    "build",
                    "--config-file",
                    str(config_path),
                    "--site-dir",
                    str(dist),
                ],
                cwd=workspace.root,
                check=True,
            )
        except FileNotFoundError as exc:
            raise SiteError(
                f"Failed to build site: '{self.executable}' executable not found on PATH. "
                "Please ensure MkDocs is installed."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise SiteError(f"Failed to build site: mkdocs exited with status {exc.returncode}") from exc
        return dist

    def _write_config(self, workspace: Workspace) -> Path:
        config_dir = workspace.root / ".akashic" / "cache" / "site"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "mkdocs.yml"
        config = {
            "site_name": "Akashic",
            "docs_dir": str(workspace.root),
            "site_dir": str(workspace.root / "dist"),
            "exclude_docs": [
                "tests/",
                "src/",
                "pyproject.toml",
                "uv.lock",
            ],
            "theme": {
                "name": "material",
                "features": ["navigation.instant", "navigation.sections", "search.suggest"],
            },
            "plugins": ["search"],
            "markdown_extensions": [
                "admonition",
                "tables",
                "toc",
                {
                    "pymdownx.superfences": {
                        "custom_fences": [
                            {
                                "name": "mermaid",
                                "class": "mermaid",
                                "format": "!!python/name:pymdownx.superfences.fence_code_format",
                            }
                        ]
                    }
                },
            ],
            "nav": self._nav(workspace.root),
        }
        config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        return config_path

    def _nav(self, root: Path) -> list[dict[str, str] | str]:
        nav: list[dict[str, str] | str] = []
        readme = root / "README.md"
        if readme.exists():
            nav.append({"Home": "README.md"})

        for dirname in ("services", "flows", "system", "entities", "adr", "glossary"):
            section = root / dirname
            if not section.exists():
                continue
            pages = [
                {page.stem.replace("-", " ").title(): str(page.relative_to(root))}
                for page in sorted(section.rglob("*.md"))
            ]
            if pages:
                nav.append({dirname.title(): pages})
        return nav


def default_site_provider() -> SiteProvider:
    return MkDocsSiteProvider()
