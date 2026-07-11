from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def temp_knowledge_repo(tmp_path: Path) -> Callable[[str], Path]:
    def build(name: str = "knowledge") -> Path:
        repo = tmp_path / name
        repo.mkdir()
        return repo

    return build

