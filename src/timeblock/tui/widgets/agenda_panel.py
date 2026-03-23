"""AgendaPanel - Régua de horas com blocos coloridos por status.

BR-TUI-003-R13: Régua adaptativa 05:00-23:30.
BR-TUI-003-R15: Auto-scroll na hora atual.
BR-TUI-031: Scroll horizontal para multi-coluna.
BR-TUI-032: Renderização de blocos contínuos com granularidade de 15min.
"""

from datetime import datetime

from textual.containers import ScrollableContainer
from textual.widget import Widget
from textual.widgets import Static

from timeblock.tui.colors import (
    C_ACCENT,
    C_TEXT,
    fill_char,
    fill_color,
    is_bold_status,
    status_color,
    status_icon,
)


def compute_agenda_range(instances: list[dict]) -> tuple[int, int]:
    """Calcula range de slots da régua baseado nos eventos (BR-TUI-003-R13).

    Retorna (start_slot, end_slot) com range minimo 05:00-23:30
    (slots 10-47). Eventos fora desse intervalo expandem o range
    com 1h de padding (2 slots).
    """
    default_start, default_end = 10, 47  # 05:00-23:30

    if not instances:
        return default_start, default_end

    first_slot = min(i["start_minutes"] // 30 for i in instances)
    last_slot = max(-(-i["end_minutes"] // 30) for i in instances)  # ceil

    range_start = max(0, first_slot - 2)  # 1h padding antes
    range_end = min(47, last_slot + 2)  # 1h padding depois

    range_start = min(range_start, default_start)  # nunca acima de 05:00
    range_end = max(range_end, default_end)  # nunca abaixo de 23:30

    return range_start, range_end


class AgendaPanel(Widget):
    can_focus = True
    """Agenda com horas fixas e blocos scrolláveis horizontalmente (BR-TUI-031)."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._instances: list[dict] = []

    def compose(self):
        """Estrutura interna: horas fixas + blocos scrolláveis (ADR-041-19)."""
        yield Static(id="agenda-hours")
        with ScrollableContainer(id="agenda-blocks-scroll", can_focus=False):
            yield Static(id="agenda-blocks")

    def update_data(self, instances: list[dict]) -> None:
        """Recebe instâncias do coordinator e renderiza."""
        self._instances = instances
        self._refresh_content()

    def _refresh_content(self) -> None:
        """Atualiza horas e blocos nos widgets filhos."""
        hours_lines, blocks_lines, content_width = self._build_content()
        self.query_one("#agenda-hours", Static).update("\n".join(hours_lines))
        blocks_widget = self.query_one("#agenda-blocks", Static)
        blocks_widget.styles.min_width = content_width
        blocks_widget.update("\n".join(blocks_lines))

    def _assign_columns(self, sorted_inst: list[dict]) -> tuple[dict[int, int], dict[int, int]]:
        """Atribui colunas para renderizar sobreposição (estilo Google Calendar).

        Algoritmo greedy: cada evento recebe a primeira coluna livre.
        Eventos no mesmo grupo de sobreposição compartilham a mesma
        contagem total de colunas para manter largura consistente.

        Returns:
            col_of: id(inst) -> índice da coluna (0-based)
            total_cols_of: id(inst) -> total de colunas no grupo
        """
        col_ends: list[int] = []
        col_of: dict[int, int] = {}

        for inst in sorted_inst:
            sm = inst.get("start_minutes", 0)
            em = inst.get("end_minutes", sm + 60)
            placed = False
            for c, ce in enumerate(col_ends):
                if sm >= ce:
                    col_ends[c] = em
                    col_of[id(inst)] = c
                    placed = True
                    break
            if not placed:
                col_of[id(inst)] = len(col_ends)
                col_ends.append(em)

        # Union-Find para grupos de sobreposição
        parent: dict[int, int] = {}

        def find(x: int) -> int:
            while parent.get(x, x) != x:
                parent[x] = parent.get(parent[x], parent[x])
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        # Agrupar eventos que compartilham slots
        slot_events: dict[int, list[dict]] = {}
        for inst in sorted_inst:
            sm = inst.get("start_minutes", 0)
            em = inst.get("end_minutes", sm + 60)
            si = sm // 30
            ei = max(si + 1, -(-em // 30))
            for s in range(si, ei):
                if s not in slot_events:
                    slot_events[s] = []
                slot_events[s].append(inst)

        for events in slot_events.values():
            if len(events) > 1:
                first = id(events[0])
                for e in events[1:]:
                    union(first, id(e))

        # Max colunas por grupo
        group_max: dict[int, int] = {}
        for inst in sorted_inst:
            root = find(id(inst))
            col = col_of[id(inst)]
            group_max[root] = max(group_max.get(root, 0), col + 1)

        total_cols_of: dict[int, int] = {}
        for inst in sorted_inst:
            total_cols_of[id(inst)] = group_max[find(id(inst))]

        return col_of, total_cols_of

    def _build_content(self) -> tuple[list[str], list[str], int]:
        """Monta conteúdo separando horas (fixas) e blocos (scrolláveis).

        Cada linha visual = 15 minutos (BR-TUI-032). Labels a cada 30min.
        R10: linha do end_minutes ainda tem cor.
        R12: título de bloco consecutivo substitui corpo do anterior.

        Returns:
            hours_lines: linhas da coluna de horas
            blocks_lines: linhas da coluna de blocos
            content_width: largura total em chars da coluna de blocos
        """
        instances = self._instances
        now = datetime.now()
        cur_h, cur_m = now.hour, now.minute
        hours_out: list[str] = []
        blocks_out: list[str] = []
        min_col_w = 18  # BR-TUI-032-R13
        fw = 38  # largura ideal para coluna única
        max_content_w = 0

        sorted_inst = sorted(instances, key=lambda x: x.get("start_minutes", 0))
        col_of, total_cols_of = self._assign_columns(sorted_inst)

        # Mapa: linha de 15min -> [(inst, role, col)]
        line_info: dict[int, list[tuple[dict, str, int]]] = {}
        for inst in sorted_inst:
            sm = inst.get("start_minutes", 0)
            em = inst.get("end_minutes", sm + 60)
            col = col_of[id(inst)]
            start_line = sm // 15
            last_temporal = (em - 1) // 15
            r10_line = em // 15

            if last_temporal > start_line:
                display_end = r10_line
            else:
                display_end = start_line

            for li in range(start_line, display_end + 1):
                if li not in line_info:
                    line_info[li] = []
                role = "start" if li == start_line else "body"
                line_info[li].append((inst, role, col))

        def _time_label(h: int, m: int) -> str:
            if h == cur_h and m <= cur_m < m + 30:
                return f"[bold {C_ACCENT}]{now.strftime('%H:%M')}[/bold {C_ACCENT}]"
            return f"[dim]{h:02d}:{m:02d}[/dim]"

        range_start, range_end = compute_agenda_range(instances)
        line_start = range_start * 2
        line_end = range_end * 2 + 1

        for li in range(line_start, line_end + 1):
            minute = li * 15
            h = minute // 60
            m = minute % 60
            show_label = m % 30 == 0

            if show_label:
                hours_out.append(f"  {_time_label(h, m)}  [dim]\u2502[/dim]")
            else:
                hours_out.append("         [dim]\u2502[/dim]")

            entries = line_info.get(li, [])

            if not entries:
                blocks_out.append("")
                continue

            n_cols = max(total_cols_of[id(e[0])] for e in entries)
            gap = n_cols - 1  # BR-TUI-032-R14
            col_w = max(min_col_w, (fw - gap) // n_cols)
            line_w = n_cols * col_w + gap + 1
            max_content_w = max(max_content_w, line_w)

            # Indexar por coluna; "start" vence "body" (R12)
            col_map: dict[int, tuple[dict, str]] = {}
            for inst, role, col in entries:
                if col not in col_map or role == "start":
                    col_map[col] = (inst, role)

            parts: list[str] = []
            for c in range(n_cols):
                if c in col_map:
                    inst, role = col_map[c]
                    nm = inst.get("name", "")
                    st = inst.get("status", "pending")
                    sub = inst.get("substatus")
                    color = status_color(st, sub)
                    icon = status_icon(st, sub)
                    fc = fill_char(st, sub)
                    bold = is_bold_status(st)
                    fcolor = fill_color(st, sub)

                    if role == "start":
                        # accent bar + título C_TEXT + ícone (BR-TUI-032-R4)
                        accent_w = 1  # \u258c
                        separator_w = 3  # " \u00b7 "
                        icon_w = len(icon)
                        max_nm = max(1, col_w - accent_w - separator_w - icon_w)
                        if len(nm) > max_nm:
                            display_nm = nm[: max(1, max_nm - 1)] + "\u2026"
                        else:
                            display_nm = nm
                        visual_w = accent_w + len(display_nm) + separator_w + icon_w
                        pad = " " * max(0, col_w - visual_w)
                        if bold:
                            parts.append(
                                f"[bold {color}]\u258c[/bold {color}]"
                                f"[bold {C_TEXT}]{display_nm}[/bold {C_TEXT}]"
                                f" [dim]\u00b7[/dim] "
                                f"[bold {color}]{icon}[/bold {color}]"
                                f"{pad}"
                            )
                        else:
                            parts.append(
                                f"[{color}]\u258c[/{color}]"
                                f"[{C_TEXT}]{display_nm}[/{C_TEXT}]"
                                f" [dim]\u00b7[/dim] "
                                f"[{color}]{icon}[/{color}]"
                                f"{pad}"
                            )
                    else:
                        # Corpo: accent bar + fill (BR-TUI-032-R5)
                        parts.append(
                            f"[{color}]\u258c[/{color}][{fcolor}]{fc * (col_w - 1)}[/{fcolor}]"
                        )
                else:
                    parts.append(" " * col_w)

            blocks_out.append(f" {' '.join(parts)}")

        return hours_out, blocks_out, max_content_w

    def scroll_to_current_time(self) -> None:
        """Auto-scroll para posicionar hora atual no terco superior (BR-TUI-003-R15)."""
        now = datetime.now()
        current_slot = (now.hour * 60 + now.minute) // 30
        range_start, _ = compute_agenda_range(self._instances)
        slot_offset = current_slot - range_start
        if slot_offset < 0:
            return
        line_offset = slot_offset * 2
        if isinstance(self.parent, Widget):
            self.parent.scroll_to(y=max(0, line_offset - 6), animate=False)

    @staticmethod
    def find_block_at(instances: list[dict], hour: int, minute: int = 0) -> dict | None:
        """Encontra bloco que cobre o slot hora:minuto."""
        slot_min = hour * 60 + minute
        for inst in instances:
            start_min = inst.get("start_minutes", 0)
            end_min = inst.get("end_minutes", 0)
            if start_min <= slot_min < end_min:
                return inst
        return None
