"""Command-line interface for ``file-organizer``."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from rich.console import Console
from rich.table import Table

from .core import execute, plan_moves

app = typer.Typer(
    name="file-organizer",
    help="Organize the top-level files of a folder into category subfolders.",
    no_args_is_help=True,
    add_completion=False,
)

Mode = Literal["type", "date"]


def _render_plan(plans) -> None:
    console = Console()
    table = Table(title="Planned moves")
    table.add_column("Source", style="red")
    table.add_column("Destination", style="green")
    for plan in plans:
        table.add_row(str(plan.source), str(plan.destination))
    console.print(table)


@app.command()
def organize(
    path: Path = typer.Argument(..., help="Directory whose files to organize."),
    mode: Mode = typer.Option(
        "type",
        "--mode",
        "-m",
        help="Group by 'type' (extension) or 'date' (modified month).",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print the plan without moving files."
    ),
    exclude: list[str] = typer.Option(
        [], "--exclude", "-e", help="Filename to skip (repeatable)."
    ),
) -> None:
    """Move top-level files into category or month subfolders."""
    if not path.is_dir():
        typer.echo(f"Error: '{path}' is not a directory.", err=True)
        raise typer.Exit(code=1)

    try:
        plans = plan_moves(path, mode=mode, exclude=set(exclude))
    except OSError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)

    if not plans:
        typer.echo(f"No files to organize in '{path}'.")
        return

    if dry_run:
        _render_plan(plans)
        typer.echo(
            f"Dry run: {len(plans)} file(s) would be moved. "
            "Re-run without --dry-run to apply."
        )
        return

    executed = execute(plans)
    typer.echo(f"Done! Moved {len(executed)} file(s).")
