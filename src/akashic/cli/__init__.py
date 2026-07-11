from __future__ import annotations

from pathlib import Path

import typer

from akashic import __version__
from akashic.engine.init import init_workspace
from akashic.engine.repositories import (
    RepositoryError,
    attach_repository,
    detach_repository,
    list_repositories,
)
from akashic.engine.workspace import WorkspaceNotFoundError, discover_workspace

app = typer.Typer(
    add_completion=False,
    help="Akashic knowledge repository CLI.",
)


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


def _workspace(ctx: typer.Context):
    knowledge = ctx.obj.get("knowledge") if ctx.obj else None
    try:
        return discover_workspace(knowledge=knowledge)
    except WorkspaceNotFoundError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
