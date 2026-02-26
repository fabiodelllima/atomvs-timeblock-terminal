"""MetricsPanel - Card de métricas com streak, completude e heatmap (BR-TUI-003).

BR-TUI-003 regra 6: Streak, barras 7d/30d, dot matrix semanal.
Cores das barras: Green >= 80%, Yellow 50-79%, Red < 50%.
"""

from datetime import datetime

from textual.widgets import Static

from timeblock.tui.colors import C_ERROR, C_SUCCESS, C_SURFACE, C_WARNING
from timeblock.tui.formatters import spaced_title


class MetricsPanel(Static):
    """Card de métricas com streak, completude e heatmap semanal."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def update_data(self, data: dict) -> None:
        """Recebe dados de métricas do coordinator e renderiza."""
        self._refresh_content(data)

    def _refresh_content(self, data: dict) -> None:
        """Constrói linhas do card e atualiza border_title + conteúdo."""
        now = datetime.now()
        pct_7d = data.get("pct_7d", 72)
        pct_30d = data.get("pct_30d", 63)
        streak = data.get("streak", 12)
        best_streak = data.get("best_streak", 28)

        week_data = data.get(
            "week_data",
            [
                ("Seg", 8, 10, "✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ · ·"),
                ("Ter", 9, 10, "✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ·"),
                ("Qua", 7, 10, "✓ ✓ ✓ ✓ ✓ ✓ ✓ · · ·"),
                ("Qui", 6, 10, "✓ ✓ ✓ ✓ ✓ ✓ · · · ·"),
            ],
        )

        self.border_title = spaced_title("Métricas", now.strftime("%H:%M"))

        lines = [
            (
                f"  Streak [dim]·········[/dim]  "
                f"[{C_WARNING}]{streak} dias[/{C_WARNING}]  "
                f"[dim](best: {best_streak})[/dim]"
            ),
            f"  Completude 7d [dim]··[/dim]  {self._bar(pct_7d)}",
            f"  Completude 30d [dim]·[/dim]  {self._bar(pct_30d)}",
            "",
        ]

        for day, d, t, checks in week_data:
            d_bar = int((d / t) * 10)
            e_bar = 10 - d_bar
            c = C_SUCCESS if d >= 8 else C_WARNING if d >= 6 else C_ERROR
            lines.append(
                f"  {day} [{c}]{'▪' * d_bar}[/{c}]"
                f"[{C_SURFACE}]{'░' * e_bar}[/{C_SURFACE}] {d}/{t}"
                f"  [dim]{checks}[/dim]"
            )

        lines.append(f"  [dim]{'':>36}← hoje[/dim]")
        lines.append("")
        lines.append(r"  [dim]\[f] 7d/14d/30d[/dim]")

        self.update("\n".join(lines))

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
