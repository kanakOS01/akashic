from __future__ import annotations

import subprocess
from pathlib import Path

from akashic.cli import app
from akashic.server.site import ViteSiteProvider
from akashic.engine.workspace import discover_workspace


def _frontend_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "frontend"


def test_serve_invokes_npm_run_dev_on_configured_port(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    workspace = discover_workspace(knowledge=knowledge)
    (_frontend_dir() / "node_modules").mkdir(parents=True, exist_ok=True)
    calls: list[tuple[list[str], Path, dict]] = []

    class FakeProcess:
        def wait(self):
            return 0

    def fake_popen(command, cwd, env=None):
        calls.append((command, cwd, env or {}))
        return FakeProcess()

    monkeypatch.setattr("akashic.server.site.subprocess.Popen", fake_popen)

    process = ViteSiteProvider(frontend_dir=_frontend_dir()).serve(workspace)

    assert isinstance(process, FakeProcess)
    assert len(calls) == 1
    command, cwd, env = calls[0]
    assert command[:3] == ["npm", "run", "dev"]
    assert "--port" in command
    assert command[command.index("--port") + 1] == str(workspace.config.site.port)
    assert cwd == _frontend_dir()
    assert env.get("AKASHIC_KB_ROOT") == str(knowledge)
    assert env.get("AKASHIC_PORT") == str(workspace.config.site.port)


def test_build_site_invokes_npm_run_build_and_produces_dist(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    workspace = discover_workspace(knowledge=knowledge)
    (_frontend_dir() / "node_modules").mkdir(parents=True, exist_ok=True)
    calls: list[tuple[list[str], Path, dict]] = []
    created_files: list[Path] = []

    def fake_run(command, cwd, check, env=None):
        calls.append((command, cwd, env or {}))
        dist = Path(env["AKASHIC_DIST_DIR"])
        dist.mkdir(parents=True)
        (dist / "index.html").write_text("<html></html>\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("akashic.server.site.subprocess.run", fake_run)

    provider = ViteSiteProvider(frontend_dir=_frontend_dir())
    dist = provider.build_site(workspace)

    assert dist == knowledge / "dist"
    assert (dist / "index.html").exists()
    assert (dist / "404.html").exists(), "SPA fallback 404.html should be copied"
    assert calls == [
        (
            ["npm", "run", "build"],
            _frontend_dir(),
            {
                **_base_env(),
                "AKASHIC_KB_ROOT": str(knowledge),
                "AKASHIC_DIST_DIR": str(knowledge / "dist"),
                "AKASHIC_BASE": "./",
            },
        )
    ]


def test_provider_raises_site_error_on_missing_npm(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    workspace = discover_workspace(knowledge=knowledge)
    provider = ViteSiteProvider(frontend_dir=_frontend_dir())

    import pytest
    from akashic.server.site import SiteError

    monkeypatch.setattr("akashic.server.site.shutil.which", lambda name: None if name == "npm" else "/usr/bin/node")
    with pytest.raises(SiteError) as exc_info:
        provider.serve(workspace)
    assert "npm" in str(exc_info.value)

    with pytest.raises(SiteError) as exc_info:
        provider.build_site(workspace)
    assert "npm" in str(exc_info.value)


def _base_env() -> dict:
    import os

    return dict(os.environ)


def _init_knowledge(runner, tmp_path: Path) -> Path:
    knowledge = tmp_path / "knowledge"
    result = runner.invoke(app, ["init", str(knowledge)])
    assert result.exit_code == 0, result.stdout
    return knowledge.resolve()
