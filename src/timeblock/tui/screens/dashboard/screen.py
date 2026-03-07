"""DashboardScreen - Coordinator do dashboard (BR-TUI-003, ADR-034).

Responsabilidade única: composição de layout, rastreamento de foco
e despacho de operações para loader e crud modules.

Referências:
    - BR-TUI-003: Dashboard Screen
    - ADR-034: Dashboard-first CRUD
    - RF-001: Extract Delegate (FOWLER, 2018, p. 182)
    - RF-003: Split Phase (FOWLER, 2018, p. 154)
"""

from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Static

from timeblock.tui.screens.dashboard import crud_routines, loader
from timeblock.tui.widgets.agenda_panel import AgendaPanel
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.metrics_panel import MetricsPanel
from timeblock.tui.widgets.tasks_panel import TasksPanel
from timeblock.tui.widgets.timer_panel import TimerPanel


class DashboardScreen(Static):
    """Dashboard coordinator: compose + focus tracking + dispatch."""

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
            pass  # Sprint 4c
        elif self._focused_panel == "panel-tasks":
            pass  # Sprint 4d

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
            pass  # Sprint 4c
        elif self._focused_panel == "panel-tasks":
            pass  # Sprint 4d

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
            pass  # Sprint 4c
        elif self._focused_panel == "panel-tasks":
            pass  # Sprint 4d

    def _on_crud_done(self) -> None:
        """Callback universal: refresh após qualquer operação CRUD."""
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
    # Data Loading (delegado para loader.py)
    # =========================================================================

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
            pass

        self.query_one(AgendaPanel).update_data(instances)
        self.query_one(HabitsPanel).update_data(instances)
        self.query_one(TasksPanel).update_data(tasks)
        self.query_one(TimerPanel).update_data(timer)
        self.query_one(MetricsPanel).update_data({})
