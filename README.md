# Akashic

Akashic is a local-first CLI for Git-backed knowledge repositories. It helps
teams keep structured Markdown documentation beside real source repositories,
then browse that documentation through a local web UI.

Akashic does not analyze code by itself. It manages the knowledge repo,
discovers attached source repos, builds generation prompts, and hands those
prompts to an agent provider such as Codex or Claude.

## Features

- Initialize a Git-backed knowledge repository.
- Attach one or more local Git source repositories.
- Generate structured docs for services, flows, system notes, ADRs, entities,
  and glossary entries.
- Preserve hand-written content through `<!-- HUMAN:START -->` sections.
- Serve docs through a local React/Vite site.
- Build a static read-only docs site.
- Validate setup with `doctor` and inspect repo state with `status`.

## Installation

Akashic is a Python package targeting Python 3.10+.

For local development:

```bash
uv sync
uv run akashic --version
```

If installing from a checkout:

```bash
pip install .
akashic --version
```

The documentation site commands also require Node.js and npm.

## Quickstart

Create a knowledge repository:

```bash
mkdir knowledge
cd knowledge
akashic init
```

Attach source repositories:

```bash
akashic attach /path/to/source-repo
akashic attach /path/to/another-repo --name billing
akashic list
```

Generate docs:

```bash
akashic generate
```

Review changes, then commit them yourself:

```bash
git status
git add -A
git commit -m "Generate knowledge docs"
```

Browse docs locally:

```bash
akashic serve
```

Build a static site:

```bash
akashic build-site
```

## Commands

| Command | Purpose |
| --- | --- |
| `akashic init [PATH]` | Initialize a knowledge repo. |
| `akashic root` | Print discovered knowledge repo root. |
| `akashic attach [PATH] [--name NAME]` | Register a source Git repo. |
| `akashic detach NAME` | Remove an attached source repo. |
| `akashic list` | List attached source repos. |
| `akashic generate` | Compose prompts and run configured provider. |
| `akashic serve` | Start local docs site. |
| `akashic build-site` | Build static docs site. |
| `akashic doctor` | Validate config, Git, repos, provider, and runtime. |
| `akashic status` | Show attached repos, generation state, and doc counts. |

Global options:

- `--version`: print package version.
- `--knowledge <dir>`: use a specific knowledge repo instead of discovering one.

## Configuration

Akashic stores shared repo configuration in `.akashic/config.yaml` and
machine-local absolute paths in `.akashic/config.local.yaml`. The local config
is gitignored so the knowledge repo can be shared across machines.

Workspace discovery order:

1. `--knowledge <dir>`
2. `AKASHIC_HOME`
3. Parent directory walk from the current working directory

## Documentation

Full docs live in [`docs/README.md`](docs/README.md):

- [`docs/installation.md`](docs/installation.md)
- [`docs/quickstart.md`](docs/quickstart.md)
- [`docs/commands.md`](docs/commands.md)
- [`docs/configuration.md`](docs/configuration.md)
- [`docs/generation.md`](docs/generation.md)
- [`docs/site.md`](docs/site.md)
- [`docs/troubleshooting.md`](docs/troubleshooting.md)

## Development

Run tests:

```bash
uv run pytest
```

Run focused CLI commands from the checkout:

```bash
uv run akashic doctor --knowledge /path/to/knowledge
```

Frontend sources live under `frontend/` and are packaged into the Python wheel.

## Current status

The built-in `fake` provider writes files and is useful for exercising the full
pipeline. Real providers (`codex`, `claude`) are documented in
[`docs/generation.md`](docs/generation.md), including current execution
behavior and limitations.

## License

MIT. See [`LICENSE`](LICENSE).
