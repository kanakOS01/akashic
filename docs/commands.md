# Command Reference

Every command as implemented. Global options come **before** the subcommand.

## Global options

| Option | Description |
|--------|-------------|
| `--version` | Print the package version and exit. |
| `--knowledge <dir>` | Use this directory as the knowledge repo instead of discovering one by walking up from the current directory. Resolved to an absolute path. |

Workspace discovery order (for every command except `init`):

1. `--knowledge <dir>` if given.
2. `AKASHIC_HOME` environment variable if set.
3. Walk up from the current working directory looking for `.akashic/config.yaml`.

If none resolve, the command fails with: `No Akashic knowledge repo found from <dir>. Run 'akashic init' first or pass --knowledge.`

---

## `akashic init [PATH]`

Initialize (or top up) a knowledge repository at `PATH`. When `PATH` is omitted,
Akashic initializes the current directory.

Creates: `services/ flows/ system/ adr/ entities/ glossary/`, `.akashic/cache/`, `.akashic/logs/`, `README.md`, `.akashic/config.yaml`, `.gitignore`. Runs `git init` if not already a repo, and makes an empty initial commit if there is no `HEAD` yet.
Registers the repository in the global Akashic registry at `~/akashic/knowledge-bases.yaml` (or `$AKASHIC_GLOBAL_HOME/knowledge-bases.yaml` when set), so Claude/Codex skills can discover all local knowledge bases. The knowledge base reference is the absolute path to the knowledge base.

- **Idempotent:** existing directories, README, and config are left untouched; `.gitignore` lines are merged, not duplicated.
- The initial commit is authored as `Akashic <akashic@example.invalid>` via `-c` overrides, so it does not depend on your global Git identity.

`.gitignore` always contains: `.akashic/cache/`, `.akashic/logs/`, `.akashic/config.local.yaml`.

Output: `Initialized Akashic repository at <root>`

---

## `akashic bases`

List every knowledge repository Akashic can discover from the machine-level
registry and from knowledge base folders under the global Akashic folder.

- Registry location defaults to `~/akashic/knowledge-bases.yaml`.
- Set `AKASHIC_GLOBAL_HOME` to use a different global Akashic directory.
- Each row is tab-separated: `<reference-path>\t<name>`.

Output:
```
Registry: /Users/alice/akashic/knowledge-bases.yaml
/Users/alice/akashic/.platform    platform
/Users/alice/akashic/.payments    payments
```

---

## `akashic root`

Print the discovered knowledge repository root. Useful for scripting and for confirming discovery works from a subdirectory.

---

## `akashic attach [PATH] [--name NAME]`

Register a source Git repository. `PATH` defaults to the current directory.

- Validates `PATH` is inside a Git work tree (`git rev-parse --is-inside-work-tree`); otherwise errors `<path> is not a Git repository.`
- Name defaults to the resolved directory's basename; override with `--name`.
- **Dedupe by resolved path:** re-attaching the same path updates the entry in place (and renames it if `--name` differs).
- **Unique names:** attaching a *different* path under an already-used name errors `Repository name '<name>' is already attached.`
- Writes the name to `config.yaml` (`repositories`) and the absolute path to `config.local.yaml`.

Output: `Attached <name>`

---

## `akashic detach NAME`

Remove a repository from both `config.yaml` and `config.local.yaml`. Deletes no files.

- Unknown name errors `Repository '<name>' is not attached.`

Output:
```
Detached <name>
Generated docs remain; remove them with git rm when ready.
```

---

## `akashic list`

List attached repositories, sorted by name.

- `No repositories attached.` when empty.
- Each row is tab-separated:
  - `<name>\t<path>` — path present and exists.
  - `<name>\t[missing local path]` — no entry in `config.local.yaml` (e.g. after cloning the knowledge repo on a new machine).
  - `<name>\t<path>\t[missing target]` — path recorded but the directory no longer exists.

---

## `akashic generate`

Compose the master prompt and run the configured agent provider.

Steps:
1. Merge `config.yaml` repos with `config.local.yaml` paths. Repos with a missing/nonexistent path are **skipped with a warning**.
2. If no valid repo remains, error `No valid attached repositories found.`
3. Build the master prompt from bundled + custom templates (see [generation.md](generation.md)).
4. Invoke the provider (`agent.provider`). Detect changes via `git status --porcelain` (ignoring `.akashic/`).
5. Write `.akashic/cache/state.json` (timestamp, provider, repos, duration).

- **No Git commit or staging is performed** — changes are left in the working tree.
- Success = agent exit code 0 **and** at least one changed file. A clean exit with no changes warns: `Agent exited cleanly but produced no knowledge changes.`
- Real providers (`claude`, `codex`) run with inherited stdio, so the interactive session takes over the terminal; Akashic waits for it to exit and reads its real exit code. See [generation.md](generation.md#execution-status).

Output: warnings (to stderr), a `Changed files:` list (or `Changed files: none`), and `State written: <path>`.

---

## `akashic serve`

Start the local React documentation site (Vite dev server) reading directly from the knowledge repo. Binds `127.0.0.1:<site.port>` (default `6969`). Blocks until the server exits (Ctrl-C). Installs frontend dependencies if missing, then runs `npm run dev`. Supports in-browser editing (Save writes back to the knowledge repo; Commit stages and commits via Git). See [site.md](site.md).

Errors `… Node.js not found on PATH. …` / `… npm not found on PATH. …` if Node/npm is missing.

---

## `akashic build-site`

Compile the docs into a static `dist/` (via the Vite build). Output: `Built site at <root>/dist`. In this static mode the site is read-only (no in-browser editing).

---

## `akashic doctor`

Run six checks and print pass/fail for each: configuration schema, Git presence, attached repositories, agent provider, writability, and Node runtime. Exits with code `1` if any check fails. See [troubleshooting.md](troubleshooting.md).

---

## `akashic status`

Print: attached repositories (with paths or `missing local path`), last generation (from `state.json`, or `None`), pending Git changes (porcelain), and per-section document counts (`*.md` under each section directory).

---

## `akashic add skill [--to claude|codex]`

Install the Akashic skill into Claude Code or Codex.

The installed skill points the agent at the global Akashic folder and registry.
Each time the skill runs, it instructs the agent to read the registry, scan the
global folder for knowledge bases containing `.akashic/config.yaml`, list the
reference paths, and ask which one to use before reading docs.
