from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REGISTRY_FILENAME = "knowledge-bases.yaml"


@dataclass(frozen=True)
class KnowledgeBaseReference:
    name: str
    path: Path

    @property
    def reference(self) -> Path:
        return self.path


def global_akashic_dir(
    home: Path | None = None,
    env: dict[str, str] | None | Any = None,
) -> Path:
    if env is None:
        env = os.environ

    configured = env.get("AKASHIC_GLOBAL_HOME")
    if configured:
        return Path(configured).expanduser().resolve()
    return (home or Path.home()) / "akashic"


def registry_path(
    home: Path | None = None,
    env: dict[str, str] | None | Any = None,
) -> Path:
    return global_akashic_dir(home=home, env=env) / REGISTRY_FILENAME


def list_knowledge_bases(
    home: Path | None = None,
    env: dict[str, str] | None | Any = None,
) -> list[KnowledgeBaseReference]:
    path = registry_path(home=home, env=env)
    if not path.exists():
        return []

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    references = raw.get("knowledge_bases", [])
    bases: list[KnowledgeBaseReference] = []
    for reference in references:
        if not isinstance(reference, dict):
            continue
        name = reference.get("name")
        base_path = reference.get("reference", reference.get("path"))
        if isinstance(name, str) and isinstance(base_path, str):
            bases.append(KnowledgeBaseReference(name=name, path=Path(base_path)))
    return bases


def discover_knowledge_bases(
    home: Path | None = None,
    env: dict[str, str] | None | Any = None,
) -> list[KnowledgeBaseReference]:
    bases_by_path = {
        base.path.resolve(): KnowledgeBaseReference(name=base.name, path=base.path.resolve())
        for base in list_knowledge_bases(home=home, env=env)
    }

    global_dir = global_akashic_dir(home=home, env=env)
    if global_dir.exists():
        for candidate in global_dir.iterdir():
            if not candidate.is_dir():
                continue
            if not (candidate / ".akashic" / "config.yaml").exists():
                continue
            resolved = candidate.resolve()
            bases_by_path.setdefault(
                resolved,
                KnowledgeBaseReference(name=_reference_name(candidate), path=resolved),
            )

    return sorted(bases_by_path.values(), key=lambda base: str(base.reference).lower())


def register_knowledge_base(
    root: Path,
    name: str | None = None,
    home: Path | None = None,
    env: dict[str, str] | None | Any = None,
) -> KnowledgeBaseReference:
    root = root.resolve()
    desired_name = name or _reference_name(root)
    bases = list_knowledge_bases(home=home, env=env)

    existing_names_by_path = {base.path.resolve(): base.name for base in bases}
    registered_name = existing_names_by_path.get(root)
    if registered_name is None:
        registered_name = _unique_name(desired_name, bases)

    updated = [
        base
        for base in bases
        if base.path.resolve() != root
    ]
    reference = KnowledgeBaseReference(name=registered_name, path=root)
    updated.append(reference)
    updated.sort(key=lambda base: base.name.lower())

    path = registry_path(home=home, env=env)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "version": 1,
        "knowledge_bases": [
            {"name": base.name, "reference": str(base.reference)}
            for base in updated
        ],
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return reference


def _unique_name(desired_name: str, bases: list[KnowledgeBaseReference]) -> str:
    existing = {base.name for base in bases}
    if desired_name not in existing:
        return desired_name

    index = 2
    while f"{desired_name}-{index}" in existing:
        index += 1
    return f"{desired_name}-{index}"


def _reference_name(root: Path) -> str:
    if root.name.startswith(".") and len(root.name) > 1:
        return root.name[1:]
    return root.name
