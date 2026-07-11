from __future__ import annotations

from pathlib import Path

import typer

from akashic import __version__
from akashic.engine.init import init_workspace
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
