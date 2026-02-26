"""HabitsPanel - Card de hábitos do dia com substatus e esforço (BR-TUI-003).

BR-TUI-003-R14: Subtítulo com dot matrix e percentual.
BR-TUI-003-R18: Effort bar proporcional.
BR-TUI-003-R19: Ordenação por start_time.
BR-TUI-003-R27: Nome herda cor do status.
"""

from textual.widgets import Static

from timeblock.tui.colors import (
    is_bold_status,
    status_color,
    status_icon,
)
from timeblock.tui.formatters import format_duration_card, spaced_title


class HabitsPanel(Static):
    """Card de hábitos com substatus DONE/NOT_DONE e barra de progresso."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._instances: list[dict] = []

    def update_data(self, instances: list[dict]) -> None:
        """Recebe instâncias do coordinator e renderiza."""
        self._instances = instances
        self._refresh_content()

    def _refresh_content(self) -> None:
        """Constrói linhas do card e atualiza border_title + conteúdo."""
        instances = self._instances
        done = sum(1 for i in instances if i["status"] == "done")
        total = len(instances)

        if total > 0:
            pct = int((done / total) * 100)
            dots = "●" * done + "○" * (total - done)
            self.border_title = spaced_title("Hábitos", f"{dots} {done}/{total} {pct}%")
        else:
            self.border_title = spaced_title("Hábitos", "0/0")

        self.update("\n".join(self._build_lines()))

    def _build_lines(self) -> list[str]:
        """Monta linhas de hábitos com ícone, nome, horário, duração e barra."""
        instances = self._instances
        lines: list[str] = []
        max_bars = 4

        if not instances:
            lines.append("  [dim]Nenhum hábito agendado[/dim]")
        else:
            for inst in instances[:12]:
                name = inst["name"][:16]
                st = inst["status"]
                sub = inst.get("substatus")
                actual = inst.get("actual_minutes")
                sh = inst.get("start_hour", 0)
                eh = inst.get("end_hour", 0)
                est_min = (eh - sh) * 60
                minutes = actual if actual else est_min
                dur = format_duration_card(minutes)
                color = status_color(st, sub)
                icon = status_icon(st, sub)
                bold = is_bold_status(st)

                # Ícone colorido
                if bold:
                    icon_fmt = f"[bold {color}]{icon:<2s}[/bold {color}]"
                else:
                    icon_fmt = f"[{color}]{icon:<2s}[/{color}]"

                # Nome herda cor do status (pending = neutro)
                if st == "pending":
                    nm_fmt = f"{name:<16s}"
                elif bold:
                    nm_fmt = f"[bold {color}]{name:<16s}[/bold {color}]"
                else:
                    nm_fmt = f"[{color}]{name:<16s}[/{color}]"

                # Horário com espaço ao redor do hífen
                time_fmt = f"[dim]{sh:02d}:00 - {eh:02d}:00[/dim]"

                # Duração zero-padded
                if bold:
                    dur_fmt = f"[{color}]{dur:>7s}[/{color}]"
                else:
                    dur_fmt = f"[dim]{dur:>7s}[/dim]"

                # Barra de progresso
                bar = self._build_bar(st, color, actual, est_min, max_bars)

                lines.append(f"  {icon_fmt} {nm_fmt} {time_fmt} {dur_fmt} {bar}")

        lines.append("")
        lines.append(r"  [dim]\[enter] done  \[s] skip  \[g] ir para screen[/dim]")
        return lines

    @staticmethod
    def _build_bar(status: str, color: str, actual: int | None, est_min: int, max_bars: int) -> str:
        """Constrói barra de progresso com quadradinhos."""
        sq = chr(9724)
        if status == "done":
            filled = min(max_bars, max(1, (actual or est_min) // 15))
            empty = max_bars - filled
            bar = f"[{color}]{sq * filled}[/{color}]"
            if empty > 0:
                bar += f"[dim]{sq * empty}[/dim]"
        elif status in ("running", "paused"):
            filled = min(max_bars, (actual or 0) // 15)
            empty = max_bars - filled
            bar = f"[{color}]{sq * filled}[/{color}]"
            if empty > 0:
                bar += f"[dim]{sq * empty}[/dim]"
        elif status == "not_done":
            bar = f"[dim]{'─' * max_bars}[/dim]"
        else:
            bar = f"[dim]{sq * max_bars}[/dim]"
        return bar
