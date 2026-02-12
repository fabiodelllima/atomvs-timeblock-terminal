"""Helpers de display para timer."""

import json
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.habit_service import HabitService
from timeblock.services.task_service import TaskService
from timeblock.services.timer_service import TimerService

console = Console()


def get_selected_schedule():
    """Recupera schedule selecionado do contexto."""
    config_path = Path.home() / ".timeblock_context"
    if not config_path.exists():
        return None
    try:
        config = json.loads(config_path.read_text())
        return config.get("selected_schedule")
    except Exception:
        return None


def get_activity_name(timelog) -> str:
    """Retorna nome da atividade do timelog."""
    instance_service = HabitInstanceService()

    if timelog.habit_instance_id:
        instance = instance_service.get_instance(timelog.habit_instance_id)
        if instance:
            with get_engine_context() as engine, Session(engine) as session:
                habit_service = HabitService(session)
                habit = habit_service.get_habit(instance.habit_id)
                if habit:
                    return f"{habit.title} ({instance.date.strftime('%d/%m/%Y')})"
    elif timelog.task_id:
        task = TaskService.get_task(timelog.task_id)
        if task:
            return task.title

    return "Atividade"


def format_duration(total_seconds: int) -> tuple[int, int, int]:
    """Formata segundos em horas, minutos, segundos."""
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds


def display_timer(timelog_id: int) -> None:
    """Mostra timer ativo com atualização em tempo real."""
    timer_service = TimerService()

    with Live(refresh_per_second=1, console=console) as live:
        while True:
            try:
                timelog = timer_service.get_timelog(timelog_id)

                if timelog is None or timelog.end_time:
                    break

                elapsed = datetime.now() - timelog.start_time
                hours, minutes, seconds = format_duration(int(elapsed.total_seconds()))

                activity = get_activity_name(timelog)

                text = Text()
                text.append("[>] ", style="bold cyan")
                text.append(f"{hours:02d}:{minutes:02d}:{seconds:02d}", style="bold cyan")
                text.append(" | ", style="dim")
                text.append(activity, style="bold white")
                text.append(" | ", style="dim")

                if hasattr(timelog, "paused") and timelog.paused:
                    text.append("[||] Pausado", style="yellow")
                else:
                    text.append("[>] Em andamento", style="green")

                info = f"\n\nIniciado: {timelog.start_time.strftime('%H:%M')}\n"
                info += "\nComandos: [yellow]pause[/] | [green]stop[/] | [red]cancel[/]"

                panel = Panel(text.append(info), title="Timer Ativo", border_style="cyan")
                live.update(panel)
                time.sleep(1)

            except KeyboardInterrupt:
                console.print(
                    "\n\nTimer ainda ativo. Use 'timeblock timer stop' ou 'timer cancel'",
                    style="yellow",
                )
                return
            except Exception as e:
                console.print(f"\n[red]Erro: {e}[/red]")
                return
