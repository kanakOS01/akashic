# Akashic CLI Specification (MVP)

## Overview

Akashic is a **local-first CLI** that helps engineering teams build and maintain an AI-friendly knowledge repository for distributed codebases.

Rather than indexing code into a proprietary backend, Akashic generates a **Git-backed knowledge repository** consisting of structured Markdown documentation. This repository serves as the shared knowledge layer for both humans and AI coding agents.

Akashic itself is **not** responsible for understanding code. Instead, it orchestrates coding agents (Claude Code, Codex, etc.) to analyze repositories and generate documentation using standardized prompts and templates.

The generated knowledge can then be:

* browsed by engineers
* edited by humans
* committed to Git
* consumed by AI agents
* rendered as a documentation website

---

# Design Principles

## Git First

The knowledge repository is a normal Git repository.

No proprietary storage.

No hidden database.

Everything important lives in Git.

---

## Local First

Everything should work on a developer's machine.

No cloud services are required.

No Akashic backend is required.

---

## Agent First

Akashic does not replace coding agents.

It extends them.

Claude Code, Codex and future agent harnesses become the "documentation authors."

---

## Human Editable

Generated documentation should never prevent engineers from adding manual knowledge.

Manual edits must survive regeneration.

---

## Incremental

Akashic should eventually support updating only changed repositories, but the MVP may regenerate everything.

---

# Repository Structure

After initialization, the user has a normal Git repository dedicated to engineering knowledge.

```
knowledge/

├── .akashic/
│   ├── config.yaml
│   ├── cache/
│   └── logs/
│
├── services/
│
├── flows/
│
├── system/
│
├── adr/
│
├── entities/
│
├── glossary/
│
└── README.md
```

The user's source repositories may live anywhere on disk.

Example

```
~/code/

    bookings/

    payments/

    auth/

    knowledge/
```

Akashic never requires repositories to be moved.

---

# Configuration

Configuration is stored in

```
knowledge/.akashic/config.yaml
```

Example

```yaml
version: 1

knowledge:
  path: .

repositories:

  - name: bookings
    path: /Users/alice/code/bookings

  - name: payments
    path: /Users/alice/code/payments

  - name: auth
    path: /Users/alice/code/auth

agent:

  provider: claude-code

site:

  port: 3000

generation:

  parallel: true

sync:

  enabled: false
```

---

# CLI Commands

## akashic init

Initializes a knowledge repository.

Creates

```
knowledge/

    .akashic/

    services/

    flows/

    system/

    adr/

    entities/

    glossary/

    README.md
```

The command should never modify source repositories.

---

## akashic attach

Registers an existing repository with Akashic.

Usage

```
akashic attach
```

Registers the current directory.

Or

```
akashic attach /path/to/repository
```

Behavior

* validates the directory is a Git repository
* discovers repository name
* stores its path in config
* avoids duplicates

No documentation is generated.

---

## akashic detach

Removes a repository from configuration.

```
akashic detach payments
```

No repositories are deleted.

---

## akashic list

Displays all attached repositories.

Example

```
Repositories

✓ bookings
✓ payments
✓ auth
```

---

## akashic generate

Primary command.

Pipeline

```
Read configuration

↓

Load repositories

↓

Generate prompts

↓

Invoke coding agent

↓

Collect generated documents

↓

Merge human edits

↓

Write markdown
```

No Git commits are performed.
Human edits are not neede for v0 of the docs in the mvp

---

## akashic sync

Runs

```
Pull repositories

↓

Generate

↓

Commit knowledge repo

↓

Push
```

Future versions may support incremental updates.

---

## akashic serve

Runs a local documentation server.

Example

```
http://localhost:3000
```

Features

* navigation
* search
* markdown rendering
* Mermaid support
* edit pages
* commit edits

---

## akashic build-site

Compiles documentation into a static website.

Output

```
dist/
```

Deployable to GitHub Pages, Netlify, Cloudflare Pages, etc.

---

## akashic doctor

Validates

* configuration
* repository paths
* Git
* coding agent installation
* writable knowledge repository

