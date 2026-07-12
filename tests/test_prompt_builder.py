from __future__ import annotations

from pathlib import Path

from akashic.engine.config import AkashicLocalConfig, RepositoryConfig, default_config
from akashic.engine.prompt_builder import build_master_prompt, load_prompt_templates


def test_prompt_composition_contains_repos_layout_human_rules_and_frontmatter() -> None:
    config = default_config()
    config.repositories = [
        RepositoryConfig(name="api"),
        RepositoryConfig(name="web"),
    ]
    local_config = AkashicLocalConfig(
        repositories={
            "api": "/src/api",
            "web": "/src/web",
        }
    )

    prompt = build_master_prompt(config, local_config, load_prompt_templates())

    assert "api: /src/api" in prompt
    assert "web: /src/web" in prompt
    assert "services/: generated service docs" in prompt
    assert "flows/: generated flow docs" in prompt
    assert "Preserve any `<!-- HUMAN:START -->`" in prompt
    assert "source_repositories: list of attached repository names used" in prompt
    assert "### Service Document Template" in prompt
    assert "### Flow Document Template" in prompt
    assert "### System Document Template" in prompt
    assert "### Entity Document Template" in prompt
    assert "### ADR Document Template" in prompt


def test_prompt_composition_marks_missing_local_path() -> None:
    config = default_config()
    config.repositories = [RepositoryConfig(name="api")]

    prompt = build_master_prompt(config, AkashicLocalConfig(), load_prompt_templates())

    assert "api: [missing local path]" in prompt


def test_custom_prompt_override_wins(tmp_path: Path) -> None:
    custom_dir = tmp_path / ".akashic" / "custom-prompts"
    custom_dir.mkdir(parents=True)
    (custom_dir / "generate_service.md").write_text("CUSTOM SERVICE TEMPLATE", encoding="utf-8")

    templates = load_prompt_templates(custom_dir)
    prompt = build_master_prompt(default_config(), AkashicLocalConfig(), templates)

    assert "CUSTOM SERVICE TEMPLATE" in prompt
    assert "### Service Document Template" not in prompt
    assert "### Flow Document Template" in prompt
