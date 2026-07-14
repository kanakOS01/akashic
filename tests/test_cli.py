from pathlib import Path

from akashic import __version__
from akashic.cli import app
from akashic.engine.registry import register_knowledge_base


def test_version_flag_prints_version(runner) -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_temp_knowledge_repo_fixture(temp_knowledge_repo) -> None:
    repo = temp_knowledge_repo()

    assert repo.exists()
    assert repo.is_dir()


def test_bases_command_lists_global_registry(runner, tmp_path: Path, monkeypatch) -> None:
    global_home = tmp_path / "global" / "akashic"
    monkeypatch.setenv("AKASHIC_GLOBAL_HOME", str(global_home))
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    register_knowledge_base(knowledge)

    result = runner.invoke(app, ["bases"])

    assert result.exit_code == 0, result.stdout
    assert f"Registry: {global_home / 'knowledge-bases.yaml'}" in result.stdout
    assert f"{knowledge.resolve()}\tknowledge" in result.stdout


def test_bases_command_discovers_hidden_global_knowledge_bases(
    runner,
    tmp_path: Path,
    monkeypatch,
) -> None:
    global_home = tmp_path / "global" / "akashic"
    hidden_base = global_home / ".checkout"
    (hidden_base / ".akashic").mkdir(parents=True)
    (hidden_base / ".akashic" / "config.yaml").write_text("version: 1\n", encoding="utf-8")
    monkeypatch.setenv("AKASHIC_GLOBAL_HOME", str(global_home))

    result = runner.invoke(app, ["bases"])

    assert result.exit_code == 0, result.stdout
    assert f"{hidden_base.resolve()}\tcheckout" in result.stdout


def test_serve_command_invokes_provider(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    called = False

    class FakeProcess:
        def wait(self):
            return 0

    class FakeProvider:
        def serve(self, workspace):
            nonlocal called
            called = True
            assert workspace.root == knowledge.resolve()
            return FakeProcess()

    monkeypatch.setattr("akashic.cli.default_site_provider", lambda: FakeProvider())

    result = runner.invoke(app, ["--knowledge", str(knowledge), "serve"])

    assert result.exit_code == 0, result.stdout
    assert "Serving Akashic site on http://127.0.0.1:6969" in result.stdout
    assert called


def test_serve_command_handles_site_error(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    class FakeProvider:
        def serve(self, workspace):
            from akashic.server.site import SiteError
            raise SiteError("MkDocs not installed")

    monkeypatch.setattr("akashic.cli.default_site_provider", lambda: FakeProvider())

    result = runner.invoke(app, ["--knowledge", str(knowledge), "serve"])

    assert result.exit_code != 0
    output = result.stdout + (result.stderr or "")
    assert "MkDocs not installed" in output


def test_build_site_command_invokes_provider(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    called = False

    class FakeProvider:
        def build_site(self, workspace):
            nonlocal called
            called = True
            assert workspace.root == knowledge.resolve()
            return workspace.root / "dist"

    monkeypatch.setattr("akashic.cli.default_site_provider", lambda: FakeProvider())

    result = runner.invoke(app, ["--knowledge", str(knowledge), "build-site"])

    assert result.exit_code == 0, result.stdout
    assert f"Built site at {knowledge.resolve() / 'dist'}" in result.stdout
    assert called


def test_build_site_command_handles_site_error(runner, tmp_path: Path, monkeypatch) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    class FakeProvider:
        def build_site(self, workspace):
            from akashic.server.site import SiteError
            raise SiteError("Build failed")

    monkeypatch.setattr("akashic.cli.default_site_provider", lambda: FakeProvider())

    result = runner.invoke(app, ["--knowledge", str(knowledge), "build-site"])

    assert result.exit_code != 0
    output = result.stdout + (result.stderr or "")
    assert "Build failed" in output
