# Quickstart

End-to-end walkthrough. Assumes `akashic` is installed and on `PATH` (see [installation.md](installation.md)).

## 1. Initialize a knowledge repository

```bash
mkdir knowledge && cd knowledge
akashic init
# -> Initialized Akashic repository at /Users/alice/knowledge
```

This creates the section directories (`services/ flows/ system/ adr/ entities/ glossary/`), a `README.md`, `.akashic/` (with `cache/` and `logs/`), a `.gitignore`, runs `git init`, and makes an empty initial commit. Re-running is safe.
By default, `akashic init` initializes the current directory. The absolute path
to that knowledge base is stored as a reference in the global registry under
`~/.akashic/knowledge-bases.yaml`, so installed skills can discover it later.

All later commands can run from anywhere **inside** this repo — Akashic walks up to find `.akashic/config.yaml`.

## 2. Attach source repositories

From inside a source repo, or by path:

```bash
akashic attach /Users/alice/code/bookings
akashic attach /Users/alice/code/payments --name billing
akashic attach .            # attach the current directory
```

Each target must be a Git repository. The name (committed to `config.yaml`) defaults to the directory basename; the absolute path is stored per-machine in the gitignored `config.local.yaml`.

```bash
akashic list
# billing    /Users/alice/code/payments
# bookings   /Users/alice/code/bookings
```

## 3. Generate documentation

With the default `codex` provider (or `claude`), `generate` runs your agent CLI as an interactive session — it takes over the terminal, you approve permissions live, and it exits back to Akashic when done. See [generation.md](generation.md#execution-status).

```bash
akashic generate
# Changed files:
# - services/bookings/purpose.md
# - ...
# State written: /…/knowledge/.akashic/cache/state.json
```

To exercise the pipeline deterministically (tests, CI, no real agent), set `agent.provider: fake` in `.akashic/config.yaml`:

```bash
akashic generate
# Changed files:
# - system/fake-provider.md
# State written: /…/knowledge/.akashic/cache/state.json
```

`generate` performs no Git commit — review and commit yourself:

```bash
git add -A && git commit -m "Generate knowledge docs"
```

## 4. Browse the docs

```bash
akashic serve
# -> Serving Akashic site on http://127.0.0.1:6969
```

## 5. Build a static site

```bash
akashic build-site
# -> Built site at /…/knowledge/dist
```

## 6. Inspect state

```bash
akashic status     # repos, last generation, pending changes, per-section doc counts
akashic doctor     # validate config, git, repos, agent, writability
```
