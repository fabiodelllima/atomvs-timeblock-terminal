"""Dashboard data loader (RF-003, BR-TUI-009).

Responsabilidade única: buscar dados via services e transformar
em dicts para consumo dos panels. Nenhuma lógica de apresentação.

Referências:
    - RF-003: Split Phase (FOWLER, 2018, p. 154)
    - BR-TUI-009: Service Layer Sharing
"""

from datetime import date, datetime
from typing import Any

from sqlmodel import Session, col, select

from timeblock.models.enums import Status
from timeblock.models.habit import Habit
from timeblock.models.habit_instance import HabitInstance
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.routine_service import RoutineService
from timeblock.services.task_service import TaskService
from timeblock.services.timer_service import TimerService
from timeblock.tui.session import service_action
from timeblock.utils.logger import get_logger

logger = get_logger(__name__)


def ensure_today_instances() -> int:
    """Garante instâncias para todos os hábitos aplicáveis ao dia (DT-023).

    Chamado no startup da TUI e na detecção de virada de dia.
    Para cada hábito da rotina ativa cuja recurrence bate com hoje
    e que ainda não tem instância, gera via INSERT direto.
    Idempotente — chamadas repetidas não duplicam.

    Returns:
        Número de instâncias criadas.
    """

    def _ensure(s: Session) -> int:
        routine = RoutineService(s).get_active_routine()
        if not routine or not routine.id:
            return 0

        habits = list(s.exec(select(Habit).where(Habit.routine_id == routine.id)).all())
        if not habits:
            return 0

        today = date.today()
        habit_ids = [h.id for h in habits if h.id is not None]

        existing_ids = set(
            s.exec(
                select(HabitInstance.habit_id)
                .where(HabitInstance.date == today)
                .where(col(HabitInstance.habit_id).in_(habit_ids))
            ).all()
        )

        created = 0
        for habit in habits:
            if habit.id in existing_ids:
                continue
            if not HabitInstanceService._should_create_for_date(habit.recurrence, today):
                continue
            s.add(
                HabitInstance(
                    habit_id=habit.id,
                    date=today,
                    scheduled_start=habit.scheduled_start,
                    scheduled_end=habit.scheduled_end,
                    status=Status.PENDING,
                )
            )
            created += 1

        return created

    try:
        result, error = service_action(_ensure)
        if error or result is None:
            return 0
        return result
    except Exception:
        logger.exception("Falha em ensure_today_instances")
        return 0


def load_active_routine() -> tuple[int | None, str]:
    """Carrega rotina ativa. Retorna (id, nome) ou (None, "").

    Extrai escalares dentro da sessão para consistência com
    os demais loaders e prevenção de DetachedInstanceError
    em futuras expansões que acessem relationships.
    """

    def _load(s: Session) -> tuple[int | None, str]:
        routine = RoutineService(s).get_active_routine()
        if not routine:
            return None, ""
        return routine.id, routine.name

    try:
        result, error = service_action(_load)
        if error or not result:
            return None, ""
        return result
    except Exception:
        logger.exception("Falha em load_active_routine")
        return None, ""


def load_instances() -> list[dict]:
    """Carrega instâncias do dia como lista de dicts.

    Toda extração de dados (incluindo lazy relationships como inst.habit)
    é feita dentro do callback para evitar DetachedInstanceError.
    """

    def _load(s: Session) -> list[dict]:
        today = date.today()
        result = HabitInstanceService().list_instances(date_start=today, date_end=today, session=s)
        if not result:
            return []

        instances: list[dict] = []
        for inst in result:
            ss = inst.scheduled_start
            se = inst.scheduled_end
            start_min = (ss.hour * 60 + ss.minute) if ss else 0
            end_min = (se.hour * 60 + se.minute) if se else start_min + 60
            name = ""
            if inst.habit:
                name = inst.habit.title
            elif hasattr(inst, "habit_id"):
                name = f"Hábito #{inst.habit_id}"
            status = inst.status.value if inst.status else "pending"
            substatus = None
            if hasattr(inst, "done_substatus") and inst.done_substatus:
                substatus = inst.done_substatus.value
            elif hasattr(inst, "not_done_substatus") and inst.not_done_substatus:
                substatus = inst.not_done_substatus.value
            instances.append(
                {
                    "id": inst.id,
                    "name": name,
                    "start_minutes": start_min,
                    "end_minutes": end_min,
                    "status": status,
                    "substatus": substatus,
                    "actual_minutes": getattr(inst, "actual_duration", None),
                }
            )
        return instances

    try:
        result, error = service_action(_load)
        if error or not result:
            return []
        return result
    except Exception:
        logger.exception("Falha ao carregar instâncias")
        return []


