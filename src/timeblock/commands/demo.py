"""Comando demo: popula banco com rotinas de demonstração (BR-TUI-003-R28)."""

from datetime import datetime, time, timedelta
from typing import NamedTuple

import typer
from rich.console import Console

from timeblock.models.habit import Recurrence
from timeblock.services.habit_service import HabitService
from timeblock.services.routine_service import RoutineService
from timeblock.services.task_service import TaskService
from timeblock.utils.logger import get_logger

logger = get_logger(__name__)

app = typer.Typer(help="Cria dados de demonstração para showcase da TUI.")
console = Console()


class HabitDef(NamedTuple):
    """Definição de hábito para demo."""

    title: str
    start: time
    end: time


class RoutineDef(NamedTuple):
    """Definição de rotina para demo."""

    recurrence: Recurrence
    habits: list[HabitDef]


DEMO_ROUTINES: dict[str, RoutineDef] = {
    "Semanal Mock": RoutineDef(
        recurrence=Recurrence.WEEKDAYS,
        habits=[
            HabitDef("Despertar", time(6, 0), time(6, 30)),
            HabitDef("Academia", time(6, 30), time(7, 30)),
            HabitDef("Standup", time(8, 0), time(8, 30)),
            HabitDef("Deep Work", time(9, 0), time(12, 0)),
            HabitDef("Almoço", time(12, 0), time(13, 0)),
            HabitDef("Code Review", time(14, 0), time(16, 0)),
            HabitDef("Estudo", time(16, 0), time(17, 0)),
            HabitDef("Leitura", time(21, 0), time(22, 0)),
        ],
    ),
    "Fim de Semana Mock": RoutineDef(
        recurrence=Recurrence.WEEKENDS,
        habits=[
            HabitDef("Despertar", time(8, 0), time(9, 0)),
            HabitDef("Exercício", time(9, 0), time(10, 0)),
            HabitDef("Projeto Pessoal", time(10, 0), time(12, 0)),
            HabitDef("Almoço", time(12, 0), time(13, 0)),
            HabitDef("Leitura", time(15, 0), time(16, 0)),
            HabitDef("Jantar", time(19, 0), time(20, 0)),
        ],
    ),
    "Férias Mock": RoutineDef(
        recurrence=Recurrence.EVERYDAY,
        habits=[
            HabitDef("Despertar", time(9, 0), time(10, 0)),
            HabitDef("Yoga", time(10, 0), time(11, 0)),
            HabitDef("Leitura", time(11, 0), time(12, 0)),
            HabitDef("Caminhada", time(14, 0), time(15, 0)),
            HabitDef("Journaling", time(20, 0), time(21, 0)),
        ],
    ),
}

DEMO_TASKS: list[tuple[str, timedelta]] = [
    ("Dentista", timedelta(hours=3)),
    ("Email cliente", timedelta(days=1)),
    ("Deploy staging", timedelta(days=3)),
    ("Code review PR", timedelta(days=5)),
    ("Retrospectiva", timedelta(days=14)),
    ("Renovar domínio", timedelta(days=30)),
    ("Enviar relatório", timedelta(days=-2)),
    ("Revisar PR #142", timedelta(days=-1)),
]


@app.command("create")
def create(
    activate: bool = typer.Option(True, "--activate/--no-activate", help="Ativa a primeira rotina"),
) -> None:
    """Cria 3 rotinas demo com hábitos e tarefas para showcase."""
    from sqlmodel import Session

    from timeblock.database import get_engine_context

    with get_engine_context() as engine, Session(engine) as session:
        routine_svc = RoutineService(session)
        habit_svc = HabitService(session)

        created_routines = []
        for name, config in DEMO_ROUTINES.items():
            routine = routine_svc.create_routine(name)
            session.commit()
            session.refresh(routine)
            created_routines.append(routine)
            console.print(f"  [green]+[/green] Rotina: {name}")

            for habit_def in config.habits:
                habit_svc.create_habit(
                    routine_id=routine.id,  # type: ignore[arg-type]
                    title=habit_def.title,
                    scheduled_start=habit_def.start,
                    scheduled_end=habit_def.end,
                    recurrence=config.recurrence,
                )
            session.commit()
            console.print(f"    {len(config.habits)} hábitos criados")

        now = datetime.now()
        for title, delta in DEMO_TASKS:
            TaskService.create_task(
                title=title,
                scheduled_datetime=now + delta,
                session=session,
            )
        session.commit()
        console.print(f"  [green]+[/green] {len(DEMO_TASKS)} tarefas criadas")

        if activate and created_routines:
            routine_svc.activate_routine(
                created_routines[0].id  # type: ignore[arg-type]
            )
            session.commit()
            console.print(f"\n  [bold]Rotina ativa:[/bold] {created_routines[0].name}")

    console.print(
        "\n[green]Demo criado com sucesso.[/green] Use [bold]atomvs tui[/bold] para visualizar."
    )


@app.command("clear")
def clear() -> None:
    """Remove todas as rotinas e tarefas demo."""
    from sqlmodel import Session, select

    from timeblock.database import get_engine_context
    from timeblock.models.habit import Habit
    from timeblock.models.routine import Routine

    with get_engine_context() as engine, Session(engine) as session:
        removed = 0
        for name in DEMO_ROUTINES:
            stmt = select(Routine).where(Routine.name == name)
            routine = session.exec(stmt).first()
            if routine:
                habits = session.exec(select(Habit).where(Habit.routine_id == routine.id)).all()
                for h in habits:
                    session.delete(h)
                session.flush()
                session.delete(routine)
                session.commit()
                removed += 1

        console.print(f"  [red]-[/red] {removed} rotinas demo removidas (com hábitos)")
        console.print("[green]Limpeza concluída.[/green]")
