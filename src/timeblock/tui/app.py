"""ATOMVS - Aplicação TUI"""

from pathlib import PurePath
from typing import Any, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical

from timeblock.services.backup_service import create_backup
from timeblock.tui.screens.dashboard import DashboardScreen
from timeblock.tui.screens.habits import HabitsScreen
from timeblock.tui.screens.routines import RoutinesScreen
from timeblock.tui.screens.tasks import TasksScreen
from timeblock.tui.screens.timer import TimerScreen
from timeblock.tui.widgets.header_bar import HeaderBar
from timeblock.tui.widgets.help_overlay import HelpOverlay
from timeblock.tui.widgets.nav_bar import NavBar
from timeblock.tui.widgets.status_bar import StatusBar
from timeblock.utils.logger import get_logger

logger = get_logger(__name__)

SCREENS = {
    "dashboard": "Dashboard",
    "routines": "Rotinas",
    "habits": "Hábitos",
    "tasks": "Tasks",
    "timer": "Timer",
}

SCREEN_IDS = {
    "dashboard": "dashboard-view",
    "routines": "routines-view",
    "habits": "habits-view",
    "tasks": "tasks-view",
    "timer": "timer-view",
}


class TimeBlockApp(App):
    """ATOMVS TimeBlock - TUI Interface."""

    CSS_PATH: ClassVar[str | PurePath | list[str | PurePath] | None] = [
        "styles/base.tcss",
        "styles/layout.tcss",
        "styles/cards.tcss",
        "styles/dashboard.tcss",
        "styles/statusbar.tcss",
        "styles/timer.tcss",
        "styles/forms.tcss",
    ]
    TITLE = "ATOMVS"

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("1", "switch_screen('dashboard')", "Dashboard", show=False),
        Binding("2", "switch_screen('routines')", "Rotinas", show=False),
        Binding("3", "switch_screen('habits')", "Hábitos", show=False),
        Binding("4", "switch_screen('tasks')", "Tasks", show=False),
        Binding("5", "switch_screen('timer')", "Timer", show=False),
        Binding("?", "toggle_help", "Ajuda", show=False),
        Binding("escape", "handle_escape", "Voltar", show=False),
        Binding("ctrl+q", "quit", "Sair"),
    ]

    active_screen: str = "dashboard"

    def compose(self) -> ComposeResult:
        """Compõe layout: sidebar | (header + content)."""
        with Horizontal(id="main-layout"):
            yield NavBar(id="sidebar")
            with Vertical(id="content-area"):
                yield HeaderBar(id="header-bar")
                yield Container(
                    DashboardScreen(id="dashboard-view"),
                    RoutinesScreen(id="routines-view"),
                    HabitsScreen(id="habits-view"),
                    TasksScreen(id="tasks-view"),
                    TimerScreen(id="timer-view"),
                    id="screen-container",
                )
        yield StatusBar()

    def on_mount(self) -> None:
        """Oculta todas as screens exceto Dashboard."""
        logger.info("TUI inicializada — screen: dashboard")
        for name, screen_id in SCREEN_IDS.items():
            self.query_one(f"#{screen_id}").display = name == "dashboard"

    def _handle_exception(self, error: Exception) -> None:
        """Loga exceções não capturadas antes de delegar ao Textual.

        O Textual exibe traceback visual e encerra o app. Este override
        garante que o erro também fique registrado no arquivo JSON Lines
        para consulta posterior.
        """
        logger.critical(
            "Exceção não capturada na TUI: %s: %s",
            type(error).__name__,
            error,
            exc_info=True,
        )
        super()._handle_exception(error)

    async def action_switch_screen(self, screen: str) -> None:
        """Alterna a screen ativa via display toggle."""
        if screen not in SCREENS or screen == self.active_screen:
            return

        self.query_one(f"#{SCREEN_IDS[self.active_screen]}").display = False

        self.active_screen = screen
        new_screen = self.query_one(f"#{SCREEN_IDS[screen]}")
        new_screen.display = True

        refresh = getattr(new_screen, "refresh_data", None)
        if refresh is not None:
            refresh()
        new_screen.focus()

        self.query_one(HeaderBar).update_screen(screen)
        self.query_one(NavBar).update_active(screen)
        logger.debug("Screen alterada: %s", screen)

    def on_descendant_focus(self, event: Any) -> None:
        """Atualiza footer quando foco muda entre panels (DT-066)."""
        widget = event.widget
        if widget and widget.id:
            try:
                hint = ""
                if getattr(widget, "_showing_placeholders", False):
                    hint = getattr(widget, "_placeholder_hint", "")
                self.query_one(StatusBar).update_focused_panel(widget.id, context_hint=hint)
            except Exception:
                logger.debug("Falha ao atualizar status bar para widget %s", widget.id)

    async def action_toggle_help(self) -> None:
        """Exibe ou fecha o overlay de ajuda."""
        existing = self.query("#help-overlay")
        if existing:
            existing.first().remove()
        else:
            await self.mount(HelpOverlay())

    async def action_handle_escape(self) -> None:
        """Fecha modal, deseleciona panels ou volta ao Dashboard."""
        help_overlay = self.query("#help-overlay")
        if help_overlay:
            help_overlay.first().remove()
        elif self.active_screen != "dashboard":
            await self.action_switch_screen("dashboard")
        else:
            self.set_focus(None)

    async def action_quit(self) -> None:
        """Faz backup e encerra a aplicação."""
        logger.info("Encerrando TUI — backup de shutdown")
        create_backup(label="shutdown")
        self.exit()
