"""DashboardScreen - Coordinator do dashboard (BR-TUI-003, BR-TUI-016).

Responsabilidade única: composição de layout, carregamento de dados,
distribuição para os 5 panels especializados e orquestração de CRUD
via modais contextuais (ADR-034).
"""

from datetime import date, datetime

from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Static

from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.routine_service import RoutineService
from timeblock.services.task_service import TaskService
from timeblock.services.timer_service import TimerService
from timeblock.tui.session import service_action
from timeblock.tui.widgets.agenda_panel import AgendaPanel
from timeblock.tui.widgets.confirm_dialog import ConfirmDialog
from timeblock.tui.widgets.form_modal import FormField, FormModal
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.metrics_panel import MetricsPanel
from timeblock.tui.widgets.tasks_panel import TasksPanel
from timeblock.tui.widgets.timer_panel import TimerPanel


class DashboardScreen(Static):
    """Dashboard coordinator: compose + load + distribute + CRUD."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._focused_panel: str = ""
        self._active_routine_id: int | None = None
        self._active_routine_name: str = ""

    @staticmethod
    def get_no_routine_label() -> str:
        """Retorna mensagem quando não há rotina ativa."""
        return "[Nenhuma rotina ativa] - Crie uma com: n"

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
        self.app.set_focus(None)

    def on_descendant_focus(self, event) -> None:
        """Rastreia panel focado para CRUD contextual."""
        if event.widget and event.widget.id:
            self._focused_panel = event.widget.id

    # =========================================================================
    # Key Handler — CRUD contextual (BR-TUI-016, BR-TUI-017, BR-TUI-018)
    # =========================================================================

    def on_key(self, event: Key) -> None:
        """Intercepta n/e/x e despacha conforme panel focado."""
        if event.key == "n":
            self._handle_create()
            event.stop()
        elif event.key == "e":
            self._handle_edit()
            event.stop()
        elif event.key == "x":
            self._handle_delete()
            event.stop()

    def _handle_create(self) -> None:
        """Despacha criação conforme contexto."""
        if self._focused_panel in ("", "agenda-content"):
            self._create_routine()
        elif self._focused_panel == "panel-habits":
            pass  # Sprint 4c
        elif self._focused_panel == "panel-tasks":
            pass  # Sprint 4d

    def _handle_edit(self) -> None:
        """Despacha edição conforme contexto."""
        if self._focused_panel in ("", "agenda-content"):
            self._edit_routine()
        elif self._focused_panel == "panel-habits":
            pass  # Sprint 4c
        elif self._focused_panel == "panel-tasks":
            pass  # Sprint 4d

    def _handle_delete(self) -> None:
        """Despacha deleção conforme contexto."""
        if self._focused_panel in ("", "agenda-content"):
            self._delete_routine()
        elif self._focused_panel == "panel-habits":
            pass  # Sprint 4c
        elif self._focused_panel == "panel-tasks":
            pass  # Sprint 4d

    # =========================================================================
    # CRUD Rotinas (BR-TUI-016)
    # =========================================================================

    def _create_routine(self) -> None:
        """Abre FormModal para criar rotina."""
        fields = [
            FormField(name="name", label="Nome da rotina", required=True),
        ]
        self.app.push_screen(
            FormModal(
                title="Nova Rotina",
                fields=fields,
                on_submit=self._on_routine_created,
            )
        )

    def _on_routine_created(self, data: dict) -> None:
        """Callback: cria rotina e ativa automaticamente."""
        result, error = service_action(
            lambda s: RoutineService(s).create_routine(data["name"], auto_activate=True)
        )
        if not error and result:
            self._active_routine_id = result.id
            self._active_routine_name = result.name
            self.refresh_data()
            self._refresh_header()

    def _edit_routine(self) -> None:
        """Abre FormModal para editar rotina ativa."""
        if not self._active_routine_id:
            return
        fields = [
            FormField(name="name", label="Nome da rotina", required=True),
        ]
        self.app.push_screen(
            FormModal(
                title="Editar Rotina",
                fields=fields,
                edit_data={"name": self._active_routine_name},
                on_submit=self._on_routine_edited,
            )
        )

    def _on_routine_edited(self, data: dict) -> None:
        """Callback: atualiza nome da rotina ativa."""
        if not self._active_routine_id:
            return
        rid = self._active_routine_id
        result, error = service_action(
            lambda s: RoutineService(s).update_routine(rid, name=data["name"])
        )
        if not error and result:
            self._active_routine_name = result.name
            self._refresh_header()

    def _delete_routine(self) -> None:
        """Abre ConfirmDialog para deletar rotina ativa."""
        if not self._active_routine_id:
            return
        self.app.push_screen(
            ConfirmDialog(
                title="Deletar Rotina",
                message=f"Deletar '{self._active_routine_name}'?",
                on_confirm=self._on_routine_deleted,
            )
        )

    def _on_routine_deleted(self) -> None:
        """Callback: deleta rotina ativa e limpa panels."""
        if not self._active_routine_id:
            return
        rid = self._active_routine_id
        service_action(lambda s: RoutineService(s).delete_routine(rid))
        self._active_routine_id = None
        self._active_routine_name = ""
        self.refresh_data()
        self._refresh_header()

    def _refresh_header(self) -> None:
        """Atualiza header bar após operação CRUD."""
        try:
            from timeblock.tui.widgets.header_bar import HeaderBar

            self.app.query_one(HeaderBar)._refresh_content()
        except Exception:
            pass

    # =========================================================================
    # Data Loading
    # =========================================================================

    def refresh_data(self) -> None:
        """Carrega dados e distribui para os panels."""
        self._load_active_routine()
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

    def _load_active_routine(self) -> None:
        """Carrega rotina ativa e armazena ID/nome."""
        result, error = service_action(lambda s: RoutineService(s).get_active_routine())
        if not error and result:
            self._active_routine_id = result.id
            self._active_routine_name = result.name
        else:
            self._active_routine_id = None
            self._active_routine_name = ""

    @staticmethod
    def _load_instances() -> list[dict]:
        """Carrega instâncias do dia."""
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

    @staticmethod
    def _load_tasks() -> list[dict]:
        """Carrega tasks pendentes."""
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
