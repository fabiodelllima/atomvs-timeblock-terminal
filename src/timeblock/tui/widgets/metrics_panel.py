"""MetricsPanel - Card de métricas com streak, completude e heatmap (BR-TUI-003).

BR-TUI-003 regra 6: Streak, barras 7d/30d, dot matrix semanal.
Cores das barras: Green >= 80%, Yellow 50-79%, Red < 50%.
"""

from typing import Any

from textual.widgets import Static

from timeblock.tui.colors import C_ERROR, C_MUTED, C_SUCCESS, C_SURFACE, C_WARNING


class MetricsPanel(Static):
    can_focus = True
    """Card de métricas com streak, completude e heatmap semanal."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def update_data(self, data: dict) -> None:
        """Recebe dados de métricas do coordinator e renderiza."""
        self._refresh_content(data)

    def _refresh_content(self, data: dict) -> None:
        """Constrói linhas do card e atualiza border_title + conteúdo."""
        pct_7d = data.get("pct_7d", 0)
        pct_30d = data.get("pct_30d", 0)
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
            f"  Completude 7d [dim]··[/dim]  {self._bar(pct_7d)}",
            f"  Completude 30d [dim]·[/dim]  {self._bar(pct_30d)}",
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
