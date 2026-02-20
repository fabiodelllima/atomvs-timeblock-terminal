"""TimeBlockApp - Aplicação TUI principal."""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header

from timeblock.tui.screens.dashboard import DashboardScreen
from timeblock.tui.widgets.nav_bar import NavBar

SCREENS = {
    "dashboard": "Dashboard",
    "routines": "Rotinas",
    "habits": "Hábitos",
    "tasks": "Tasks",
    "timer": "Timer",
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
        Binding("q", "quit", "Sair"),
    ]

    active_screen: str = "dashboard"

    def compose(self) -> ComposeResult:
        """Compõe o layout da aplicação."""
        yield Header()
        yield Container(
            DashboardScreen(id="dashboard-view"),
            id="content-area",
        )
        yield NavBar()
        yield Footer()

    async def action_switch_screen(self, screen_name: str) -> None:
        """Alterna a screen ativa."""
        if screen_name in SCREENS:
            self.active_screen = screen_name
            nav_bar = self.query_one(NavBar)
            nav_bar.update_active(screen_name)
