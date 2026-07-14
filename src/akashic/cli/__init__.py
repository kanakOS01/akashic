from __future__ import annotations

from pathlib import Path

import typer

from akashic import __version__
from akashic.engine.generate import GenerateError, run_generate
from akashic.engine.init import init_workspace
from akashic.engine.repositories import (
    RepositoryError,
    attach_repository,
    detach_repository,
    list_repositories,
)
from akashic.engine.skills import (
    UnknownSkillTargetError,
    default_target,
    install_skill,
)
from akashic.engine.workspace import WorkspaceNotFoundError, discover_workspace
from akashic.server.site import SiteError, default_site_provider

app = typer.Typer(
    add_completion=False,
    help="Akashic knowledge repository CLI.",
)

add_app = typer.Typer(add_completion=False, help="Add resources to the knowledge repository.")
app.add_typer(add_app, name="add")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    knowledge: Path | None = typer.Option(
        None,
        "--knowledge",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Knowledge repository path.",
    ),
) -> None:
    """Akashic command-line entry point."""
    ctx.obj = {"knowledge": knowledge}


@app.command()
def init(
    path: Path = typer.Argument(
        Path("."),
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Directory to initialize.",
    ),
) -> None:
    """Initialize an Akashic knowledge repository."""
    root = init_workspace(path)
    typer.echo(f"Initialized Akashic repository at {root}")


@app.command()
def root(ctx: typer.Context) -> None:
    """Print discovered Akashic repository root."""
    knowledge = ctx.obj.get("knowledge") if ctx.obj else None
    try:
        workspace = discover_workspace(knowledge=knowledge)
    except WorkspaceNotFoundError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(workspace.root)


@app.command()
def attach(
    ctx: typer.Context,
    path: Path = typer.Argument(
        Path("."),
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Source Git repository to attach.",
    ),
    name: str | None = typer.Option(None, "--name", help="Attached repository name."),
) -> None:
    """Attach a source Git repository."""
    workspace = _workspace(ctx)
    try:
        repository = attach_repository(workspace, path, name)
    except RepositoryError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Attached {repository.name}")


@app.command()
def detach(ctx: typer.Context, name: str) -> None:
    """Detach a source repository."""
    workspace = _workspace(ctx)
    removed = detach_repository(workspace, name)
    if not removed:
        raise typer.BadParameter(f"Repository '{name}' is not attached.")
    typer.echo(f"Detached {name}")
    typer.echo("Generated docs remain; remove them with git rm when ready.")


@app.command("list")
def list_command(ctx: typer.Context) -> None:
    """List attached source repositories."""
    workspace = _workspace(ctx)
    repositories = list_repositories(workspace)
    if not repositories:
        typer.echo("No repositories attached.")
        return

    for repository in repositories:
        if repository.missing_local_path:
            typer.echo(f"{repository.name}\t[missing local path]")
        elif repository.missing_target:
            typer.echo(f"{repository.name}\t{repository.path}\t[missing target]")
        else:
            typer.echo(f"{repository.name}\t{repository.path}")


@app.command()
def generate(ctx: typer.Context) -> None:
    """Generate knowledge docs from attached repositories."""
    workspace = _workspace(ctx)
    try:
        result = run_generate(workspace)
    except GenerateError as exc:
        raise typer.BadParameter(str(exc)) from exc

    for warning in result.warnings:
        typer.echo(f"Warning: {warning}", err=True)

    if result.changed_files:
        typer.echo("Changed files:")
        for path in result.changed_files:
            typer.echo(f"- {path}")
    else:
        typer.echo("Changed files: none")

    typer.echo(f"State written: {result.state_path}")


@app.command()
def serve(ctx: typer.Context) -> None:
    """Serve the knowledge repository as a documentation site."""
    workspace = _workspace(ctx)
    try:
        process = default_site_provider().serve(workspace)
    except SiteError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Serving Akashic site on http://127.0.0.1:{workspace.config.site.port}")
    process.wait()


@app.command("build-site")
def build_site(ctx: typer.Context) -> None:
    """Build the knowledge repository documentation site."""
    workspace = _workspace(ctx)
    try:
        dist = default_site_provider().build_site(workspace)
    except SiteError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Built site at {dist}")


@app.command()
def doctor(ctx: typer.Context) -> None:
    """Validate configuration, repository paths, and agent installation."""
    workspace = _workspace(ctx)
    from akashic.engine.doctor import diagnose
    results = diagnose(workspace)

    all_passed = True
    for res in results:
        status_str = "Pass" if res.passed else "Fail"
        name_map = {
            "Configuration Schema": "configuration",
            "Git Presence": "Git presence",
            "Attached Repositories": "attached repositories",
            "Agent Provider": "agent provider",
            "Writability": "writability",
            "Node Runtime": "node runtime",
        }
        display_name = name_map.get(res.name, res.name.lower())
        if res.passed:
            typer.echo(f"Checking {display_name}... {status_str} ({res.message})")
        else:
            all_passed = False
            typer.echo(f"Checking {display_name}... {status_str}")
            typer.echo(f"  Error: {res.message}")
        for detail in res.details:
            typer.echo(f"  - {detail}")

    if not all_passed:
        raise typer.Exit(code=1)


@app.command()
def status(ctx: typer.Context) -> None:
    """Show the status of attached repositories, generation, and documents."""
    workspace = _workspace(ctx)
    from akashic.engine.status import get_status
    state = get_status(workspace)

    typer.echo("Attached repositories:")
    if state.repositories:
        for name, path in state.repositories:
            if path:
                typer.echo(f"- {name} ({path})")
            else:
                typer.echo(f"- {name} (missing local path)")
    else:
        typer.echo("No repositories attached.")

    typer.echo("\nLast generation:")
    if state.last_generation:
        typer.echo(f"- Time: {state.last_generation.get('timestamp')}")
        typer.echo(f"- Provider: {state.last_generation.get('provider')}")
        repos_str = ", ".join(state.last_generation.get("repos", []))
        typer.echo(f"- Repositories: {repos_str}")
        duration = state.last_generation.get("duration")
        duration_str = f"{duration:.1f} seconds" if isinstance(duration, (int, float)) else "unknown"
        typer.echo(f"- Duration: {duration_str}")
    else:
        typer.echo("- None")

    typer.echo("\nPending changes:")
    if state.pending_changes:
        for change in state.pending_changes:
            typer.echo(f"  {change}")
    else:
        typer.echo("- None")

    typer.echo("\nDocument statistics:")
    for section, count in state.document_counts.items():
        doc_word = "document" if count == 1 else "documents"
        typer.echo(f"- {section}: {count} {doc_word}")



@add_app.command("skill")
def add_skill(
    ctx: typer.Context,
    to: str | None = typer.Option(
        None,
        "--to",
        help="Where to install the skill: 'claude' or 'codex'. Defaults to agent.provider in config.yaml.",
    ),
) -> None:
    """Generate a SKILL.md from the knowledge base and install it for Claude or Codex."""
    workspace = _workspace(ctx)

    target = to
    if target is None:
        suggested = default_target(workspace)
        prompt_text = "Add skill for which agent? [claude/codex]"
        target = typer.prompt(prompt_text, default=suggested) if suggested else typer.prompt(prompt_text)

    try:
        result = install_skill(workspace, target)
    except UnknownSkillTargetError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"Installed {result.target} skill at {result.skill_path}")


def _workspace(ctx: typer.Context):
    knowledge = ctx.obj.get("knowledge") if ctx.obj else None
    try:
        return discover_workspace(knowledge=knowledge)
    except WorkspaceNotFoundError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
