"""NavBar - Barra de navegação horizontal."""

from textual.widgets import Static


class NavBar(Static):
    """Barra de navegação horizontal no rodapé."""

    DEFAULT_CSS = """
    NavBar {
        dock: bottom;
        height: 1;
        background: $surface;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._active = "dashboard"

    def on_mount(self) -> None:
        """Renderiza estado inicial."""
        self._render_bar()

    def update_active(self, screen_name: str) -> None:
        """Atualiza indicador da screen ativa."""
        self._active = screen_name
        self._render_bar()

    def _render_bar(self) -> None:
        """Renderiza a barra de navegação."""
        items = {
            "dashboard": "[D]Dashboard",
            "routines": "[R]Rotinas",
            "habits": "[H]Hábitos",
            "tasks": "[T]Tasks",
            "timer": "[M]Timer",
        }
        parts = []
        for key, label in items.items():
            if key == self._active:
                parts.append(f"[bold reverse] {label} [/]")
            else:
                parts.append(f"  {label}  ")
        self.update("  ".join(parts))
