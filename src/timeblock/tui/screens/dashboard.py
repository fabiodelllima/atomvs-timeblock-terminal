"""DashboardScreen - Coordinator do dashboard (BR-TUI-003).

Responsabilidade única: composição de layout, carregamento de dados
e distribuição para os 5 panels especializados. Nenhuma lógica de
renderização — cada panel encapsula sua própria apresentação.
"""

from datetime import date, datetime

from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.routine_service import RoutineService
from timeblock.services.task_service import TaskService
from timeblock.services.timer_service import TimerService
from timeblock.tui.session import service_action
from timeblock.tui.widgets.agenda_panel import AgendaPanel
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.metrics_panel import MetricsPanel
from timeblock.tui.widgets.tasks_panel import TasksPanel
from timeblock.tui.widgets.timer_panel import TimerPanel


class DashboardScreen(Static):
    """Dashboard coordinator: compose + load + distribute."""

    @staticmethod
    def get_no_routine_label() -> str:
        """Retorna mensagem quando não há rotina ativa."""
        return "[Nenhuma rotina ativa] - Crie uma com: timeblock routine add"

    def compose(self):
        """Compõe layout: agenda esquerda + panels direita."""
        with Horizontal(id="dashboard-layout"):
            yield Vertical(
                Static(id="agenda-header"),
                AgendaPanel(id="agenda-content"),
                id="agenda-column",
            )
            yield Vertical(
                HabitsPanel(id="panel-habits"),
                TasksPanel(id="panel-tasks"),
                TimerPanel(id="panel-timer"),
                MetricsPanel(id="panel-metrics"),
                id="panels-column",
            )

    def on_mount(self) -> None:
        """Inicializa o dashboard."""
        self.refresh_data()

    def refresh_data(self) -> None:
        """Carrega dados e distribui para os panels."""
        instances = self._load_instances()
        tasks = self._load_tasks()
        timer = self._get_active_timer()

        try:
            self.query_one("#agenda-column").border_title = "Agenda do Dia"
            self.query_one("#agenda-header", Static).update("")
        except Exception:
            pass

        self.query_one(AgendaPanel).update_data(instances)
        self.query_one(HabitsPanel).update_data(instances)
        self.query_one(TasksPanel).update_data(tasks)
        self.query_one(TimerPanel).update_data(timer)
        self.query_one(MetricsPanel).update_data({})

    # =========================================================================
    # Data Loaders
    # =========================================================================

    @staticmethod
    def _get_routine_name() -> str:
        """Obtém nome da rotina ativa."""
        try:
            result, error = service_action(lambda s: RoutineService(s).get_active_routine())
            if error or not result:
                return "Rotina Demo"
            return result.name
        except Exception:
            return "Rotina Demo"

    @staticmethod
    def _load_instances() -> list[dict]:
        """Carrega instâncias do dia. Usa mock se banco vazio."""
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

    @staticmethod
    def _load_tasks() -> list[dict]:
        """Carrega tasks pendentes. Usa mock se banco vazio."""
        try:
            result, error = service_action(lambda s: TaskService.list_pending_tasks(session=s))
            if error or not result:
                return []
            tasks: list[dict] = []
            for task in result[:9]:
                nm = task.title[:20] if hasattr(task, "title") else str(task)[:20]
                tasks.append(
                    {
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

    @staticmethod
    @staticmethod
    def _get_active_timer() -> dict | None:
        """Obtém informação do timer ativo (BR-TIMER-001)."""
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
