"""Funções de busca e computação de dados para o HeaderBar.

Responsabilidade única: acessar a service layer e retornar
dados agregados prontos para consumo pelo renderer.

Cada função recebe dependências explícitas (sem estado global)
e retorna tuplas simples — sem markup Rich, sem lógica de UI.

Referências:
    - BR-TUI-035: Conteúdo interno do HeaderBar
    - ADR-052: Redesign do conteúdo interno do HeaderBar
    - MARTIN, R. Clean Code, 2008, cap. 10 (Classes)
"""

from datetime import date, datetime, time, timedelta

from timeblock.models.enums import Status
from timeblock.models.routine import Routine
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.habit_service import HabitService
from timeblock.services.routine_service import RoutineService
from timeblock.services.task_service import TaskService
from timeblock.tui.session import service_action
from timeblock.utils.logger import get_logger

logger = get_logger(__name__)


def fetch_active_routine() -> Routine | None:
    """Retorna rotina ativa ou None."""
    try:
        result, error = service_action(
            lambda s: RoutineService(s).get_active_routine(),
        )
        if error or not result:
            return None
        return result
    except Exception:
        logger.debug("Exceção em fetch_active_routine", exc_info=True)
        return None


def compute_weekly_habits_progress(
    routine: Routine | None,
    today: date,
) -> tuple[int, int]:
    """Calcula progresso semanal de hábitos (BR-TUI-035 regras 1-5).

    Args:
        routine: rotina ativa ou None.
        today: data de referência.

    Returns:
        (done_count, total_expected). (0, 0) se sem rotina.
    """
    if routine is None:
        return 0, 0

    try:
        monday = today - timedelta(days=today.weekday())
        days_elapsed = (today - monday).days + 1

        habits_result, error = service_action(
            lambda s: HabitService(s).list_habits(routine_id=routine.id),
        )
        if error or not habits_result:
            return 0, 0

        total_expected = len(habits_result) * days_elapsed

        svc = HabitInstanceService()
        instances = svc.list_instances(date_start=monday, date_end=today)
        done_count = sum(1 for i in instances if i.status == Status.DONE)

        return done_count, total_expected
    except Exception:
        logger.debug("Exceção em compute_weekly_habits_progress", exc_info=True)
        return 0, 0


def compute_daily_tasks_progress(today: date) -> tuple[int, int]:
    """Calcula progresso de tarefas do dia (BR-TUI-035 regras 6-10).

    Args:
        today: data de referência.

    Returns:
        (completed_today, total_today). (0, 0) se sem tarefas.
    """
    try:
        all_tasks, error = service_action(
            lambda s: TaskService.list_tasks(session=s),
        )
        if error or not all_tasks:
            return 0, 0

        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)

        relevant = [
            t
            for t in all_tasks
            if (
                t.completed_datetime is not None
                and today_start <= t.completed_datetime <= today_end
            )
            or (
                t.completed_datetime is None
                and t.cancelled_datetime is None
                and t.scheduled_datetime <= today_end
            )
        ]

        completed = sum(
            1
            for t in relevant
            if t.completed_datetime is not None and today_start <= t.completed_datetime <= today_end
        )

        return completed, len(relevant)
    except Exception:
        logger.debug("Exceção em compute_daily_tasks_progress", exc_info=True)
        return 0, 0


def find_next_pending_item(
    routine: Routine | None,
    now: datetime,
) -> tuple[str | None, int | None]:
    """Identifica próximo item pendente hoje (BR-TUI-035 regras 11-17).

    Compara próximo hábito vs próxima tarefa. Hábito tem prioridade
    em caso de empate (regra 15).

    Args:
        routine: rotina ativa ou None.
        now: momento atual.

    Returns:
        (name, minutes_until) ou (None, None) se sem próximo.
    """
    today = now.date()
    today_end = datetime.combine(today, time.max)

    next_habit = _find_next_habit(routine, today, now)
    next_task = _find_next_task(today_end, now)

    return _pick_closest(next_habit, next_task, now)


def _find_next_habit(
    routine: Routine | None,
    today: date,
    now: datetime,
) -> tuple[str | None, datetime | None]:
    """Retorna (nome, datetime) do próximo hábito pendente ou (None, None)."""
    if routine is None:
        return None, None

    try:
        svc = HabitInstanceService()
        instances = svc.list_instances(date_start=today, date_end=today)

        best_name: str | None = None
        best_dt: datetime | None = None

        for inst in instances:
            if inst.status != Status.PENDING:
                continue
            inst_dt = datetime.combine(today, inst.scheduled_start)
            if inst_dt <= now:
                continue
            if best_dt is None or inst_dt < best_dt:
                best_dt = inst_dt
                habit = inst.habit
                best_name = habit.title if habit else str(inst.habit_id)

        return best_name, best_dt
    except Exception:
        logger.debug("Exceção em _find_next_habit", exc_info=True)
        return None, None


def _find_next_task(
    today_end: datetime,
    now: datetime,
) -> tuple[str | None, datetime | None]:
    """Retorna (título, datetime) da próxima tarefa pendente ou (None, None)."""
    try:
        tasks, error = service_action(
            lambda s: TaskService.list_pending_tasks(session=s),
        )
        if error or not tasks:
            return None, None

        best_name: str | None = None
        best_dt: datetime | None = None

        for t in tasks:
            if now < t.scheduled_datetime <= today_end:
                if best_dt is None or t.scheduled_datetime < best_dt:
                    best_dt = t.scheduled_datetime
                    best_name = t.title

        return best_name, best_dt
    except Exception:
        logger.debug("Exceção em _find_next_task", exc_info=True)
        return None, None


def _pick_closest(
    habit: tuple[str | None, datetime | None],
    task: tuple[str | None, datetime | None],
    now: datetime,
) -> tuple[str | None, int | None]:
    """Escolhe o item mais próximo. Hábito vence empate (regra 15)."""
    habit_name, habit_dt = habit
    task_name, task_dt = task

    if habit_dt and task_dt:
        if habit_dt <= task_dt:
            return habit_name, max(0, int((habit_dt - now).total_seconds() / 60))
        return task_name, max(0, int((task_dt - now).total_seconds() / 60))
    if habit_dt:
        return habit_name, max(0, int((habit_dt - now).total_seconds() / 60))
    if task_dt:
        return task_name, max(0, int((task_dt - now).total_seconds() / 60))

    return None, None
