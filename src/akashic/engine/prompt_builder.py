from __future__ import annotations

from importlib import resources
from pathlib import Path
from string import Template

from akashic.engine.config import AkashicConfig, AkashicLocalConfig

PROMPT_TEMPLATE_NAMES = (
    "master.md",
    "generate_service.md",
    "generate_flow.md",
    "generate_system.md",
    "generate_entity.md",
    "generate_adr.md",
)

DOC_TYPE_TEMPLATE_NAMES = tuple(name for name in PROMPT_TEMPLATE_NAMES if name != "master.md")


def load_prompt_templates(custom_dir: Path | None = None) -> dict[str, str]:
    templates = {name: _read_bundled_template(name) for name in PROMPT_TEMPLATE_NAMES}
    if custom_dir is None:
        return templates

    for name in PROMPT_TEMPLATE_NAMES:
        override = custom_dir / name
        if override.exists():
            templates[name] = override.read_text(encoding="utf-8")
    return templates


def build_master_prompt(
    config: AkashicConfig,
    local_config: AkashicLocalConfig,
    templates: dict[str, str],
) -> str:
    missing = [name for name in PROMPT_TEMPLATE_NAMES if name not in templates]
    if missing:
        raise ValueError(f"Missing prompt templates: {', '.join(missing)}")

    context = {
        "repository_list": _repository_list(config, local_config),
        "knowledge_layout": _knowledge_layout(config.knowledge.path),
        "human_preservation_rules": _human_preservation_rules(),
        "frontmatter_contract": _frontmatter_contract(),
        "doc_type_templates": _doc_type_templates(templates),
    }
    return Template(templates["master.md"]).safe_substitute(context).strip() + "\n"


def load_workspace_prompt_templates(root: Path) -> dict[str, str]:
    return load_prompt_templates(root / ".akashic" / "custom-prompts")


def _read_bundled_template(name: str) -> str:
    return resources.files("akashic.prompts").joinpath(name).read_text(encoding="utf-8")


def _repository_list(config: AkashicConfig, local_config: AkashicLocalConfig) -> str:
    if not config.repositories:
        return "- No source repositories attached."

    rows: list[str] = []
    for repository in sorted(config.repositories, key=lambda item: item.name):
        path = local_config.repositories.get(repository.name)
        if path:
            rows.append(f"- {repository.name}: {path}")
        else:
            rows.append(f"- {repository.name}: [missing local path]")
    return "\n".join(rows)


def _knowledge_layout(path: str) -> str:
    root = path.rstrip("/") or "."
    return "\n".join(
        [
            f"- Knowledge root: {root}",
            "- services/: generated service docs",
            "- flows/: generated flow docs",
            "- system/: generated system docs",
            "- entities/: generated entity docs",
            "- adr/: generated architecture decision records",
            "- glossary/: shared terminology",
        ]
    )


def _human_preservation_rules() -> str:
    return "\n".join(
        [
            "- Preserve any `<!-- HUMAN:START -->` to `<!-- HUMAN:END -->` block exactly.",
            "- Never rewrite, move, summarize, or delete HUMAN sections.",
            "- Add generated content outside HUMAN sections only.",
        ]
    )


def _frontmatter_contract() -> str:
    return "\n".join(
        [
            "Every generated markdown file must begin with YAML frontmatter:",
            "- title: human-readable document title",
            "- type: one of service, flow, system, entity, adr",
            "- source_repositories: list of attached repository names used",
            "- generated_at: ISO-8601 timestamp",
            "- akashic_version: prompt/config contract version",
        ]
    )


def _doc_type_templates(templates: dict[str, str]) -> str:
    return "\n\n".join(templates[name].strip() for name in DOC_TYPE_TEMPLATE_NAMES)
