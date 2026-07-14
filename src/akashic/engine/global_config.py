from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class KnowledgeBaseRegistryEntry(BaseModel):
    path: str


class AkashicGlobalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    knowledge_bases: dict[str, KnowledgeBaseRegistryEntry] = Field(default_factory=dict)


def global_config_path(home: Path | None = None) -> Path:
    return (home or Path.home()) / ".akashic" / "config.yaml"


def default_global_config() -> AkashicGlobalConfig:
    return AkashicGlobalConfig()


def load_global_config(path: Path) -> AkashicGlobalConfig:
    if not path.exists():
        return default_global_config()

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid Akashic global config YAML at {path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Unable to read Akashic global config at {path}: {exc}") from exc

    try:
        return AkashicGlobalConfig.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid Akashic global config at {path}: {exc}") from exc


def write_global_config(path: Path, config: AkashicGlobalConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = config.model_dump(mode="json")
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def register_knowledge_base(root: Path, home: Path | None = None) -> str:
    root = root.resolve()
    base_name = root.name
    path = global_config_path(home)
    config = load_global_config(path)
    name = _available_name(config, base_name, str(root))
    config.knowledge_bases[name] = KnowledgeBaseRegistryEntry(path=str(root))
    write_global_config(path, config)
    return name


def _available_name(config: AkashicGlobalConfig, base_name: str, root: str) -> str:
    existing = config.knowledge_bases.get(base_name)
    if existing is None or existing.path == root:
        return base_name

    index = 2
    while True:
        candidate = f"{base_name}-{index}"
        existing = config.knowledge_bases.get(candidate)
        if existing is None or existing.path == root:
            return candidate
        index += 1
