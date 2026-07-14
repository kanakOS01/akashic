from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from akashic.engine.workspace import Workspace


class SiteError(RuntimeError):
    pass


class SiteProvider(Protocol):
    def serve(self, workspace: Workspace) -> subprocess.Popen:
        ...

    def build_site(self, workspace: Workspace) -> Path:
        ...


def _frontend_dir() -> Path:
    override = os.environ.get("AKASHIC_FRONTEND_DIR")
    if override:
        return Path(override).resolve()

    try:
        from importlib import resources

        packaged = (resources.files("akashic") / "frontend").resolve()
        if (packaged / "package.json").exists():
            return packaged  # type: ignore[no-any-return]
    except Exception:
        pass

    return (Path(__file__).resolve().parent.parent.parent.parent / "frontend").resolve()


def _ensure_node() -> str:
    node = shutil.which("node")
    if not node:
        raise SiteError(
            "Node.js not found on PATH. Akashic serve/build-site require Node.js (npm) to run the React site. "
            "Install Node.js from https://nodejs.org and retry."
        )
    return node


def _ensure_npm(workspace: Workspace, frontend_dir: Path) -> None:
    if not shutil.which("npm"):
        raise SiteError(
            "npm not found on PATH. Akashic serve/build-site require npm to install and run the React site. "
            "Install Node.js (which includes npm) from https://nodejs.org and retry."
        )
    if not (frontend_dir / "node_modules").exists():
        try:
            subprocess.run(
                ["npm", "install", "--include=dev"],
                cwd=frontend_dir,
                check=True,
                env={**os.environ, "AKASHIC_KB_ROOT": str(workspace.root)},
            )
        except subprocess.CalledProcessError as exc:
            raise SiteError(f"Failed to install frontend dependencies in {frontend_dir}: {exc}") from exc


@dataclass(frozen=True)
class ViteSiteProvider:
    frontend_dir: Path | None = None

    def _frontend(self) -> Path:
        return self.frontend_dir or _frontend_dir()

    def serve(self, workspace: Workspace) -> subprocess.Popen:
        _ensure_node()
        frontend_dir = self._frontend()
        _ensure_npm(workspace, frontend_dir)

        env = {
            **os.environ,
            "AKASHIC_KB_ROOT": str(workspace.root),
            "AKASHIC_PORT": str(workspace.config.site.port),
        }
        command = [
            "npm",
            "run",
            "dev",
            "--",
            "--host",
            "127.0.0.1",
            "--port",
            str(workspace.config.site.port),
        ]
        try:
            return subprocess.Popen(command, cwd=frontend_dir, env=env)
        except FileNotFoundError as exc:
            raise SiteError(
                f"Failed to start documentation server: 'npm' executable not found on PATH. "
                "Please ensure Node.js (npm) is installed."
            ) from exc

    def build_site(self, workspace: Workspace) -> Path:
        _ensure_node()
        frontend_dir = self._frontend()
        _ensure_npm(workspace, frontend_dir)

        dist = workspace.root / "dist"
        env = {
            **os.environ,
            "AKASHIC_KB_ROOT": str(workspace.root),
            "AKASHIC_DIST_DIR": str(dist),
            "AKASHIC_BASE": "./",
        }
        try:
            subprocess.run(
                ["npm", "run", "build"],
                cwd=frontend_dir,
                check=True,
                env=env,
            )
        except FileNotFoundError as exc:
            raise SiteError(
                f"Failed to build site: 'npm' executable not found on PATH. "
                "Please ensure Node.js (npm) is installed."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise SiteError(f"Failed to build site: npm build exited with status {exc.returncode}") from exc

        fallback = dist / "404.html"
        index = dist / "index.html"
        if index.exists() and not fallback.exists():
            fallback.write_bytes(index.read_bytes())

        return dist


def default_site_provider() -> SiteProvider:
    return ViteSiteProvider()
