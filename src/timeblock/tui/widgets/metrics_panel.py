"""MetricsPanel - Card de métricas com streak, completude e heatmap (BR-TUI-003).

BR-TUI-003 regra 6: Streak, barras 7d/30d, dot matrix semanal.
BR-TUI-033-R7: Keybinding f alterna período (7d/14d/30d).
BR-TUI-033-R14: Texto mock removido do corpo do panel.
Cores das barras: Green >= 80%, Yellow 50-79%, Red < 50%.
"""

from typing import Any

from textual.events import Key
from textual.widgets import Static

from timeblock.tui.colors import C_ERROR, C_MUTED, C_SUCCESS, C_SURFACE, C_WARNING

PERIOD_CYCLE = [7, 14, 30]


class MetricsPanel(Static):
    can_focus = True
    """Card de métricas com streak, completude e heatmap semanal."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._period_days: int = 7
        self._last_data: dict = {}

    def _cycle_period(self) -> None:
        """Alterna período entre 7d/14d/30d (BR-TUI-033-R7)."""
        idx = PERIOD_CYCLE.index(self._period_days)
        self._period_days = PERIOD_CYCLE[(idx + 1) % len(PERIOD_CYCLE)]

    def on_key(self, event: Key) -> None:
        """Handler de teclado — f alterna período."""
        if event.key == "f":
            self._cycle_period()
            if self._last_data:
                self._refresh_content(self._last_data)
            event.stop()

    def update_data(self, data: dict) -> None:
        """Recebe dados de métricas do coordinator e renderiza."""
        self._last_data = data
        self._refresh_content(data)

    def _refresh_content(self, data: dict) -> None:
        """Constrói linhas do card e atualiza border_title + conteúdo."""
        pct_key = f"pct_{self._period_days}d"
        pct = data.get(pct_key, 0)
        streak = data.get("streak", 0)
        best_streak = data.get("best_streak", 0)
        week_data = data.get("week_data", [])

        self.border_title = "Métricas"
        self.border_subtitle = ""

        lines = [
            (
                f"  Streak [dim]·········[/dim]  "
                f"[{C_MUTED}]{streak} dias[/{C_MUTED}]  "
                f"[dim](best: {best_streak})[/dim]"
            ),
            f"  Completude {self._period_days}d {self._dots()}  {self._bar(pct)}",
            "",
        ]

        if week_data:
            for day, d, t, checks in week_data:
                d_bar = int((d / t) * 10) if t > 0 else 0
                e_bar = 10 - d_bar
                c = C_SUCCESS if d >= 8 else C_WARNING if d >= 6 else C_ERROR
                lines.append(
                    f"  {day} [{c}]{'▪' * d_bar}[/{c}]"
                    f"[{C_SURFACE}]{'░' * e_bar}[/{C_SURFACE}] {d}/{t}"
                    f"  [dim]{checks}[/dim]"
                )
            lines.append(f"  [dim]{'':>36}← hoje[/dim]")
        else:
            lines.append(f"  [{C_MUTED}]Sem dados de atividade[/{C_MUTED}]")

        lines.append("")
        self.update("\n".join(lines))

    def _dots(self) -> str:
        """Alinhamento de pontos conforme comprimento do label."""
        if self._period_days < 10:
            return "[dim]···[/dim]"
        return "[dim]··[/dim]"

    @staticmethod
    def _bar(pct: int) -> str:
        """Barra de progresso com cor por faixa."""
        filled = pct // 10
        empty = 10 - filled
        if pct >= 80:
            c = C_SUCCESS
        elif pct >= 50:
            c = C_WARNING
        else:
            c = C_ERROR
        return f"[{c}]{'▪' * filled}[/{c}][{C_SURFACE}]{'░' * empty}[/{C_SURFACE}]  {pct}%"
