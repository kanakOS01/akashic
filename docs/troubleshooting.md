# Troubleshooting

Start with `akashic doctor`. It runs five checks and exits non-zero if any fail.

## `akashic doctor` checks

| Check | Passes when | Fails / message |
|-------|-------------|-----------------|
| **Configuration schema** | `config.yaml` (and `config.local.yaml` if present) parse and validate | `Committed config invalid: …` / `Local config invalid: …` |
| **Git presence** | `git` is on `PATH` and reports a version | `Git executable not found on PATH.` |
| **Attached repositories** | every attached repo has a local path that exists and is a Git repo | lists per-repo issues: missing mapping, path does not exist, or not a Git repo |
| **Agent provider** | the configured provider's binary is on `PATH` and `--version` works | `Agent '<name>' is not installed (command '<cmd>' not found on PATH).` |
| **Writability** | the knowledge root exists, is a directory, and a temp file can be written under `.akashic/` | `Knowledge repository … is not writable` / `Cannot write to knowledge repository: …` |
| **Node runtime** | `node` and `npm` are on `PATH` | `Node.js executable not found on PATH. …` / `npm executable not found on PATH. …` |

`doctor` writes and deletes `.akashic/doctor_write_test` as part of the writability check.

## Common problems

### Akashic skill cannot find a knowledge base name
Run `akashic init <knowledge-path>` for that knowledge repo. This creates or
updates `~/.akashic/config.yaml`, which maps knowledge base names to local paths
for installed agent skills.

### `No Akashic knowledge repo found from <dir>`
You are not inside an initialized repo. Run `akashic init`, or pass `--knowledge <dir>`, or set `AKASHIC_HOME`.

### `<path> is not a Git repository` (on attach)
The attach target must be inside a Git work tree. Run `git init` in the source repo first.

### `Repository name '<name>' is already attached`
Another path already uses that name. Pick a different `--name`, or re-attach the *same* path (which updates in place).

### `list` shows `[missing local path]`
The repo is in the committed `config.yaml` but has no entry in this machine's `config.local.yaml` (typical right after cloning the knowledge repo). Re-run `akashic attach <path>` with the same name to record the local path.

### `list` shows `[missing target]`
The recorded path no longer exists (repo moved/deleted). Re-attach the new location or `detach`.

### `generate` says `No valid attached repositories found`
Every attached repo was skipped — no local path, or the paths don't exist. Fix with `attach` / check `config.local.yaml`, or see `doctor`'s repository check.

### `generate` runs but writes nothing (`Agent exited cleanly but produced no knowledge changes`)
The agent session exited 0 but the knowledge repo has no changed files under `git status`. With `provider: codex`/`provider: claude` this means the live agent decided there was nothing to write (or you exited without producing changes); rerun and use the interactive session to have it write something. Set `provider: fake` to sanity-check the rest of the pipeline without a real agent.

### `Agent binary '<bin>' not found on PATH.`
`generate` checks availability right before spawning the process (in addition to `doctor`'s check). Install the agent CLI (`claude` or `codex`) and ensure it's on `PATH`, or set `agent.command` to its binary path in `config.yaml`, or switch `agent.provider` to `fake` for testing.

### `Agent '<name>' is not installed` (from `doctor`)
Same fix as above — `doctor`'s agent-provider check surfaces this ahead of running `generate`.

### Source repo changes unexpectedly during `generate`
Exposing a source repo to the agent (`--add-dir` / Codex readable roots) also grants its write tools access to that directory — Akashic does not hard-enforce "read-only" for source repos in v1 (see [generation.md](generation.md#known-limitations)). Review the live session's file writes as you approve permissions, and prefer generating against a clean/committed source tree so any stray write shows up in `git status` immediately.

### `serve` / `build-site`: `Node.js not found on PATH` / `npm not found on PATH`
`serve` and `build-site` launch a Vite + React site and require Node.js (with npm) on `PATH`. Install Node.js from https://nodejs.org (npm ships with it), then retry. `doctor`'s Node Runtime check surfaces this ahead of running the command.

### `serve` / `build-site`: frontend build fails (`npm build exited with status <n>`)
The `frontend/` dependencies may be missing or stale. Delete `frontend/node_modules` and let `akashic` reinstall, or run `npm install` in `frontend/` yourself, then retry.
