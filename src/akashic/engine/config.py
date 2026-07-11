from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class KnowledgeConfig(BaseModel):
    path: str = "."


class SiteConfig(BaseModel):
    port: int = 6969


class GenerationConfig(BaseModel):
    model: str | None = None


class AkashicConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = 1
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    repositories: list[str] = Field(default_factory=list)
    agent: str | None = None
    site: SiteConfig = Field(default_factory=SiteConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)


def default_config() -> AkashicConfig:
    return AkashicConfig()


def config_to_dict(config: AkashicConfig) -> dict[str, Any]:
    return config.model_dump(mode="json")


def write_default_config(path: Path) -> None:
    data = config_to_dict(default_config())
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def load_config(path: Path) -> AkashicConfig:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid Akashic config YAML at {path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Unable to read Akashic config at {path}: {exc}") from exc

    try:
        return AkashicConfig.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid Akashic config at {path}: {exc}") from exc

