"""Ações pontuais para hábitos (adjust, skip)."""

from datetime import time as dt_time

import typer
from rich.console import Console
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.models.enums import SkipReason
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.utils.conflict_display import display_conflicts

console = Console()


def adjust_instance(
    instance_id: int = typer.Argument(..., help="ID da instância"),
    start: str = typer.Option(..., "--start", "-s", help="Nova hora início (HH:MM)"),
    end: str = typer.Option(..., "--end", "-e", help="Nova hora fim (HH:MM)"),
):
    """
    Ajusta horário de instância específica de hábito.

    Este comando modifica apenas a instância especificada. O hábito na rotina
    e outras instâncias permanecem inalterados.
    """
    try:
        new_start = dt_time.fromisoformat(start)
        new_end = dt_time.fromisoformat(end)

        _instance, conflicts = HabitInstanceService.adjust_instance_time(
            instance_id, new_start, new_end
        )

        console.print(f"[green]Instância {instance_id} ajustada: {new_start} - {new_end}[/green]")

        if conflicts:
            console.print("\n[yellow]Atenção: O ajuste resultou em conflitos:[/yellow]")
            display_conflicts(conflicts, console)

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


def skip_instance(
    instance_id: int = typer.Argument(..., help="ID da instância do hábito"),
    category: str = typer.Option(
        None,
        "--category",
        "-c",
        help="Categoria do skip (HEALTH|WORK|FAMILY|TRAVEL|WEATHER|LACK_RESOURCES|EMERGENCY|OTHER)",
    ),
    note: str = typer.Option(None, "--note", "-n", help="Nota opcional (máx 500 chars)"),
):
    """
    Marca instância de hábito como skipped (pulada) com categorização.

    Exemplos:
        timeblock habit skip 42 --category WORK --note "Reunião urgente"
        timeblock habit skip 42 --category HEALTH
    """
    try:
        if category is None:
            console.print("[red]Categoria obrigatória. Use --category[/red]")
            console.print("\nCategorias válidas:")
            console.print("  HEALTH, WORK, FAMILY, TRAVEL, WEATHER,")
            console.print("  LACK_RESOURCES, EMERGENCY, OTHER")
            raise typer.Exit(1)

        try:
            skip_reason = SkipReason[category.upper()]
        except KeyError:
            console.print(f"[red]Categoria inválida: {category}[/red]")
            console.print("\nCategorias válidas:")
            console.print("  HEALTH, WORK, FAMILY, TRAVEL, WEATHER,")
            console.print("  LACK_RESOURCES, EMERGENCY, OTHER")
            raise typer.Exit(1)

        if note and len(note) > 500:
            console.print("[red]Nota muito longa (máximo 500 caracteres)[/red]")
            raise typer.Exit(1)

        with get_engine_context() as engine, Session(engine) as session:
            service = HabitInstanceService()
            service.skip_habit_instance(
                habit_instance_id=instance_id,
                skip_reason=skip_reason,
                skip_note=note,
                session=session,
            )

            category_pt = {
                "health": "Saúde",
                "work": "Trabalho",
                "family": "Família",
                "travel": "Viagem",
                "weather": "Clima",
                "lack_resources": "Falta de recursos",
                "emergency": "Emergência",
                "other": "Outro",
            }

            console.print("[green]Hábito marcado como skipped[/green]")
            console.print(f"  Categoria: {category_pt.get(skip_reason.value, skip_reason.value)}")
            if note:
                console.print(f"  Nota: {note}")

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            console.print(f"[red]HabitInstance {instance_id} não encontrada[/red]")
            raise typer.Exit(2)
        elif "timer" in error_msg.lower():
            console.print("[red]Pare o timer antes de marcar skip[/red]")
            raise typer.Exit(1)
        elif "completed" in error_msg.lower():
            console.print("[red]Não é possível skip de instância completada[/red]")
            raise typer.Exit(1)
        else:
            console.print(f"[red]Erro: {e}[/red]")
            raise typer.Exit(1)
