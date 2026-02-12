"""Comandos para gerenciar timer de tracking."""

from datetime import datetime

import typer
from rich.console import Console
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.habit_service import HabitService
from timeblock.services.task_service import TaskService
from timeblock.services.timer_service import TimerService
from timeblock.utils.conflict_display import display_conflicts

from .display import display_timer, format_duration, get_activity_name, get_selected_schedule

console = Console()


def start_timer(
    background: bool = typer.Option(
        False, "--background", "-b", help="Não mostrar display interativo"
    ),
    schedule: int = typer.Option(None, "--schedule", "-s", help="ID da instância agendada"),
    task: int = typer.Option(None, "--task", "-t", help="ID da tarefa"),
):
    """
    Inicia timer (workflow A: direto ou B: via select).

    Se houver conflitos de horário, o timer será iniciado normalmente
    mas os conflitos serão exibidos para o usuário.
    """
    try:
        instance_service = HabitInstanceService()

        active = TimerService.get_any_active_timer()
        if active:
            console.print(
                "[red]Já existe um timer ativo. Use 'timer stop' ou 'timer cancel' primeiro.[/red]"
            )
            raise typer.Exit(1)

        timelog = None
        conflicts: list = []

        if schedule or task:
            timelog = _start_with_flags(schedule, task, instance_service)
        else:
            timelog = _start_via_select(instance_service)

        console.print(
            f"\n[green]Timer iniciado às {timelog.start_time.strftime('%H:%M')}![/green]\n"
        )

        if conflicts:
            console.print("[yellow]Atenção: Conflitos detectados no horário atual:[/yellow]")
            display_conflicts(conflicts, console)
            console.print(
                "[dim]Timer foi iniciado. Você pode ajustar eventos conflitantes depois.[/dim]\n"
            )

        assert timelog.id is not None, "TimeLog must be persisted"
        if not background:
            display_timer(timelog.id)

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


def _start_with_flags(schedule: int | None, task: int | None, instance_service):
    """Inicia timer com flags --schedule ou --task."""
    if schedule:
        instance = instance_service.get_instance(schedule)
        if instance is None:
            console.print("[red]Instância não encontrada[/red]")
            raise typer.Exit(1)

        with get_engine_context() as engine, Session(engine) as session:
            habit_service = HabitService(session)
            habit = habit_service.get_habit(instance.habit_id)
            if habit is None:
                console.print("[red]Hábito não encontrado[/red]")
                raise typer.Exit(1)
            activity = f"{habit.title} ({instance.date.strftime('%d/%m/%Y')})"

        if not typer.confirm(f"Iniciar timer para {activity}?", default=True):
            console.print("[yellow]Cancelado.[/yellow]")
            raise typer.Exit(0)

        return TimerService.start_timer(habit_instance_id=schedule)

    # Guard clause: task é obrigatório se chegou aqui
    if task is None:
        console.print("[red]Erro: --schedule ou --task obrigatório[/red]")
        raise typer.Exit(1)

    task_obj = TaskService.get_task(task)
    if task_obj is None:
        console.print("[red]Tarefa não encontrada[/red]")
        raise typer.Exit(1)

    console.print("[red]Timer para tasks não implementado[/red]")
    raise typer.Exit(1)


def _start_via_select(instance_service):
    """Inicia timer via schedule selecionado."""
    selected = get_selected_schedule()
    if not selected:
        console.print(
            "[red]Nenhuma instância selecionada. "
            "Use 'timeblock schedule select <id>' ou '--schedule <id>'[/red]"
        )
        raise typer.Exit(1)

    instance = instance_service.get_instance(selected)
    if instance is None:
        console.print("[red]Instância não encontrada[/red]")
        raise typer.Exit(1)

    with get_engine_context() as engine, Session(engine) as session:
        habit_service = HabitService(session)
        habit = habit_service.get_habit(instance.habit_id)

        if habit is None:
            console.print("[red]Hábito não encontrado[/red]")
            raise typer.Exit(1)

        if not typer.confirm(f"Iniciar timer para {habit.title}?", default=True):
            console.print("[yellow]Cancelado.[/yellow]")
            raise typer.Exit(0)

    return TimerService.start_timer(habit_instance_id=selected)


def pause_timer():
    """Pausa o timer ativo."""
    try:
        active = TimerService.get_any_active_timer()
        if not active:
            console.print("[red]Nenhum timer ativo[/red]")
            raise typer.Exit(1)

        TimerService.pause_timer(active.id)  # type: ignore[arg-type]
        console.print("[yellow][||] Timer pausado[/yellow]")

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


def resume_timer(
    background: bool = typer.Option(
        False, "--background", "-b", help="Não mostrar display interativo"
    ),
):
    """Retoma timer pausado."""
    try:
        active = TimerService.get_any_active_timer()
        if not active:
            console.print("[red]Nenhum timer ativo[/red]")
            raise typer.Exit(1)

        TimerService.resume_timer(active.id)  # type: ignore[arg-type]
        console.print("[green][>] Timer retomado[/green]")

        if not background:
            display_timer(active.id)  # type: ignore[arg-type]

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


def stop_timer():
    """Finaliza e salva o timer."""
    try:
        active = TimerService.get_any_active_timer()
        if not active:
            console.print("[red]Nenhum timer ativo[/red]")
            raise typer.Exit(1)

        timelog = TimerService.stop_timer(active.id)  # type: ignore[arg-type]

        if timelog.end_time is None:
            console.print("[red]Erro ao finalizar timer[/red]")
            raise typer.Exit(1)

        duration = timelog.end_time - timelog.start_time
        hours, minutes, seconds = format_duration(int(duration.total_seconds()))

        console.print("\n[green]Timer finalizado![/green]\n")
        console.print(f"Duração total: {hours}h {minutes}min {seconds}s")
        console.print(f"Início: {timelog.start_time.strftime('%H:%M')}")
        console.print(f"Fim: {timelog.end_time.strftime('%H:%M')}")
        console.print()

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


def cancel_timer():
    """Cancela timer sem salvar."""
    try:
        active = TimerService.get_any_active_timer()
        if not active:
            console.print("[red]Nenhum timer ativo[/red]")
            raise typer.Exit(1)

        if not typer.confirm("Cancelar timer? (não será salvo)", default=False):
            console.print("[yellow]Operação cancelada.[/yellow]")
            return

        TimerService.cancel_timer(active.id)  # type: ignore[arg-type]
        console.print("[yellow]Timer cancelado (não salvo)[/yellow]")

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


def timer_status():
    """Mostra status do timer atual."""
    try:
        active = TimerService.get_any_active_timer()

        if not active:
            console.print("[yellow]Nenhum timer ativo[/yellow]")
            return

        elapsed = datetime.now() - active.start_time
        hours, minutes, seconds = format_duration(int(elapsed.total_seconds()))

        activity = get_activity_name(active)

        console.print(f"\n[bold]Timer Ativo:[/bold] {activity}")
        console.print(f"Tempo decorrido: {hours:02d}:{minutes:02d}:{seconds:02d}")
        console.print(f"Iniciado: {active.start_time.strftime('%H:%M')}\n")

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)
