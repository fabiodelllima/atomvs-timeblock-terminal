"""Dashboard data loader (RF-003, BR-TUI-009).

Responsabilidade única: buscar dados via services e transformar
em dicts para consumo dos panels. Nenhuma lógica de apresentação.

Referências:
    - RF-003: Split Phase (FOWLER, 2018, p. 154)
    - BR-TUI-009: Service Layer Sharing
"""

from datetime import date, datetime

from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.routine_service import RoutineService
from timeblock.services.task_service import TaskService
from timeblock.services.timer_service import TimerService
from timeblock.tui.session import service_action


def load_active_routine() -> tuple[int | None, str]:
    """Carrega rotina ativa. Retorna (id, nome) ou (None, "")."""
    result, error = service_action(lambda s: RoutineService(s).get_active_routine())
    if not error and result:
        return result.id, result.name
    return None, ""


def load_instances() -> list[dict]:
    """Carrega instâncias do dia como lista de dicts."""
    try:
        today = date.today()
        result, error = service_action(
            lambda s: HabitInstanceService().list_instances(
                date_start=today, date_end=today, session=s
            )
        )
        if error or not result:
            return []

        instances: list[dict] = []
        for inst in result:
            start_h = inst.scheduled_start.hour if inst.scheduled_start else 0
            end_h = inst.scheduled_end.hour if inst.scheduled_end else 0
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
                    "start_hour": start_h,
                    "end_hour": end_h,
                    "status": status,
                    "substatus": substatus,
                    "actual_minutes": getattr(inst, "actual_duration", None),
                }
            )
        return instances
    except Exception:
        return []


def load_tasks() -> list[dict]:
    """Carrega tasks pendentes como lista de dicts."""
    try:
        result, error = service_action(lambda s: TaskService.list_pending_tasks(session=s))
        if error or not result:
            return []
        tasks: list[dict] = []
        for task in result[:9]:
            nm = task.title[:20] if hasattr(task, "title") else str(task)[:20]
            tasks.append(
                {
                    "id": task.id,
                    "name": nm,
                    "proximity": "",
                    "date": "",
                    "time": "--:--",
                    "status": "pending",
                    "days": 0,
                }
            )
        return tasks
    except Exception:
        return []


def load_active_timer() -> dict | None:
    """Carrega timer ativo como dict ou None."""
    try:
        result, error = service_action(lambda s: TimerService.get_any_active_timer(session=s))
        if error or not result:
            return None
        elapsed = (datetime.now() - result.start_time).total_seconds() - (
            result.paused_duration or 0
        )
        timer_status = result.status
        if timer_status is None:
            return None
        return {
            "id": result.id,
            "status": timer_status.value,
            "elapsed_seconds": int(elapsed),
            "habit_instance_id": result.habit_instance_id,
        }
    except Exception:
        return None
