# Documentation Site

`serve` and `build-site` render the knowledge repo as a documentation website. Both go through a swappable `SiteProvider` seam (`server/site.py`); the only implementation today is `MkDocsSiteProvider`. A future FastAPI + React frontend can replace it without touching the CLI or engine.

## How it works

On each invocation Akashic writes a generated MkDocs config to `.akashic/cache/site/mkdocs.yml`, then shells out to `mkdocs`. Key generated settings:

- `docs_dir` = the knowledge repo root (the site reads Markdown directly from the repo — no copy step).
- `exclude_docs` = `tests/`, `src/`, `pyproject.toml`, `uv.lock` (so tooling files don't appear as pages).
- Theme: **Material**, with `navigation.instant`, `navigation.sections`, `search.suggest`.
- Plugins: `search`.
- Markdown extensions: `admonition`, `tables`, `toc`, and `pymdownx.superfences` configured with a **mermaid** custom fence.
- `nav` is generated automatically: `Home` (from `README.md`) plus a section per directory (`services`, `flows`, `system`, `entities`, `adr`, `glossary`) containing its `*.md` files, titled from the filename (dashes → spaces, title-cased).

## `akashic serve`

```bash
akashic serve
# -> Serving Akashic site on http://127.0.0.1:6969
```

Runs `mkdocs serve` bound to `127.0.0.1:<site.port>` (default `6969`, configurable in `config.yaml`). Blocks until stopped (Ctrl-C). Live-reloads as you edit Markdown in your own editor — that is the intended editing workflow (in-browser editing is out of scope).

## `akashic build-site`

```bash
akashic build-site
# -> Built site at /…/knowledge/dist
```

Runs `mkdocs build` into `dist/` at the repo root — a static bundle deployable to GitHub Pages, Netlify, Cloudflare Pages, etc.

> Tip: `dist/` is **not** currently in `.gitignore`. Add it yourself if you don't want the built site committed.

## Mermaid

Fenced ` ```mermaid ` blocks render as diagrams via the configured `pymdownx.superfences` custom fence.

## Errors

If `mkdocs` is not found on `PATH`, both commands raise: `… 'mkdocs' executable not found on PATH. Please ensure MkDocs is installed.` A failed build reports `mkdocs exited with status <n>`.
