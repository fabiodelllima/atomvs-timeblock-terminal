"""Comandos para instâncias de hábitos (atom)."""

from datetime import date
from datetime import time as dt_time

import typer
from rich.console import Console
from sqlmodel import Session, select

from timeblock.database import get_engine_context
from timeblock.models.habit import Habit
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.routine_service import RoutineService
from timeblock.services.timer_service import TimerService
from timeblock.utils.logger import get_logger

from .display import (
    _resolve_date_range,
    _resolve_status_filter,
    display_instances,
    display_log_result,
    handle_log_error,
)

logger = get_logger(__name__)

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
        logger.exception("Erro inesperado em comando atom")
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


@atom_app.command("generate")
def atom_generate(
    months: int = typer.Option(0, "--months", "-m", help="Gerar para N meses (0 = apenas hoje)"),
):
    """
    Gera instâncias para hábitos da rotina ativa.

    Por padrão gera apenas para hoje. Com --months N, gera para
    os próximos N meses.

    Exemplos:
        atomvs habit atom generate          # Hoje
        atomvs habit atom generate -m 3     # Próximos 3 meses
    """
    try:
        with get_engine_context() as engine, Session(engine) as session:
            routine = RoutineService(session).get_active_routine()
            if not routine:
                console.print("[red]Nenhuma rotina ativa.[/red]")
                raise typer.Exit(1)

            habits = list(session.exec(select(Habit).where(Habit.routine_id == routine.id)).all())
            if not habits:
                console.print(f"[yellow]Rotina '{routine.name}' não tem hábitos.[/yellow]")
                raise typer.Exit(0)

            from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]

            start_date = date.today()
            end_date = start_date + relativedelta(months=months) if months > 0 else start_date

            total = 0
            for habit in habits:
                assert habit.id is not None
                created = HabitInstanceService.generate_instances(
                    habit_id=habit.id,
                    start_date=start_date,
                    end_date=end_date,
                    session=session,
                )
                if created:
                    total += len(created)
                    console.print(
                        f"  [green]\u2713[/green] {habit.title} ({habit.recurrence.value})"
                        f" \u2192 {len(created)} instância(s)"
                    )

            if total:
                console.print(f"\n[green]Total: {total} instância(s) gerada(s)[/green]")
            else:
                console.print(
                    "[yellow]Nenhuma instância nova gerada (já existem ou não aplicam).[/yellow]"
                )

    except typer.Exit:
        raise
    except Exception as e:
        logger.exception("Erro inesperado em comando atom")
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


@atom_app.command("done")
def atom_done(
    instance_id: int = typer.Argument(..., help="ID da instância"),
):
    """
    Marca instância de hábito como concluída (DONE).

    Exemplos:
        atomvs habit atom done 42
    """
    try:
        with get_engine_context() as engine, Session(engine) as session:
            result = HabitInstanceService.mark_completed(instance_id=instance_id, session=session)
            if result:
                name = ""
                if result.habit:
                    name = f" ({result.habit.title})"
                console.print(
                    f"[green]\u2713 Instância #{instance_id}{name} marcada como concluída[/green]"
                )
            else:
                console.print(f"[red]Instância #{instance_id} não encontrada[/red]")
                raise typer.Exit(1)

    except typer.Exit:
        raise
    except ValueError as e:
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
