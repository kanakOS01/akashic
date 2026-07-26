# Akashic Usage Documentation

Akashic is a local-first CLI that builds a **Git-backed knowledge repository** of structured Markdown for a set of source repositories. It does not understand code itself — it composes a prompt and hands generation off to a coding agent (Claude Code or Codex).

This directory documents how to install, configure, and operate the CLI as it is built today.

## Documentation map

| Page | Contents |
|------|----------|
| [installation.md](installation.md) | Requirements, install, verifying the CLI |
| [quickstart.md](quickstart.md) | End-to-end: init → attach → generate → serve |
| [commands.md](commands.md) | Every command, arguments, options, output |
| [configuration.md](configuration.md) | `config.yaml`, `config.local.yaml`, every field + default |
| [generation.md](generation.md) | Prompt system, providers, HUMAN sections, frontmatter |
| [site.md](site.md) | `serve` and `build-site` (React/Vite site) |
| [troubleshooting.md](troubleshooting.md) | `doctor`, common errors |

## Mental model

```
akashic init      ->  scaffold a Git knowledge repo (services/ flows/ system/ adr/ entities/ glossary/)
akashic attach    ->  register a source repo (path stored per-machine, name committed)
akashic generate  ->  compose a master prompt + run the configured agent, which writes docs
akashic serve     ->  browse the docs locally via the React site
akashic build-site->  compile the docs to dist/
akashic doctor    ->  validate setup
akashic status    ->  show repos, last generation, pending changes, doc counts
```

## Real agent execution

With `agent.provider: claude` or `codex`, `generate` runs the real agent CLI as an interactive child process (inherited stdio) and waits for it to exit — see [generation.md](generation.md#execution-status). Use `agent.provider: fake` for deterministic, non-interactive runs (tests, CI, exercising the pipeline without a real agent).
