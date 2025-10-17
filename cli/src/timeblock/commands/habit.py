"""Comandos para gerenciar hábitos."""

from datetime import time as dt_time

import typer
from rich.console import Console
from rich.table import Table

from src.timeblock.models import Recurrence
from src.timeblock.services.habit_service import HabitService

app = typer.Typer(help="Gerenciar hábitos")
console = Console()


@app.command("create")
def create_habit(
    routine_id: int = typer.Argument(..., help="ID da rotina"),
    title: str = typer.Option(..., "--title", "-t", help="Título do hábito"),
    start: str = typer.Option(..., "--start", "-s", help="Hora início (HH:MM)"),
    end: str = typer.Option(..., "--end", "-e", help="Hora fim (HH:MM)"),
    recurrence: str = typer.Option(..., "--recurrence", "-r", help="Padrão de recorrência"),
    color: str = typer.Option(None, "--color", "-c", help="Cor do hábito"),
):
    """Cria um novo hábito."""
    try:
        # Parse times
        start_time = dt_time.fromisoformat(start)
        end_time = dt_time.fromisoformat(end)

        # Parse recurrence
        rec = Recurrence(recurrence.lower())

        habit = HabitService.create_habit(
            routine_id=routine_id,
            title=title,
            scheduled_start=start_time,
            scheduled_end=end_time,
            recurrence=rec,
            color=color,
        )

        console.print(
            f"✓ Hábito criado: [bold]{habit.title}[/bold] (ID: {habit.id})", style="green"
        )
    except (ValueError, KeyError) as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("list")
def list_habits(routine_id: int = typer.Option(None, "--routine", "-r", help="Filtrar por rotina")):
    """Lista hábitos."""
    habits = HabitService.list_habits(routine_id)

    if not habits:
        console.print("Nenhum hábito encontrado.", style="yellow")
        return

    table = Table(title="Hábitos")
    table.add_column("ID", style="cyan")
    table.add_column("Rotina ID", style="magenta")
    table.add_column("Título", style="white")
    table.add_column("Horário", style="blue")
    table.add_column("Recorrência", style="green")

    for h in habits:
        table.add_row(
            str(h.id),
            str(h.routine_id),
            h.title,
            f"{h.scheduled_start.strftime('%H:%M')} → {h.scheduled_end.strftime('%H:%M')}",
            h.recurrence.value,
        )

    console.print(table)


@app.command("update")
def update_habit(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    title: str = typer.Option(None, "--title", "-t", help="Novo título"),
    start: str = typer.Option(None, "--start", "-s", help="Nova hora início (HH:MM)"),
    end: str = typer.Option(None, "--end", "-e", help="Nova hora fim (HH:MM)"),
    recurrence: str = typer.Option(None, "--recurrence", "-r", help="Nova recorrência"),
    color: str = typer.Option(None, "--color", "-c", help="Nova cor"),
):
    """Atualiza um hábito."""
    try:
        updates = {}
        if title:
            updates["title"] = title
        if start:
            updates["scheduled_start"] = dt_time.fromisoformat(start)
        if end:
            updates["scheduled_end"] = dt_time.fromisoformat(end)
        if recurrence:
            updates["recurrence"] = Recurrence(recurrence.lower())
        if color:
            updates["color"] = color

        if not updates:
            console.print("Nenhuma atualização especificada.", style="yellow")
            return

        habit = HabitService.update_habit(habit_id, **updates)
        console.print(f"✓ Hábito {habit.id} atualizado", style="green")
    except (ValueError, KeyError) as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("delete")
def delete_habit(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    force: bool = typer.Option(False, "--force", "-f", help="Não pedir confirmação"),
):
    """Deleta um hábito."""
    if not force:
        confirm = typer.confirm(f"Deletar hábito {habit_id}?")
        if not confirm:
            console.print("Cancelado.", style="yellow")
            return

    try:
        HabitService.delete_habit(habit_id)
        console.print(f"✓ Hábito {habit_id} deletado", style="green")
    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)
