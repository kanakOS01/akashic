# Installation

## Requirements

- **Python** 3.10 or newer.
- **Git** on `PATH` (used for `init`, `attach` validation, change detection, and `status`/`doctor`).
- **A coding agent CLI** on `PATH` for real generation — `claude` (Claude Code) or `codex` (Codex). Optional until you run `generate` against a real provider.
- **MkDocs** (installed automatically as a dependency) for `serve` / `build-site`.

## Install

The project uses a standard `pyproject.toml` (Hatchling build backend) and declares the console script `akashic`.

With [uv](https://docs.astral.sh/uv/) (used by the repo, `uv.lock` present):

```bash
uv sync                 # install project + locked dependencies
uv run akashic --version
```

Editable install with pip / pipx:

```bash
pip install -e ".[dev]"     # includes pytest
# or, once published / for isolated global use:
pipx install .
```

Runtime dependencies (from `pyproject.toml`): `mkdocs`, `mkdocs-material`, `pydantic>=2`, `pymdown-extensions`, `PyYAML`, `typer`.

## Verify

```bash
akashic --version        # prints the package version (e.g. 0.1.0)
akashic --help           # lists all commands
```

## Run the tests

```bash
uv run pytest -q         # 46 tests, all under tests/
```