def _task_proximity(days: int) -> str:
    """Retorna label de proximidade para exibição no painel."""
    if days < 0:
        return "Atrasada"
    if days == 0:
        return "Hoje"
    if days == 1:
        return "Amanhã"
    return f"Em {days}d"


def _build_task_dict(task: Any, status: str, proximity: str | None = None) -> dict:
    """Converte Task ORM em dict para consumo do TasksPanel.

    Extração centralizada para evitar duplicação entre pendentes
    e recentes (BR-TUI-003-R29).
    """
    today = date.today()
    nm = task.title[:20] if hasattr(task, "title") else str(task)[:20]
    dt = task.scheduled_datetime
    task_date = dt.date() if dt else today
    days = (task_date - today).days

    if dt and (dt.hour != 0 or dt.minute != 0):
        time_str = dt.strftime("%H:%M")
    else:
        time_str = "--:--"

    if proximity is None:
        proximity = _task_proximity(days)

    return {
        "id": task.id,
        "name": nm,
        "proximity": proximity,
        "date": dt.strftime("%d/%m") if dt else "",
        "time": time_str,
        "status": status,
        "days": days,
    }


def load_tasks() -> list[dict]:
    """Carrega tasks para o dashboard (BR-TUI-003-R29).

    Combina pendentes/overdue com concluídas e canceladas das últimas 24h.
    Pendentes/overdue têm prioridade dentro do limite de 9 items.
    Toda extração de dados é feita dentro do callback para consistência
    com os demais loaders e prevenção de DetachedInstanceError.
    """

    def _load(s: Session) -> list[dict]:
        # Pendentes + overdue (sem filtro temporal)
        pending = TaskService.list_pending_tasks(session=s)
        active_tasks: list[dict] = []
        for task in pending:
            status = task.derived_status  # "overdue" ou "pending"
            active_tasks.append(_build_task_dict(task, status))

        # Concluídas recentes (últimas 24h)
        completed = TaskService.list_recently_completed_tasks(hours=24, session=s)
        recent_tasks: list[dict] = []
        for task in completed:
            recent_tasks.append(_build_task_dict(task, "completed", "Concluída"))

        # Canceladas recentes (últimas 24h)
        cancelled = TaskService.list_recently_cancelled_tasks(hours=24, session=s)
        for task in cancelled:
            recent_tasks.append(_build_task_dict(task, "cancelled", "Cancelada"))

        # Pendentes/overdue têm prioridade, recentes preenchem o restante
        limit = 9
        result = active_tasks[:limit]
        remaining = limit - len(result)
        if remaining > 0:
            result.extend(recent_tasks[:remaining])

        return result

    try:
        result, error = service_action(_load)
        if error or not result:
            return []
        return result
    except Exception:
        logger.exception("Falha ao carregar tasks")
        return []


