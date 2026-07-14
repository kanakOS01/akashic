# Configuration

Akashic also keeps a per-user registry at `~/.akashic/config.yaml`. This file is
created/updated only by `akashic init` and lets installed agent skills resolve a
knowledge base name to its local path:

```yaml
knowledge_bases:
  knowledge:
    path: /Users/alice/docs/knowledge
```

If two initialized knowledge repos have the same directory basename, Akashic
registers the later one with a numeric suffix such as `knowledge-2`.

Akashic uses **two** config files under `.akashic/`:

| File | Committed? | Purpose |
|------|-----------|---------|
| `config.yaml` | Yes | Portable settings: repo names, agent, site, generation. |
| `config.local.yaml` | No (gitignored) | Per-machine `name → absolute path` mapping for attached repos. |

This split keeps machine-specific absolute paths out of Git, so a teammate can clone the knowledge repo and set their own paths (via `akashic attach`) without breaking the committed config.

Both files are validated on load with `extra="forbid"` — unknown keys raise a clear error.

---

## `config.yaml`

Written by `init` with defaults. Full shape and defaults:

```yaml
version: 1

knowledge:
  path: "."          # knowledge root, relative to the repo; used in the prompt's layout section

repositories: []      # list of { name: <str>, settings: {} }; managed by attach/detach

agent:
  provider: codex      # one of: codex | claude | fake
  command: null        # optional path/name of the agent binary, overriding the default

site:
  port: 6969           # port used by `serve`

generation:
  model: null          # optional model hint (reserved; not yet wired into invocation)
```

### Field reference

- **`version`** (int, default `1`) — config contract version.
- **`knowledge.path`** (str, default `"."`) — knowledge root, surfaced in the prompt's Knowledge Layout section.
- **`repositories`** (list) — each entry `{ name, settings }`. Managed by `attach`/`detach`; edit by hand only if you know what you're doing. `settings` is reserved and currently unused.
- **`agent.provider`** (str, default `codex`) — selects the provider. `codex` and `claude` construct real agent commands (but do not execute yet — see [generation.md](generation.md#execution-status)); `fake` runs the full pipeline and writes a placeholder doc. An unknown value errors `Unknown agent provider '<x>'.`
- **`agent.command`** (str | null) — override the binary looked up on `PATH` (default `claude` or `codex`). Useful for non-standard installs.
- **`site.port`** (int, default `6969`) — bind port for `serve`.
- **`generation.model`** (str | null) — reserved model hint; not yet passed to the agent.

---

## `config.local.yaml`

Created/updated by `attach` and `detach`; gitignored. Shape:

```yaml
repositories:
  bookings: /Users/alice/code/bookings
  billing: /Users/alice/code/payments
```

If the file is absent, an empty mapping is assumed. A repo listed in `config.yaml` but missing here shows as `[missing local path]` in `list` and is skipped by `generate`.

---

## Setting up on a new machine

After cloning a knowledge repo:

```bash
akashic list            # shows attached repos as [missing local path]
akashic attach /new/machine/path/to/bookings   # re-record the local path (name preserved)
```
