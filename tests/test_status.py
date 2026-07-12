from __future__ import annotations

import json
from pathlib import Path
import pytest

from akashic.cli import app
from akashic.engine.workspace import discover_workspace


def test_status_command_no_state_no_repos(runner, tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    result = runner.invoke(app, ["--knowledge", str(knowledge), "status"])

    assert result.exit_code == 0
    output = result.stdout + (result.stderr or "")
    assert "No repositories attached." in output
    assert "Last generation:\n- None" in output
    assert "Pending changes:\n- None" in output
    assert "Document statistics:" in output
    assert "- services: 0 documents" in output


def test_status_command_with_state_and_documents(runner, tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    runner.invoke(app, ["init", str(knowledge)])

    # Add dummy section directories and markdown files
    (knowledge / "services").mkdir(exist_ok=True)
    (knowledge / "services" / "a.md").write_text("# A", encoding="utf-8")
    (knowledge / "services" / "b.md").write_text("# B", encoding="utf-8")
    (knowledge / "flows").mkdir(exist_ok=True)
    (knowledge / "flows" / "flow1.md").write_text("# Flow 1", encoding="utf-8")

    # Add cache state.json
    cache_dir = knowledge / ".akashic" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    state_file = cache_dir / "state.json"
    state_data = {
        "timestamp": "2026-07-12T10:00:00Z",
        "provider": "fake-agent",
        "repos": ["bookings", "payments"],
        "duration": 15.678
    }
    state_file.write_text(json.dumps(state_data), encoding="utf-8")

    # Attach dummy repository in config
    config_file = knowledge / ".akashic" / "config.yaml"
    config_file.write_text(
        "version: 1\n"
        "repositories:\n"
        "  - name: bookings\n",
        encoding="utf-8"
    )
    local_file = knowledge / ".akashic" / "config.local.yaml"
    local_file.write_text(
        "repositories:\n"
        "  bookings: /path/to/bookings\n",
        encoding="utf-8"
    )

    result = runner.invoke(app, ["--knowledge", str(knowledge), "status"])

    assert result.exit_code == 0
    output = result.stdout + (result.stderr or "")
    assert "Attached repositories:" in output
    assert "- bookings (/path/to/bookings)" in output
    assert "Last generation:" in output
    assert "- Time: 2026-07-12T10:00:00Z" in output
    assert "- Provider: fake-agent" in output
    assert "- Repositories: bookings, payments" in output
    assert "- Duration: 15.7 seconds" in output
    assert "Document statistics:" in output
    assert "- services: 2 documents" in output
    assert "- flows: 1 document" in output
    assert "- system: 0 documents" in output
