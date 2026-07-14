# Documentation Site

`serve` and `build-site` render the knowledge repo as a documentation website through a swappable `SiteProvider` seam (`server/site.py`). The implementation is `ViteSiteProvider`, which launches a Vite + React + TypeScript single-page app (the `frontend/` directory). The React app replaces MkDocs entirely: it gives a fully customizable UI with sidebar navigation, client-side search, Markdown/GFM/Mermaid rendering, and **in-browser editing that writes back into the knowledge repo** (plus optional Git commit).

## How it works

`serve` and `build-site` share one data-source abstraction:

- **Live mode (`serve` / Vite dev server):** a Vite plugin (`vite-plugin-akashic.ts`) registers a small JSON API on the dev server, reading and writing the knowledge repo passed via `AKASHIC_KB_ROOT`. The React app fetches `/api/*` for nav, documents, saves, and commits.
- **Static mode (`build-site`):** at build time the same plugin embeds the nav + all document bodies into a virtual module. `dist/` is then a fully static bundle (no runtime filesystem access). The editor and commit controls are disabled in this mode.

### Dev API contract

All routes are under `/api` and JSON-encoded. Paths are relative to the knowledge root and are guarded against traversal outside it.

| Method | Route | Returns |
|--------|-------|---------|
| `GET` | `/api/meta` | `{ mode:"live", editable:true, gitAvailable, kbRoot, port }` |
| `GET` | `/api/nav` | `{ home, sections, index }` — sections: `services, flows, system, entities, adr, glossary` |
| `GET` | `/api/doc?path=<rel>` | `{ path, title, type, frontmatter, content, raw }` (400 outside root, 404 missing) |
| `PUT` | `/api/doc` | body `{ path, raw }` writes the file, returns `{ path, updated }` |
| `POST` | `/api/commit` | body `{ paths, message? }` runs `git add <paths> && git commit` |

## `akashic serve`

```bash
akashic serve
# -> Serving Akashic site on http://127.0.0.1:6969
```

Launches the Vite dev server bound to `127.0.0.1:<site.port>` (default `6969`, configurable in `config.yaml`). It first installs frontend dependencies (`npm install`) in `frontend/` if `node_modules` is missing, then runs `npm run dev`. Blocks until stopped (Ctrl-C).

- **Live editing:** open any document, click **Edit**, change the Markdown (including frontmatter), then **Save** to write the file back into the knowledge repo, or **Commit** to stage and commit it via Git.
- Editing in your own editor also works — the site reads from the repo directly, so a refresh reflects external changes.

## `akashic build-site`

```bash
akashic build-site
# -> Built site at /…/knowledge/dist
```

Builds the React app into `dist/` at the repo root — a static bundle deployable to GitHub Pages, Netlify, Cloudflare Pages, etc. A `404.html` copy of `index.html` is written for SPA deep-link refresh (GitHub Pages). In this mode the embedded snapshot is read-only, so the editor/commit controls are hidden.

> Tip: `dist/` is **not** in `.gitignore`. Add it yourself if you don't want the built site committed.

## Mermaid

Fenced ` ```mermaid ` blocks render as diagrams client-side via the `mermaid` library.

## Requirements / errors

`serve` / `build-site` require **Node.js and npm** on `PATH`. If missing, `doctor` flags a **Node Runtime** failure and the commands raise: `… Node.js not found on PATH. …` / `… npm not found on PATH. …`. A failed frontend build reports `npm build exited with status <n>`.
