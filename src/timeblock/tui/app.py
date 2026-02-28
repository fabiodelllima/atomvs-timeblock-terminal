"""TimeBlockApp - Aplicação TUI principal."""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical

from timeblock.tui.screens.dashboard import DashboardScreen
from timeblock.tui.screens.habits import HabitsScreen
from timeblock.tui.screens.routines import RoutinesScreen
from timeblock.tui.screens.tasks import TasksScreen
from timeblock.tui.screens.timer import TimerScreen
from timeblock.tui.widgets.header_bar import HeaderBar
from timeblock.tui.widgets.help_overlay import HelpOverlay
from timeblock.tui.widgets.nav_bar import NavBar
from timeblock.tui.widgets.status_bar import StatusBar

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

    CSS_PATH = "styles/theme.tcss"
    TITLE = "ATOMVS"

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("1", "switch_screen('dashboard')", "Dashboard", show=False),
        Binding("2", "switch_screen('routines')", "Rotinas", show=False),
        Binding("3", "switch_screen('habits')", "Hábitos", show=False),
        Binding("4", "switch_screen('tasks')", "Tasks", show=False),
        Binding("5", "switch_screen('timer')", "Timer", show=False),
        Binding("d", "switch_screen('dashboard')", "Dashboard", show=False),
        Binding("r", "switch_screen('routines')", "Rotinas", show=False),
        Binding("h", "switch_screen('habits')", "Hábitos", show=False),
        Binding("t", "switch_screen('tasks')", "Tasks", show=False),
        Binding("m", "switch_screen('timer')", "Timer", show=False),
        Binding("?", "toggle_help", "Ajuda", show=False),
        Binding("escape", "handle_escape", "Voltar", show=False),
        Binding("q", "quit", "Sair"),
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
        for name, screen_id in SCREEN_IDS.items():
            self.query_one(f"#{screen_id}").display = name == "dashboard"

    async def action_switch_screen(self, screen_name: str) -> None:
        """Alterna a screen ativa via display toggle."""
        if screen_name not in SCREENS or screen_name == self.active_screen:
            return

        self.query_one(f"#{SCREEN_IDS[self.active_screen]}").display = False

        self.active_screen = screen_name
        new_screen = self.query_one(f"#{SCREEN_IDS[screen_name]}")
        new_screen.display = True
        new_screen.focus()

        self.query_one(HeaderBar).update_screen(screen_name)
        self.query_one(NavBar).update_active(screen_name)

    async def action_toggle_help(self) -> None:
        """Exibe ou fecha o overlay de ajuda."""
        existing = self.query("#help-overlay")
        if existing:
            existing.first().remove()
        else:
            await self.mount(HelpOverlay())

    async def action_handle_escape(self) -> None:
        """Fecha modal aberto ou volta ao Dashboard."""
        help_overlay = self.query("#help-overlay")
        if help_overlay:
            help_overlay.first().remove()
        elif self.active_screen != "dashboard":
            await self.action_switch_screen("dashboard")
