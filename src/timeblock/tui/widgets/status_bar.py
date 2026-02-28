"""StatusBar widget para BR-TUI-007.

Barra de status persistente no rodapé com três seções:
- Esquerda: rotina ativa (ou '[Sem rotina]')
- Centro: timer ativo com tempo decorrido (se houver)
- Direita: hora atual HH:MM
"""

from datetime import datetime

from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class StatusBar(Widget):
    """Barra de status persistente no rodapé da TUI."""

    CLOCK_INTERVAL: int = 60
    TIMER_INTERVAL: int = 1

    routine_name: reactive[str] = reactive("")
    timer_habit: reactive[str] = reactive("")
    timer_elapsed: reactive[str] = reactive("")

    def __init__(self) -> None:
        super().__init__(id="status-bar")

    def compose(self):
        """Compõe as três seções da status bar."""
        yield Static(id="status-left")
        yield Static(id="status-center")
        yield Static(id="status-right")

    def on_mount(self) -> None:
        """Inicia timers de atualização."""
        self._update_clock()
        self._update_display()
        self.set_interval(self.CLOCK_INTERVAL, self._update_clock)

    def _build_left_section(self) -> str:
        """Constrói texto da seção esquerda (rotina)."""
        if self.routine_name:
            return f" [bold]{self.routine_name}[/bold]"
        return " [dim][Sem rotina][/dim]"

    def _build_center_section(self) -> str:
        """Constrói texto da seção central (timer)."""
        if self.timer_habit and self.timer_elapsed:
            return f"▶ [bold]{self.timer_habit}[/bold] {self.timer_elapsed}"
        return ""

    def _build_right_section(self) -> str:
        """Constrói texto da seção direita (hora)."""
        now = datetime.now()
        return f"{now.strftime('%H:%M')} "

    def _update_clock(self) -> None:
        """Atualiza hora na seção direita."""
        try:
            self.query_one("#status-right", Static).update(self._build_right_section())
        except Exception:
            pass

    def _update_display(self) -> None:
        """Atualiza seções esquerda e central."""
        try:
            self.query_one("#status-left", Static).update(self._build_left_section())
            self.query_one("#status-center", Static).update(self._build_center_section())
        except Exception:
            pass

    def watch_routine_name(self, _value: str) -> None:
        """Reage à mudança de rotina."""
        self._update_display()

    def watch_timer_habit(self, _value: str) -> None:
        """Reage à mudança de timer."""
        self._update_display()

    def watch_timer_elapsed(self, _value: str) -> None:
        """Reage à mudança de elapsed."""
        self._update_display()
