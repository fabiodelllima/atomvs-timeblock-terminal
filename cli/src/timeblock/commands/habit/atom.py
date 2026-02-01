"""Comandos para instâncias de hábitos (atom)."""

from datetime import time as dt_time

import typer
from rich.console import Console
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.timer_service import TimerService

from .display import (
    _resolve_date_range,
    _resolve_status_filter,
    display_instances,
    display_log_result,
    handle_log_error,
)

console = Console()

atom_app = typer.Typer(help="Gerenciar instâncias de hábitos")


def _validate_log_mode(start: str | None, end: str | None, duration: int | None) -> None:
    """Valida modos mutuamente exclusivos para log manual."""
    has_interval = start is not None or end is not None
    has_duration = duration is not None

    if has_interval and has_duration:
        raise ValueError("não pode combinar --start/--end com --duration")
    if not has_interval and not has_duration:
        raise ValueError("forneça intervalo (--start/--end) ou duração (--duration)")
    if has_interval and (start is None or end is None):
        raise ValueError("--start requer --end (e vice-versa)")


def _parse_time_string(time_str: str, param_name: str) -> dt_time:
    """Parse string HH:MM para objeto time."""
    try:
        parts = time_str.split(":")
        return dt_time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        raise ValueError(f"Formato inválido para {param_name}: {time_str}. Use HH:MM")


@atom_app.command("list")
def atom_list(
    habit_id: int = typer.Argument(None, help="Filtrar por ID do hábito"),
    today: bool = typer.Option(False, "--today", "-T", help="Apenas hoje"),
    week: bool = typer.Option(False, "--week", "-w", help="Semana atual"),
    pending: bool = typer.Option(False, "--pending", "-P", help="Apenas PENDING"),
    done: bool = typer.Option(False, "--done", "-C", help="Apenas DONE"),
    all_status: bool = typer.Option(False, "--all", "-a", help="Todos status"),
):
    """
    Lista instâncias de hábitos (BR-HABITINSTANCE-006).

    Defaults:
        Sem flags: semana atual, apenas pendentes
        Com HABIT_ID: todas datas, todos status

    Exemplos:
        timeblock habit atom list              # Semana, pendentes
        timeblock habit atom list 1            # Todas do hábito 1
        timeblock habit atom list -T           # Hoje, todos status
        timeblock habit atom list -T -C        # Hoje, completadas
    """
    try:
        date_start, date_end = _resolve_date_range(today, week, habit_id)
        status_filter = _resolve_status_filter(pending, done, all_status, habit_id)

        with get_engine_context() as engine, Session(engine) as session:
            service = HabitInstanceService()

            instances = service.list_instances(
                habit_id=habit_id,
                date_start=date_start,
                date_end=date_end,
                session=session,
            )

            if status_filter is not None:
                instances = [i for i in instances if i.status == status_filter]

            display_instances(instances, today, week, habit_id, status_filter)

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


@atom_app.command("log")
def atom_log(
    instance_id: int = typer.Argument(..., help="ID da instância"),
    start: str = typer.Option(None, "--start", "-s", help="Hora início (HH:MM)"),
    end: str = typer.Option(None, "--end", "-e", help="Hora fim (HH:MM)"),
    duration: int = typer.Option(None, "--duration", "-d", help="Duração em minutos"),
):
    """
    Registra tempo manualmente sem usar timer (BR-TIMER-007).

    Dois modos mutuamente exclusivos:
        - Intervalo: --start HH:MM --end HH:MM
        - Duração: --duration MINUTOS

    Exemplos:
        timeblock habit atom log 42 --start 07:00 --end 08:00
        timeblock habit atom log 42 --duration 60
    """
    try:
        _validate_log_mode(start, end, duration)

        start_time = _parse_time_string(start, "--start") if start else None
        end_time = _parse_time_string(end, "--end") if end else None

        with get_engine_context() as engine, Session(engine) as session:
            service = TimerService()
            timelog = service.log_manual(
                habit_instance_id=instance_id,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration,
                session=session,
            )

            instance_service = HabitInstanceService()
            instance = instance_service.get_instance(instance_id, session=session)

            display_log_result(timelog, instance)

    except ValueError as e:
        handle_log_error(e, instance_id)
        raise typer.Exit(1)
