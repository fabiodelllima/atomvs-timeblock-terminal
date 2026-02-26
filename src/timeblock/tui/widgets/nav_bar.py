"""Sidebar - Navegação vertical lateral (BR-TUI-002).

Substitui NavBar horizontal. Sidebar fixa de 22 chars com:
- Logo ATOMVS no topo
- 5 screens com indicador da ativa
- Keybindings de referência no rodapé
"""

from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

SIDEBAR_ITEMS = {
    "dashboard": "Dash",
    "routines": "Rotin",
    "habits": "Habit",
    "tasks": "Tasks",
    "timer": "Timer",
}


class NavBar(Widget):
    """Sidebar de navegação vertical lateral."""

    active_screen: reactive[str] = reactive("dashboard")

    def compose(self):
        """Compõe layout da sidebar."""
        yield Vertical(
            Static(id="sidebar-logo"),
            Static(id="sidebar-nav"),
            Static(id="sidebar-footer"),
            id="sidebar-inner",
        )

    def on_mount(self) -> None:
        """Renderiza estado inicial."""
        self._render_logo()
        self._render_nav()
        self._render_footer()

    def update_active(self, screen_name: str) -> None:
        """Atualiza indicador da screen ativa."""
        self.active_screen = screen_name

    def watch_active_screen(self, _value: str) -> None:
        """Reage à mudança de screen ativa."""
        self._render_nav()

    def _render_logo(self) -> None:
        """Renderiza logo ATOMVS."""
        try:
            self.query_one("#sidebar-logo", Static).update(
                "[bold #CBA6F7]◉ ATOMVS[/bold #CBA6F7]\n[#45475A]═══════════════════[/#45475A]"
            )
        except Exception:
            pass

    def _render_nav(self) -> None:
        """Renderiza itens de navegação."""
        lines = []
        for key, label in SIDEBAR_ITEMS.items():
            if key == self.active_screen:
                lines.append(f"[bold #CBA6F7]▸ {label}[/bold #CBA6F7]")
            else:
                lines.append(f"[#6C7086]  {label}[/#6C7086]")

        try:
            self.query_one("#sidebar-nav", Static).update("\n".join(lines))
        except Exception:
            pass

    def _render_footer(self) -> None:
        """Renderiza keybindings de referência."""
        try:
            self.query_one("#sidebar-footer", Static).update(
                "[#45475A]───────────────────[/#45475A]\n[dim]q quit[/dim]\n[dim]? help[/dim]"
            )
        except Exception:
            pass
