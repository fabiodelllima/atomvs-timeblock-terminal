"""StatusBar - Footer contextual com keybindings por panel (BR-TUI-007).

Layout: [rotina ativa] | [keybindings do panel focado] | [timer + hora]
O centro atualiza dinamicamente conforme o panel que recebe foco.
"""

from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

PANEL_KEYBINDINGS: dict[str, str] = {
    "agenda-content": "↑↓ navegar",
    "panel-habits": "j/i navegar  v done  s skip  t timer",
    "panel-tasks": "j/i navegar  v concluir  s adiar  c cancelar",
    "panel-timer": "space pausar  s parar  c cancelar",
    "panel-metrics": "f período",
}

DEFAULT_KEYBINDINGS = "Tab navegar  ? ajuda  Ctrl+Q sair"


class StatusBar(Widget):
    """Footer persistente com rotina, keybindings contextuais e timer+hora."""

    CLOCK_INTERVAL: int = 60
    TIMER_INTERVAL: int = 1

    routine_name: reactive[str] = reactive("")
    timer_elapsed: reactive[str] = reactive("")
    timer_status: reactive[str] = reactive("")
    focused_panel: reactive[str] = reactive("")

    def __init__(self) -> None:
        super().__init__(id="status-bar")

    def compose(self):
        """Compõe as três seções do footer."""
        yield Static(id="status-left")
        yield Static(id="status-center")
        yield Static(id="status-right")

    def on_mount(self) -> None:
        """Inicia timers de atualização."""
        self._update_all()
        self.set_interval(self.CLOCK_INTERVAL, self._update_clock)

    # =========================================================================
    # Section builders
    # =========================================================================

    def _build_left_section(self) -> str:
        """Rotina ativa ou placeholder."""
        if self.routine_name:
            return f" [bold]{self.routine_name}[/bold]"
        return " [dim][Sem rotina][/dim]"

    def _build_center_section(self) -> str:
        """Keybindings contextuais do panel focado."""
        panel_id = self.focused_panel
        keys = PANEL_KEYBINDINGS.get(panel_id, DEFAULT_KEYBINDINGS)
        if not keys:
            keys = DEFAULT_KEYBINDINGS
        return f"[dim]{keys}[/dim]"

    def _build_right_section(self) -> str:
        """Timer elapsed."""
        if self.timer_elapsed and self.timer_status:
            icon = "▶" if self.timer_status == "running" else "⏸"
            color = "#CBA6F7" if self.timer_status == "running" else "#F9E2AF"
            return f"[{color}]{icon} {self.timer_elapsed}[/{color}] "
        return ""

    # =========================================================================
    # Updates
    # =========================================================================

    def _update_all(self) -> None:
        """Atualiza as três seções."""
        try:
            self.query_one("#status-left", Static).update(self._build_left_section())
            self.query_one("#status-center", Static).update(self._build_center_section())
            self.query_one("#status-right", Static).update(self._build_right_section())
        except Exception:
            pass

    def _update_clock(self) -> None:
        """Atualiza seção direita a cada minuto."""
        try:
            self.query_one("#status-right", Static).update(self._build_right_section())
        except Exception:
            pass

    def update_focused_panel(self, panel_id: str) -> None:
        """Chamado pelo app quando foco muda entre panels."""
        self.focused_panel = panel_id

    # =========================================================================
    # Watchers
    # =========================================================================

    def watch_routine_name(self, _value: str) -> None:
        """Reage à mudança de rotina."""
        try:
            self.query_one("#status-left", Static).update(self._build_left_section())
        except Exception:
            pass

    def watch_focused_panel(self, _value: str) -> None:
        """Reage à mudança de panel focado."""
        try:
            self.query_one("#status-center", Static).update(self._build_center_section())
        except Exception:
            pass

    def watch_timer_elapsed(self, _value: str) -> None:
        """Reage à mudança de timer."""
        try:
            self.query_one("#status-right", Static).update(self._build_right_section())
        except Exception:
            pass

    def watch_timer_status(self, _value: str) -> None:
        """Reage à mudança de status do timer."""
        try:
            self.query_one("#status-right", Static).update(self._build_right_section())
        except Exception:
            pass
