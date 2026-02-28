"""Initialize database command."""

from pathlib import Path

import typer
from rich.console import Console

from timeblock.database import create_db_and_tables, get_db_path

console = Console()


def init():
    """Initialize the database."""
    db_path = Path(get_db_path())
    if db_path.exists():
        confirm = typer.confirm(
            f"Banco de dados já existe em {db_path}. Reinicializar?",
            default=False,
        )
        if not confirm:
            console.print("[yellow]Inicialização cancelada.[/yellow]")
            raise typer.Exit()
    try:
        create_db_and_tables()
        console.print(
            f"[green]✓[/green] Banco de dados inicializado em {db_path}",
            style="bold green",
        )
    except Exception as e:
        console.print(
            f"[red]✗[/red] Erro ao inicializar banco de dados: {e}",
            style="bold red",
        )
        raise typer.Exit(code=1) from None
