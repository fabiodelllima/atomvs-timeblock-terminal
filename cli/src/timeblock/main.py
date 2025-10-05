"""Entry point for TimeBlock CLI."""

import typer
from rich.console import Console

from .commands import init as init_cmd

app = typer.Typer(
    name="timeblock",
    help="TimeBlock Organizer - Time blocking & timesheet tracker",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Show version information."""
    from . import __version__

    console.print(f"[bold green]TimeBlock v{__version__}[/bold green]")


@app.command()
def init():
    """Initialize database and create tables."""
    init_cmd.init()


if __name__ == "__main__":
    app()
