from __future__ import annotations

from akashic import __version__
from akashic.cli import app


def test_version_flag_prints_version(runner) -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_temp_knowledge_repo_fixture(temp_knowledge_repo) -> None:
    repo = temp_knowledge_repo()

    assert repo.exists()
    assert repo.is_dir()

