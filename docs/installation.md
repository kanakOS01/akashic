# Installation

## Requirements

- **Python** 3.10 or newer.
- **Git** on `PATH` (used for `init`, `attach` validation, change detection, and `status`/`doctor`).
- **A coding agent CLI** on `PATH` for real generation — `claude` (Claude Code) or `codex` (Codex). Optional until you run `generate` against a real provider.
- **Node.js + npm** on `PATH` for `serve` / `build-site` (the React site). `akashic` installs frontend dependencies automatically on first run.

## Install

The project uses a standard `pyproject.toml` (Hatchling build backend) and declares the console script `akashic`.

Install the released CLI:

```bash
uv tool install akashic-kb
# or
pipx install akashic-kb
```

The PyPI distribution is `akashic-kb`; the installed CLI command is `akashic`.

## From a checkout

With [uv](https://docs.astral.sh/uv/) (used by the repo, `uv.lock` present):

```bash
uv sync                 # install project + locked dependencies
uv run akashic --version
```

Editable install with pip / pipx:

```bash
pip install -e ".[dev]"     # includes pytest
pipx install .
```

Runtime dependencies (from `pyproject.toml`): `pydantic>=2`, `PyYAML`, `typer`. The site (`serve` / `build-site`) additionally requires Node.js + npm and the `frontend/` npm dependencies, which `akashic` installs lazily on first use.

## Verify

```bash
akashic --version        # prints the package version (e.g. 0.1.0)
akashic --help           # lists all commands
```

## Run the tests

```bash
uv run pytest -q         # 46 tests, all under tests/
```