def load_active_timer() -> dict[str, Any] | None:
    """Carrega timer ativo como dict com elapsed MM:SS e nome do hábito (DT-016).

    Retorna dict compatível com TimerPanel:
        - id, status, elapsed (str MM:SS), name (str), habit_instance_id
    Ou None se nenhum timer ativo.
    """

    def _load(s: Session) -> dict[str, Any] | None:
        timer = TimerService.get_any_active_timer(session=s)
        if not timer or not timer.status:
            return None

        elapsed_secs = int(
            (datetime.now() - timer.start_time).total_seconds() - (timer.paused_duration or 0)
        )
        elapsed_secs = max(elapsed_secs, 0)
        minutes, seconds = divmod(elapsed_secs, 60)

        name = ""
        if timer.habit_instance_id:
            inst = s.exec(
                select(HabitInstance).where(HabitInstance.id == timer.habit_instance_id)
            ).first()
            if inst and inst.habit:
                name = inst.habit.title

        return {
            "id": timer.id,
            "status": timer.status.value,
            "elapsed": f"{minutes:02d}:{seconds:02d}",
            "elapsed_seconds": elapsed_secs,
            "name": name,
            "habit_instance_id": timer.habit_instance_id,
        }

    try:
        result, error = service_action(_load)
        if error or not result:
            return None
        return result
    except Exception:
        logger.exception("Falha em load_active_timer")
        return None


_WEEKDAYS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def load_metrics() -> dict:
    """Carrega métricas do dashboard (DT-017).

    Calcula streak global, completude 7d/30d e heatmap semanal
    a partir de HabitInstances da rotina ativa.
    """
    from datetime import timedelta

    def _load(s: Session) -> dict:
        today = date.today()

        # Busca instancias dos ultimos 30 dias
        cutoff_30d = today - timedelta(days=29)
        instances_30d = list(
            s.exec(
                select(HabitInstance)
                .where(HabitInstance.date >= cutoff_30d)
                .where(HabitInstance.date <= today)
            ).all()
        )

        if not instances_30d:
            return {
                "streak": 0,
                "best_streak": 0,
                "pct_7d": 0,
                "pct_30d": 0,
                "week_data": [],
            }

        # --- Completude 30d ---
        done_30d = sum(1 for i in instances_30d if i.status == Status.DONE)
        total_30d = len(instances_30d)
        pct_30d = int((done_30d / total_30d) * 100) if total_30d > 0 else 0

        # --- Completude 7d ---
        cutoff_7d = today - timedelta(days=6)
        instances_7d = [i for i in instances_30d if i.date >= cutoff_7d]
        done_7d = sum(1 for i in instances_7d if i.status == Status.DONE)
        total_7d = len(instances_7d)
        pct_7d = int((done_7d / total_7d) * 100) if total_7d > 0 else 0

        # --- Streak (BR-STREAK-001): dias consecutivos com todas DONE ---
        by_date: dict[date, list] = {}
        for inst in instances_30d:
            by_date.setdefault(inst.date, []).append(inst)

        streak = 0
        d = today
        while d >= cutoff_30d:
            day_instances = by_date.get(d, [])
            if not day_instances:
                d -= timedelta(days=1)
                continue
            all_done = all(i.status == Status.DONE for i in day_instances)
            if all_done:
                streak += 1
                d -= timedelta(days=1)
            else:
                break

        # --- Week data (heatmap semanal) ---
        week_data: list[tuple[str, int, int, str]] = []
        for offset in range(6, -1, -1):
            d = today - timedelta(days=offset)
            day_instances = by_date.get(d, [])
            total = len(day_instances)
            done = sum(1 for i in day_instances if i.status == Status.DONE)
            day_name = _WEEKDAYS_PT[d.weekday()]
            checks = " ".join(
                "\u2713" if i.status == Status.DONE else "\u00b7"
                for i in sorted(day_instances, key=lambda x: x.scheduled_start)
            )
            week_data.append((day_name, done, total, checks))

        return {
            "streak": streak,
            "best_streak": streak,  # TODO: persistir best_streak historico
            "pct_7d": pct_7d,
            "pct_30d": pct_30d,
            "week_data": week_data,
        }

    try:
        result, error = service_action(_load)
        if error or not result:
            return {}
        return result
    except Exception:
        logger.exception("Falha em load_metrics")
        return {}
