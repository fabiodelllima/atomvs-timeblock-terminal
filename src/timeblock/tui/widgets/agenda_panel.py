"""AgendaPanel - Régua de horas com blocos coloridos por status (BR-TUI-003).

BR-TUI-003-R13: Régua adaptativa 06:00-22:00.
BR-TUI-003-R15: Auto-scroll na hora atual.
BR-TUI-003-R16: Marcador ▸ no slot atual.
BR-TUI-003-R17: Indicador de tempo livre.
BR-TUI-003-R26: Cores temporais na régua.
"""

from datetime import datetime

from textual.widgets import Static

from timeblock.tui.colors import (
    C_ACCENT,
    fill_char,
    fill_color,
    is_bold_status,
    status_color,
    status_icon,
    status_label,
)
from timeblock.tui.formatters import format_duration


class AgendaPanel(Static):
    """Agenda vertical com régua de 30min e blocos proporcionais."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._instances: list[dict] = []

    def update_data(self, instances: list[dict]) -> None:
        """Recebe instâncias do coordinator e renderiza."""
        self._instances = instances
        self._refresh_content()

    def _refresh_content(self) -> None:
        """Constrói régua + blocos e atualiza conteúdo."""
        self.border_title = "Agenda do Dia"
        self.update("\n".join(self._build_lines()))

    def _build_lines(self) -> list[str]:
        """Monta linhas da agenda com régua de 30min.

        Formato: horário ─┼─ nome · duração   ícone substatus
        Bold exclusivo em running/paused. Background colorido nos fills.
        Cada slot de 30min ocupa 2 linhas uniformes.
        """
        instances = self._instances
        now = datetime.now()
        cur_h, cur_m = now.hour, now.minute
        out: list[str] = []
        fw = 38  # fill width

        sorted_inst = sorted(instances, key=lambda x: x.get("start_hour", 0))

        # Mapeia slot index → (inst, role)
        slot_info: dict[int, tuple[dict, str]] = {}
        for inst in sorted_inst:
            sh = inst.get("start_hour", 0)
            eh = inst.get("end_hour", sh + 1)
            si, ei = sh * 2, eh * 2
            for i, s in enumerate(range(si, ei)):
                slot_info[s] = (inst, "start" if i == 0 else "fill")

        def _tl(h: int, m: int) -> str:
            if h == cur_h and m <= cur_m < m + 30:
                return f"[bold {C_ACCENT}]{now.strftime('%H:%M')}[/bold {C_ACCENT}]"
            return f"[dim]{h:02d}:{m:02d}[/dim]"

        for idx in range(12, 45):
            h = idx // 2
            m = (idx % 2) * 30
            tl = _tl(h, m)

            if idx in slot_info:
                inst, role = slot_info[idx]
                nm = inst.get("name", "")
                st = inst.get("status", "pending")
                sub = inst.get("substatus")
                dur = format_duration(inst.get("actual_minutes"))
                color = status_color(st, sub)
                icon = status_icon(st, sub)
                label = status_label(st, sub)
                fc = fill_char(st, sub)
                bold = is_bold_status(st)

                fcolor = fill_color(st, sub)
                fb = f"[{color}]▌[/{color}][{fcolor}]{fc * (fw - 1)}[/{fcolor}]"
                elapsed = f" {dur}" if dur and st in ("running", "paused") else ""
                if bold:
                    ind = f"[bold {color}]{icon} {label}{elapsed}[/bold {color}]"
                else:
                    ind = f"[{color}]{icon} {label}[/{color}]"

                if role == "start":
                    est_min = (inst.get("end_hour", 0) - inst.get("start_hour", 0)) * 60
                    est_dur = format_duration(est_min) if not dur else dur
                    if bold:
                        nm_fmt = f"[bold {color}]{nm}[/bold {color}]"
                        dur_fmt = f"[{color}]{est_dur}[/{color}]"
                    else:
                        nm_fmt = f"[{color}]{nm}[/{color}]"
                        dur_fmt = f"[dim]{est_dur}[/dim]"
                    out.append(f"  {tl} [dim]─┬─[/dim] {nm_fmt} [dim]·[/dim] {dur_fmt}  {ind}")
                    out.append(f"         [dim]│[/dim] {fb}")
                else:
                    out.append(f"  {tl}  [dim]│[/dim] {fb}")
                    out.append(f"         [dim]│[/dim] {fb}")
            else:
                out.append(f"  {tl}  [dim]│[/dim]")
                out.append("         [dim]│[/dim]")

        return out

    @staticmethod
    def find_block_at(instances: list[dict], hour: int, minute: int = 0) -> dict | None:
        """Encontra bloco que cobre o slot hora:minuto."""
        slot_min = hour * 60 + minute
        for inst in instances:
            start_min = inst.get("start_hour", 0) * 60
            end_min = inst.get("end_hour", 0) * 60
            if start_min <= slot_min < end_min:
                return inst
        return None
