"""Comandos CRUD para hábitos."""

from datetime import date
from datetime import time as dt_time

import typer
from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]
from rich.console import Console
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.models import Recurrence
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.habit_service import HabitService
from timeblock.services.routine_service import RoutineService

console = Console()


def create_habit(
    title: str = typer.Option(..., "--title", "-t", help="Título do hábito"),
    start: str = typer.Option(..., "--start", "-s", help="Hora início (HH:MM)"),
    end: str = typer.Option(..., "--end", "-e", help="Hora fim (HH:MM)"),
    repeat: str = typer.Option(..., "--repeat", "-r", help="Padrão de repetição"),
    color: str = typer.Option(None, "--color", "-c", help="Cor do hábito"),
    routine: int = typer.Option(None, "--routine", help="ID da rotina (padrão: ativa)"),
    generate: int = typer.Option(None, "--generate", "-g", help="Gerar instâncias (meses)"),
):
    """Cria um novo hábito."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            habit_service = HabitService(session)

            # Determinar rotina
            if routine is None:
                active_routine = routine_service.get_active_routine()
                if active_routine is None:
                    console.print(
                        "[red]Nenhuma rotina ativa. Crie e ative uma rotina primeiro.[/red]"
                    )
                    raise typer.Exit(1)
                console.print(
                    f"Rotina ativa: [bold]{active_routine.name}[/bold] (ID: {active_routine.id})"
                )
                if not typer.confirm("Criar hábito nesta rotina?", default=True):
                    routine_id = typer.prompt("ID da rotina", type=int)
                else:
                    routine_id = active_routine.id
            else:
                routine_id = routine

            # Guard clause
            if routine_id is None:
                console.print("[red]Erro: ID da rotina não definido[/red]")
                raise typer.Exit(1)

            # Validar rotina existe
            routine_obj = routine_service.get_routine(routine_id)
            if routine_obj is None:
                console.print(f"[red]Rotina {routine_id} não encontrada[/red]")
                raise typer.Exit(1)

            # Parse recurrence
            try:
                rec = Recurrence(repeat.upper())
            except ValueError:
                valid = ", ".join([r.value for r in Recurrence])
                console.print(f"[red]Recorrência inválida. Use: {valid}[/red]")
                raise typer.Exit(1)

            # Parse times
            start_time = dt_time.fromisoformat(start)
            end_time = dt_time.fromisoformat(end)

            # Criar hábito
            habit = habit_service.create_habit(
                routine_id=routine_id,
                title=title,
                scheduled_start=start_time,
                scheduled_end=end_time,
                recurrence=rec,
                color=color,
            )

            console.print("\n[green]Hábito criado com sucesso![/green]\n")
            console.print(f"ID: [cyan]{habit.id}[/cyan]")
            console.print(f"Título: [bold]{habit.title}[/bold]")
            console.print(
                f"Horário: {habit.scheduled_start.strftime('%H:%M')} - "
                f"{habit.scheduled_end.strftime('%H:%M')}"
            )
            console.print(f"Recorrência: {habit.recurrence.value}")

            if generate:
                start_date = date.today()
                end_date = start_date + relativedelta(months=generate)

                assert habit.id is not None
                instances = HabitInstanceService.generate_instances(
                    habit_id=habit.id,
                    start_date=start_date,
                    end_date=end_date,
                )
                console.print(f"\n[green]{len(instances)} instâncias geradas[/green]")

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


def list_habits(
    routine: str = typer.Option("active", "--routine", "-R", help="Filtrar: active, all ou ID"),
):
    """Lista hábitos."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            habit_service = HabitService(session)

            if routine == "active":
                active_routine = routine_service.get_active_routine()
                if active_routine is None:
                    console.print("[red]Nenhuma rotina ativa[/red]")
                    raise typer.Exit(1)
                routine_id: int | None = active_routine.id
                title = f"Hábitos - {active_routine.name} (ativa)"
            elif routine == "all":
                routine_id = None
                title = "Todos os Hábitos"
            else:
                routine_id = int(routine)
                routine_obj = routine_service.get_routine(routine_id)
                if routine_obj is None:
                    console.print(f"[red]Rotina {routine_id} não encontrada[/red]")
                    raise typer.Exit(1)
                title = f"Hábitos - {routine_obj.name}"

            habits = habit_service.list_habits(routine_id)

            if not habits:
                console.print("[yellow]Nenhum hábito encontrado.[/yellow]")
                return

            console.print(f"\n[bold]{title}[/bold]\n")
            for h in habits:
                rec = h.recurrence.value.replace("_", " ").title()
                console.print(
                    f"[cyan]{h.id}[/cyan] [bold]{h.title}[/bold] "
                    f"({rec} {h.scheduled_start.strftime('%H:%M')}-"
                    f"{h.scheduled_end.strftime('%H:%M')})"
                )
            console.print()

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


def update_habit(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    title: str = typer.Option(None, "--title", "-t", help="Novo título"),
    start: str = typer.Option(None, "--start", "-s", help="Nova hora início (HH:MM)"),
    end: str = typer.Option(None, "--end", "-e", help="Nova hora fim (HH:MM)"),
    repeat: str = typer.Option(None, "--repeat", "-r", help="Novo padrão"),
    color: str = typer.Option(None, "--color", "-c", help="Nova cor"),
):
    """Atualiza um hábito."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            habit_service = HabitService(session)

            habit = habit_service.get_habit(habit_id)
            if habit is None:
                console.print(f"[red]Hábito {habit_id} não encontrado[/red]")
                raise typer.Exit(1)

            updates: dict = {}
            if title:
                updates["title"] = title
            if start:
                updates["scheduled_start"] = dt_time.fromisoformat(start)
            if end:
                updates["scheduled_end"] = dt_time.fromisoformat(end)
            if repeat:
                try:
                    updates["recurrence"] = Recurrence(repeat.upper())
                except ValueError:
                    valid = ", ".join([r.value for r in Recurrence])
                    console.print(f"[red]Recorrência inválida. Use: {valid}[/red]")
                    raise typer.Exit(1)
            if color:
                updates["color"] = color

            if not updates:
                console.print("[yellow]Nenhuma alteração especificada.[/yellow]")
                return

            habit_service.update_habit(habit_id, **updates)
            console.print(f"[green]Hábito atualizado: [bold]{habit.title}[/bold][/green]")

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


def delete_habit(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    force: bool = typer.Option(False, "--force", "-f", help="Não pedir confirmação"),
):
    """Deleta um hábito."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            habit_service = HabitService(session)

            habit = habit_service.get_habit(habit_id)
            if habit is None:
                console.print(f"[red]Hábito {habit_id} não encontrado[/red]")
                raise typer.Exit(1)

            if not force:
                if not typer.confirm(f"Deletar hábito '{habit.title}'?", default=False):
                    console.print("[yellow]Cancelado.[/yellow]")
                    return

            habit_service.delete_habit(habit_id)
            console.print(f"[green]Hábito deletado: [bold]{habit.title}[/bold][/green]")

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)
