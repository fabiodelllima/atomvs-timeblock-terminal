"""Entry point for TimeBlock CLI."""

import typer
from rich.console import Console

app = typer.Typer(
    help="TimeBlock Organizer - Time blocking & timesheet tracker"
)
console = Console()


@app.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"[bold green]TimeBlock v{__version__}[/bold green]")


if __name__ == "__main__":
    app()