---

## akashic status

Displays

* attached repositories
* last generation time
* pending changes
* documentation statistics

---

# Knowledge Layout

```
knowledge/

services/

flows/

system/

adr/

entities/

glossary/
```

---

## services/

One directory per service.

Example

```
services/

payments/

orders/

membership/
```

Each service contains

```
purpose.md

architecture.md

contracts.md

workflows.md
```

---

## flows/

End-to-end business workflows.

Examples

```
checkout.md

customer-login.md

payment-reconciliation.md
```

---

## adr/

Architecture Decision Records.

Examples

```
ADR-001-dual-write.md

ADR-002-nginx-auth-request.md
```

---

## entities/

Business entities.

Examples

```
Order.md

Coupon.md

Membership.md

Clinic.md
```

---

## glossary/

Shared terminology.

---

## system/

Cross-cutting documentation.

Examples

```
service-map.md

interactions.md

shared-stores.md
```

---

# Document Format

Every generated document begins with frontmatter.

Example

```yaml
---
generated: true

service: payments

sources:
  - /Users/alice/code/payments

updated_at: ...

generator: akashic
---
```

---

# Human Editing

Generated pages reserve a section for manual content.

Example

```markdown
# Payments

...

<!-- HUMAN START -->

Manual documentation goes here.

<!-- HUMAN END -->
```

During regeneration

* generated sections are replaced
* human sections are preserved

---

# Generation Pipeline

```
Repositories

↓

Prompt Builder

↓

Coding Agent

↓

Markdown

↓

Merge Engine

↓

Knowledge Repository
```

Akashic never asks the LLM directly.

It delegates generation to the configured coding agent.

---

# Agent Abstraction

Akashic should expose a provider interface.

```
AgentProvider

generate()

is_available()

version()
```

Initial providers

* Claude Code
* Codex

Future

* Gemini CLI
* OpenAI Responses
* Custom providers

this should call smthgn like claude code cli and inject a prompt into it and the configs needed along with skill markdown for geenrateion
---

# Prompt Library

Akashic ships with prompt templates.

Examples

```
generate_service.md

generate_flow.md

generate_system.md

generate_entity.md

generate_adr.md
```

Users may override prompts via

```
.akashic/custom-prompts/
```

---

# Static Site

The generated documentation should be viewable through a lightweight local web application.

Features

* sidebar navigation
* search
* Markdown rendering
* Mermaid diagrams
* WYSIWYG editing
* Git history
* responsive UI

The site reads directly from the Git repository.

---

# Synchronization

## Manual

```
akashic generate
```

---

## Scheduled (Future)

Users configure a schedule.

Akashic generates platform-specific configuration for:

* cron (Linux)
* launchd (macOS)
* Task Scheduler (Windows)

The user installs the generated configuration.

Akashic does not silently create system jobs.

---

## Event-Based (Future)

Support repository updates via:

* GitHub webhooks
* GitLab webhooks
* local file watching
* GitHub App integration

---

# Internal Components

```
CLI

↓

Workspace Manager

↓

Repository Manager

↓

Prompt Builder

↓

Agent Provider

↓

Merge Engine

↓

Knowledge Writer

↓

Static Site
```

Each component has a single responsibility.

---

# Out of Scope (MVP)

* Cloud backend
* Authentication
* Multi-user collaboration
* Knowledge graph
* Vector databases
* Semantic search
* MCP server
* Incremental dependency graph
* Automatic architecture diagrams
* IDE extensions

These are future additions once the core Git-backed workflow is validated.

---

# Success Criteria

A successful MVP allows a developer to:

1. Initialize a knowledge repository.
2. Register existing source repositories without moving them.
3. Generate structured documentation using their preferred coding agent.
4. Preserve manual edits across regenerations.
5. Browse and edit the documentation locally.
6. Store the entire knowledge base in Git with complete version history.

If those six capabilities work reliably, Akashic provides a practical foundation for future features such as MCP integration, semantic retrieval, impact analysis, and AI-assisted cross-repository development.
