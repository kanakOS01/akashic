from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from akashic.cli import app
from akashic.server.site import MkDocsSiteProvider
from akashic.engine.workspace import discover_workspace


def test_build_site_invokes_mkdocs_and_produces_dist(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    (knowledge / "services" / "billing.md").write_text("# Billing\n", encoding="utf-8")
    workspace = discover_workspace(knowledge=knowledge)
    calls: list[tuple[list[str], Path]] = []

    def fake_run(command, cwd, check):
        calls.append((command, cwd))
        dist = Path(command[command.index("--site-dir") + 1])
        dist.mkdir(parents=True)
        (dist / "index.html").write_text("<html></html>\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("akashic.server.site.subprocess.run", fake_run)

    dist = MkDocsSiteProvider().build_site(workspace)

    assert dist == knowledge / "dist"
    assert (dist / "index.html").exists()
    assert calls == [
        (
            [
                "mkdocs",
                "build",
                "--config-file",
                str(knowledge / ".akashic" / "cache" / "site" / "mkdocs.yml"),
                "--site-dir",
                str(knowledge / "dist"),
            ],
            knowledge.resolve(),
        )
    ]
    config = yaml.safe_load((knowledge / ".akashic" / "cache" / "site" / "mkdocs.yml").read_text())
    assert config["docs_dir"] == str(knowledge.resolve())
    assert config["theme"]["name"] == "material"
    assert "search" in config["plugins"]
    assert "pymdownx.superfences" in str(config["markdown_extensions"])
    assert config["exclude_docs"] == "tests/\nsrc/\npyproject.toml\nuv.lock"
    assert {"Services": [{"Billing": "services/billing.md"}]} in config["nav"]


def test_serve_invokes_mkdocs_on_configured_port(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    workspace = discover_workspace(knowledge=knowledge)
    calls: list[tuple[list[str], Path]] = []

    class FakeProcess:
        def wait(self):
            return 0

    def fake_popen(command, cwd):
        calls.append((command, cwd))
        return FakeProcess()

    monkeypatch.setattr("akashic.server.site.subprocess.Popen", fake_popen)

    process = MkDocsSiteProvider().serve(workspace)

    assert isinstance(process, FakeProcess)
    assert calls == [
        (
            [
                "mkdocs",
                "serve",
                "--config-file",
                str(knowledge / ".akashic" / "cache" / "site" / "mkdocs.yml"),
                "--dev-addr",
                "127.0.0.1:6969",
            ],
            knowledge.resolve(),
        )
    ]


def _init_knowledge(runner, tmp_path: Path) -> Path:
    knowledge = tmp_path / "knowledge"
    result = runner.invoke(app, ["init", str(knowledge)])
    assert result.exit_code == 0, result.stdout
    return knowledge.resolve()


def test_provider_raises_site_error_on_missing_executable(runner, tmp_path: Path) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    workspace = discover_workspace(knowledge=knowledge)
    provider = MkDocsSiteProvider(executable="non-existent-executable")

    import pytest
    from akashic.server.site import SiteError

    with pytest.raises(SiteError) as exc_info:
        provider.build_site(workspace)
    assert "executable not found on PATH" in str(exc_info.value)

    with pytest.raises(SiteError) as exc_info:
        provider.serve(workspace)
    assert "executable not found on PATH" in str(exc_info.value)


def test_provider_raises_site_error_on_build_failure(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = _init_knowledge(runner, tmp_path)
    workspace = discover_workspace(knowledge=knowledge)
    provider = MkDocsSiteProvider()

    def fake_run(command, cwd, check):
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr("akashic.server.site.subprocess.run", fake_run)

    import pytest
    from akashic.server.site import SiteError

    with pytest.raises(SiteError) as exc_info:
        provider.build_site(workspace)
    assert "mkdocs exited with status 1" in str(exc_info.value)

