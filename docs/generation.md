# Generation

`akashic generate` composes a single **master prompt** and hands it to a coding agent, which is responsible for reading the attached source repositories and writing Markdown docs into the knowledge repo.

## Execution status

`ClaudeProvider` and `CodexProvider` build the invocation (command, `cwd`, readable/writable roots) and then run it: `subprocess.run(command, cwd=cwd)` with no stdio redirection, so the child inherits the parent's stdin/stdout/stderr — the interactive session runs directly in the user's terminal, permission prompts and all, and Akashic blocks until it exits. The process's real exit code feeds the success check below.

If the configured binary isn't on `PATH`, `generate` fails fast with `Agent binary '<bin>' not found on PATH.` instead of spawning anything.

The `fake` provider still runs the pipeline end-to-end without a real agent: it records the prompt and writes `system/fake-provider.md`. Use it for deterministic tests and for exercising everything except the live agent call.

## Pipeline

1. **Resolve repos** — merge `config.yaml` names with `config.local.yaml` paths. Skip (with a warning) any repo whose path is missing or does not exist. Abort if none remain.
2. **Build the master prompt** — see below.
3. **Invoke the provider** — `provider_from_config(agent)` returns `ClaudeProvider` / `CodexProvider` / `FakeProvider`.
4. **Detect changes** — `git status --porcelain --untracked-files=all`, ignoring anything under `.akashic/`.
5. **Write state** — `.akashic/cache/state.json` with `timestamp`, `provider`, `repos`, `duration`.

No commit is made.

## The master prompt

Built by `prompt_builder` from six templates. The master template (`master.md`) is filled by `string.Template.safe_substitute` with these sections:

- **`$repository_list`** — the valid attached repos as `- <name>: <path>` lines.
- **`$knowledge_layout`** — the knowledge root plus a description of each section directory.
- **`$human_preservation_rules`** — instructions to preserve HUMAN blocks (below).
- **`$frontmatter_contract`** — required frontmatter fields (below).
- **`$doc_type_templates`** — the five doc-type templates concatenated.

### Templates and overrides

Bundled templates ship in the package (`akashic/prompts/`):

```
master.md
generate_service.md
generate_flow.md
generate_system.md
generate_entity.md
generate_adr.md
```

Override any of them by dropping a file with the **same name** into `.akashic/custom-prompts/` in your knowledge repo. Present files win; absent ones fall back to the bundled version.

> Note: there is no `generate_glossary.md` template. Glossary generation is guided only by the knowledge-layout section, not a dedicated doc-type template.

## HUMAN sections

Generated files are expected to carry a preserved block delimited by:

```markdown
<!-- HUMAN:START -->
Your manual notes here — never rewritten by regeneration.
<!-- HUMAN:END -->
```

The prompt instructs the agent to keep everything between these markers verbatim and to add generated content only outside them. Preservation is the agent's responsibility (there is no separate deterministic merge step).

## Frontmatter contract

The prompt requires every generated Markdown file to begin with YAML frontmatter:

```yaml
---
title: <human-readable title>
type: <service | flow | system | entity | adr>
source_repositories: [<attached repo names used>]
generated_at: <ISO-8601 timestamp>
akashic_version: <prompt/config contract version>
---
```

## Interactive session

Providers run the agent in an interactive seeded session:

- **Claude:** `claude "<prompt>" --add-dir <repo> …`, `cwd` = knowledge root. Source repos are readable roots; the knowledge root is the writable root.
- **Codex:** `codex "<prompt>"`, `cwd` = knowledge root, with source repos exposed read-side and the knowledge root write-side.

The user approves permissions live; Akashic decides success afterwards from the Git diff.

## Known limitations

- **Source-repo write protection is not hard-enforced.** Exposing a source repo to the agent (`--add-dir` for Claude, the sandbox's readable roots for Codex) grants the agent's file-writing tools access to that directory too. "Never modify source repositories" rests on the prompt's instructions (write only under the knowledge repo) plus the user approving permissions live in the interactive session — Akashic does not sandbox or block writes outside the knowledge root in v1. Generate against clean/committed source trees so any unintended write is easy to spot and revert. Hard per-directory write scoping is a candidate for a future headless runner.
