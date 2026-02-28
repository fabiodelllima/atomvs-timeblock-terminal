"""DashboardScreen - Coordinator do dashboard (BR-TUI-003).

Responsabilidade única: composição de layout, carregamento de dados
e distribuição para os 5 panels especializados. Nenhuma lógica de
renderização — cada panel encapsula sua própria apresentação.
"""

from datetime import date

from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from timeblock.tui.mock_data import MOCK_INSTANCES, MOCK_TASKS, MOCK_TIMER
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
            from timeblock.services.routine_service import RoutineService

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
            from timeblock.services.habit_instance_service import HabitInstanceService

            today = date.today()
            result, error = service_action(
                lambda s: HabitInstanceService().list_instances(
                    date_start=today, date_end=today, session=s
                )
            )
            if error or not result:
                return MOCK_INSTANCES

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
            return MOCK_INSTANCES

    @staticmethod
    def _load_tasks() -> list[dict]:
        """Carrega tasks pendentes. Usa mock se banco vazio."""
        force_mock = True
        if force_mock:
            return MOCK_TASKS
        try:
            from timeblock.services.task_service import TaskService

            result, error = service_action(lambda s: TaskService.list_pending_tasks(session=s))
            if error or not result:
                return MOCK_TASKS
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
            return MOCK_TASKS

    @staticmethod
    def _get_active_timer() -> dict | None:
        """Obtém informação do timer ativo.

        TODO: Integrar com TimerService quando dashboard tiver
        contexto de habit_instance_id ativo.
        """
        return MOCK_TIMER
