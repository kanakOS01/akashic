# Akashic

Akashic is a **local-first, Git-backed CLI** that turns a set of source repositories into a shared knowledge base for engineers *and* AI coding agents.

It doesn't understand your code itself. Instead, it scaffolds a plain Git repository of structured Markdown (`services/`, `flows/`, `system/`, `adr/`, `entities/`, `glossary/`), then hands the job of *writing* that documentation to a coding agent you already use (Claude Code or Codex). Everything lives in Git — no proprietary index, no hidden database, no cloud backend.

```
akashic init      ->  scaffold a Git knowledge repo
akashic attach    ->  register a source repo (without moving it)
akashic generate  ->  compose a prompt + run your agent, which writes the docs
akashic serve     ->  browse the docs locally (React site, live editing)
akashic build-site->  compile the docs to a static dist/
akashic doctor    ->  validate the setup
akashic status    ->  repos, last generation, pending changes, doc counts
akashic add skill ->  install an Akashic-aware skill into Claude Code / Codex
```

## Why

Engineering knowledge usually lives in people's heads, scattered wikis, and stale docs. When an AI agent (or a new engineer) needs to understand how services fit together, what a business entity means, or why a decision was made, there's nothing authoritative to read. Akashic gives you a knowledge base that:

- lives in plain Git — browsable, diffable, versioned, mergeable,
- works entirely on your machine — no cloud, no Akashic backend,
- is authored by the coding agent you already use, not a bespoke code-understanding engine,
- never requires moving your source repositories,
- preserves anything you write by hand across regeneration.

## Requirements

- **Python** 3.10+
- **Git** on `PATH`
- **A coding agent CLI** on `PATH` for real generation — `claude` (Claude Code) or `codex` (Codex)
- **Node.js + npm** on `PATH` for `serve` / `build-site` (the bundled React site); Akashic installs its frontend dependencies automatically on first use

## Install

With [uv](https://docs.astral.sh/uv/) (this repo ships a `uv.lock`):

```bash
uv sync
uv run akashic --version
```

Editable install with pip / pipx:

```bash
pip install -e ".[dev]"     # includes pytest
# or, for an isolated global install:
pipx install .
```

Verify:

```bash
akashic --version
akashic --help
```

## Quickstart

```bash
# 1. Initialize a knowledge repository
mkdir knowledge && cd knowledge
akashic init
# -> Initialized Akashic repository at /Users/you/knowledge

# 2. Attach the source repositories you want documented (paths aren't moved)
akashic attach /path/to/bookings
akashic attach /path/to/payments --name billing
akashic list

# 3. Generate documentation via your configured agent
akashic generate
# -> Changed files: ...
# -> State written: .akashic/cache/state.json
git add -A && git commit -m "Generate knowledge docs"   # generate never commits for you

# 4. Browse it
akashic serve
# -> Serving Akashic site on http://127.0.0.1:6969

# 5. Or ship it as a static site
akashic build-site
# -> Built site at ./dist
```

Run commands from anywhere inside the knowledge repo — Akashic walks up to find `.akashic/config.yaml`, the same way Git finds `.git`.

## Using it with Claude Code / Codex

```bash
akashic add skill --to claude   # or --to codex
```

This installs an Akashic-aware skill into `~/.claude/skills/akashic/` (or `~/.codex/skills/akashic/`) that teaches the agent how to discover your registered knowledge bases (via `~/.akashic/knowledge-bases.yaml`) and navigate their folder structure before answering questions about your systems. Every knowledge repo created with `akashic init` is registered there automatically; see `akashic bases` to list them.

## Configuration

Two files under `.akashic/` in each knowledge repo:

- **`config.yaml`** — committed. Repo names, agent provider, site port, generation settings.
- **`config.local.yaml`** — gitignored. Per-machine `name → absolute path` for attached repos, so teammates can clone the knowledge repo and set their own local paths without touching the shared config.

See [`docs/configuration.md`](docs/configuration.md) for the full field reference.

## Documentation

The [`docs/`](docs/) directory has the full reference:

| Page | Contents |
|------|----------|
| [installation.md](docs/installation.md) | Requirements, install, verifying the CLI |
| [quickstart.md](docs/quickstart.md) | End-to-end walkthrough |
| [commands.md](docs/commands.md) | Every command, arguments, options, output |
| [configuration.md](docs/configuration.md) | `config.yaml`, `config.local.yaml`, every field |
| [generation.md](docs/generation.md) | Prompt system, providers, HUMAN sections, frontmatter |
| [site.md](docs/site.md) | `serve` and `build-site` (the React site) |
| [troubleshooting.md](docs/troubleshooting.md) | `doctor`, common errors |

## Development

```bash
uv sync
uv run pytest -q
```
