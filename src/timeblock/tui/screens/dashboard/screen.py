"""DashboardScreen - Coordinator do dashboard (BR-TUI-003, ADR-034).

Responsabilidade única: composição de layout, rastreamento de foco
e despacho de operações para loader e crud modules.

Referências:
    - BR-TUI-003: Dashboard Screen
    - ADR-034: Dashboard-first CRUD
    - RF-001: Extract Delegate (FOWLER, 2018, p. 182)
    - RF-003: Split Phase (FOWLER, 2018, p. 154)
"""

from datetime import date

from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Static

from timeblock.models.enums import SkipReason
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.task_service import TaskService
from timeblock.services.timer_service import TimerService
from timeblock.tui.screens.dashboard import crud_habits, crud_routines, crud_tasks, loader
from timeblock.tui.session import service_action
from timeblock.tui.widgets.agenda_panel import AgendaPanel
from timeblock.tui.widgets.confirm_dialog import ConfirmDialog
from timeblock.tui.widgets.focusable_panel import FocusablePanel
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.metrics_panel import MetricsPanel
from timeblock.tui.widgets.tasks_panel import TasksPanel
from timeblock.tui.widgets.timer_panel import TimerPanel
from timeblock.utils.logger import get_logger

logger = get_logger(__name__)


class DashboardScreen(Static):
    """Dashboard coordinator: compose + focus tracking + dispatch."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._focused_panel: str = ""
        self._active_routine_id: int | None = None
        self._active_routine_name: str = ""
        self._current_date: date = date.today()

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
        """Inicializa o dashboard (DT-023: garante instâncias do dia)."""
        loader.ensure_today_instances()
        self.refresh_data()
        self.app.set_focus(None)
        # BR-TUI-003-R15: auto-scroll na hora atual
        self.call_later(self._autoscroll_agenda)
        self.set_interval(1, self._tick_timer)
        self.set_interval(60, self._refresh_agenda)

    def _autoscroll_agenda(self) -> None:
        """Auto-scroll da agenda na hora atual (BR-TUI-003-R15)."""
        try:
            self.query_one(AgendaPanel).scroll_to_current_time()
        except Exception:
            pass  # Agenda pode nao estar montada ainda

    def on_descendant_focus(self, event) -> None:
        """Rastreia panel focado para CRUD contextual."""
        if event.widget and event.widget.id:
            self._focused_panel = event.widget.id

    # =========================================================================
    # Key Dispatch (ADR-034)
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
            crud_routines.open_create_routine(self.app, self._on_crud_done)
        elif self._focused_panel == "panel-habits":
            if self._active_routine_id:
                crud_habits.open_create_habit(self.app, self._active_routine_id, self._on_crud_done)
        elif self._focused_panel == "panel-tasks":
            crud_tasks.open_create_task(self.app, self._on_crud_done)

    def _handle_edit(self) -> None:
        """Despacha edição conforme contexto."""
        if self._focused_panel in ("", "agenda-content") and self._active_routine_id:
            crud_routines.open_edit_routine(
                self.app,
                self._active_routine_id,
                self._active_routine_name,
                self._on_crud_done,
            )
        elif self._focused_panel == "panel-habits":
            item = self.query_one(HabitsPanel).get_selected_item()
            if item:
                crud_habits.open_edit_habit(self.app, item, self._on_crud_done)
        elif self._focused_panel == "panel-tasks":
            item = self.query_one(TasksPanel).get_selected_item()
            if item:
                crud_tasks.open_edit_task(self.app, item, self._on_crud_done)

    def _handle_delete(self) -> None:
        """Despacha deleção conforme contexto."""
        if self._focused_panel in ("", "agenda-content") and self._active_routine_id:
            crud_routines.open_delete_routine(
                self.app,
                self._active_routine_id,
                self._active_routine_name,
                self._on_crud_done,
            )
        elif self._focused_panel == "panel-habits":
            item = self.query_one(HabitsPanel).get_selected_item()
            if item:
                crud_habits.open_delete_habit(self.app, item, self._on_crud_done)
        elif self._focused_panel == "panel-tasks":
            item = self.query_one(TasksPanel).get_selected_item()
            if item:
                crud_tasks.open_delete_task(self.app, item, self._on_crud_done)

    def _on_crud_done(self) -> None:
        """Callback universal: refresh após qualquer operação CRUD."""
        self.refresh_data()
        self._refresh_header()

    # =========================================================================
    # Quick Action Handlers — RF-001 (Extract Delegate)
    # =========================================================================

    def on_habits_panel_habit_done_request(self, message: HabitsPanel.HabitDoneRequest) -> None:
        """Recebe HabitDoneRequest e executa mark_completed via service."""
        service_action(
            lambda s: HabitInstanceService.mark_completed(message.instance_id, session=s)
        )
        self._on_crud_done()

    def on_habits_panel_habit_skip_request(self, message: HabitsPanel.HabitSkipRequest) -> None:
        """Recebe HabitSkipRequest e executa skip com categorização (BR-SKIP-001)."""
        service_action(
            lambda s: HabitInstanceService.skip_habit_instance(
                message.instance_id, skip_reason=SkipReason.OTHER, session=s
            )
        )
        self._on_crud_done()

    def on_tasks_panel_task_complete_request(self, message: TasksPanel.TaskCompleteRequest) -> None:
        """Recebe TaskCompleteRequest e executa complete_task via service."""
        service_action(lambda s: TaskService.complete_task(message.task_id, session=s))
        self._on_crud_done()

    # =========================================================================
    # Timer Handlers — BR-TUI-021
    # =========================================================================

    def on_habits_panel_timer_start_request(self, message: HabitsPanel.TimerStartRequest) -> None:
        """Recebe TimerStartRequest e inicia timer via TimerService."""
        service_action(lambda s: TimerService.start_timer(message.instance_id, session=s))
        self._on_crud_done()

    def on_timer_panel_timer_pause_request(self, message: TimerPanel.TimerPauseRequest) -> None:
        """Recebe TimerPauseRequest e pausa timer via TimerService."""
        service_action(lambda s: TimerService.pause_timer(message.timer_id, session=s))
        self._on_crud_done()

    def on_timer_panel_timer_resume_request(self, message: TimerPanel.TimerResumeRequest) -> None:
        """Recebe TimerResumeRequest e retoma timer via TimerService."""
        service_action(lambda s: TimerService.resume_timer(message.timer_id, session=s))
        self._on_crud_done()

    def on_timer_panel_timer_stop_request(self, message: TimerPanel.TimerStopRequest) -> None:
        """Recebe TimerStopRequest e para timer via TimerService."""
        service_action(lambda s: TimerService.stop_timer(message.timer_id, session=s))
        self._on_crud_done()

    def on_timer_panel_timer_cancel_request(self, message: TimerPanel.TimerCancelRequest) -> None:
        """Recebe TimerCancelRequest e abre ConfirmDialog antes de cancelar."""

        def on_confirm() -> None:
            service_action(lambda s: TimerService.cancel_timer(message.timer_id, session=s))
            self._on_crud_done()

        self.app.push_screen(
            ConfirmDialog(
                title="Cancelar Timer",
                message="Cancelar timer ativo? A sessão será descartada.",
                on_confirm=on_confirm,
            )
        )

    def _refresh_header(self) -> None:
        """Atualiza header bar após operação CRUD."""
        try:
            from timeblock.tui.widgets.header_bar import HeaderBar

            self.app.query_one(HeaderBar)._refresh_content()
        except Exception:
            logger.debug("HeaderBar indisponível para refresh")

    # =========================================================================
    # Data Loading (delegado para loader.py)
    # =========================================================================

    def on_focusable_panel_placeholder_activated(
        self, message: FocusablePanel.PlaceholderActivated
    ) -> None:
        """Enter em placeholder despacha criação contextual (BR-TUI-013)."""
        message.stop()
        if message.panel_id == "panel-habits":
            if self._active_routine_id:
                crud_habits.open_create_habit(self.app, self._active_routine_id, self._on_crud_done)
        elif message.panel_id == "panel-tasks":
            crud_tasks.open_create_task(self.app, self._on_crud_done)

    def _refresh_agenda(self) -> None:
        """Atualiza agenda e hábitos a cada 60s (DT-015, DT-023).

        Detecta virada de dia e gera instâncias faltantes.
        """
        today = date.today()
        if today != self._current_date:
            self._current_date = today
            loader.ensure_today_instances()
            self.refresh_data()
            return

        instances = loader.load_instances()
        try:
            self.query_one(AgendaPanel).update_data(instances)
            self.query_one(HabitsPanel).update_data(instances)
        except Exception:
            logger.debug("Panels indisponíveis durante refresh")

    def _tick_timer(self) -> None:
        """Atualiza TimerPanel a cada segundo (DT-015)."""
        timer = loader.load_active_timer()
        try:
            self.query_one(TimerPanel).update_data(timer)
        except Exception:
            logger.debug("TimerPanel indisponível durante tick")

    def refresh_data(self) -> None:
        """Carrega dados via loader e distribui para panels."""
        routine_id, routine_name = loader.load_active_routine()
        self._active_routine_id = routine_id
        self._active_routine_name = routine_name

        instances = loader.load_instances()
        tasks = loader.load_tasks()
        timer = loader.load_active_timer()

        try:
            self.query_one("#agenda-column").border_title = "Agenda do Dia"
            self.query_one("#agenda-header", Static).update("")
        except Exception:
            logger.debug("Layout parcial durante inicialização")

        self.query_one(AgendaPanel).update_data(instances)
        self.query_one(HabitsPanel).update_data(instances)
        self.query_one(TasksPanel).update_data(tasks)
        self.query_one(TimerPanel).update_data(timer)
        self.query_one(MetricsPanel).update_data({})
