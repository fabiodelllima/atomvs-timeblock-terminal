"""TimerPanel - Card compacto do timer com ASCII art (BR-TUI-003).

BR-TUI-003-R25: Timer card compacto (sem ASCII art no dashboard v2).
BR-TUI-003-R27: Cores por estado (Mauve running, Yellow paused, Overlay0 idle).
"""

from textual.widgets import Static

from timeblock.tui.colors import C_ACCENT, C_MUTED, C_WARNING
from timeblock.tui.formatters import render_ascii_time, spaced_title


class TimerPanel(Static):
    """Card do timer com elapsed em ASCII art grande."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._timer_info: dict | None = None

    def update_data(self, timer_info: dict | None) -> None:
        """Recebe info do timer do coordinator e renderiza."""
        self._timer_info = timer_info
        self._refresh_content()

    def _refresh_content(self) -> None:
        """Constrói linhas do card e atualiza border_title + conteúdo."""
        if self._timer_info:
            lines = self._build_active_lines()
        else:
            lines = self._build_idle_lines()
        self.update("\n".join(lines))

    def _build_active_lines(self) -> list[str]:
        """Monta linhas para timer ativo (running ou paused)."""
        assert self._timer_info is not None
        info = self._timer_info
        elapsed = info.get("elapsed", "00:00")
        name = info.get("name", "")
        st = info.get("status", "running")

        if st == "paused":
            color = C_WARNING
            icon = "⏸"
            label = "pausado"
            self.border_title = spaced_title("Timer", "⏸ paused")
        else:
            color = C_ACCENT
            icon = "▶"
            label = "em andamento"
            self.border_title = spaced_title("Timer", "▶ ativo")

        art = render_ascii_time(elapsed)
        lines = [""]
        for row in art:
            lines.append(f"    [bold {color}]{row}[/bold {color}]")
        lines.append("")
        lines.append(f"    [{color}]{icon} {label}[/{color}]  {name}")
        lines.append("")
        lines.append(r"  [dim]\[p] pausar  \[enter] parar  \[c] cancelar[/dim]")
        return lines

    def _build_idle_lines(self) -> list[str]:
        """Monta linhas para timer idle."""
        self.border_title = spaced_title("Timer", "idle")
        art = render_ascii_time("00:00")
        lines = [""]
        for row in art:
            lines.append(f"    [{C_MUTED}]{row}[/{C_MUTED}]")
        lines.append("")
        lines.append(f"    [{C_MUTED}]⏹ idle[/{C_MUTED}]")
        return lines
