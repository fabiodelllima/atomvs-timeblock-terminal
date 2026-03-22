"""AgendaPanel - Régua de horas com blocos coloridos por status.

BR-TUI-003-R13: Régua adaptativa 05:00-23:30.
BR-TUI-003-R15: Auto-scroll na hora atual.
BR-TUI-032: Renderização de blocos contínuos com granularidade de 15min.
"""

from datetime import datetime

from textual.widget import Widget
from textual.widgets import Static

from timeblock.tui.colors import (
    C_ACCENT,
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


class AgendaPanel(Static):
    can_focus = True
    """Agenda vertical com régua de 15min e blocos contínuos."""

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

    def _build_lines(self) -> list[str]:
        """Monta linhas da agenda com granularidade de 15min (BR-TUI-032).

        Cada linha visual = 15 minutos. Labels de hora a cada 30min.
        Linha de início: título + ícone (texto limpo, sem accent bar).
        Linhas de corpo: accent bar + fill char colorido.
        R10: linha do end_minutes ainda tem cor.
        R12: título de bloco consecutivo substitui corpo do anterior.
        Sem linhas horizontais atravessando blocos (BR-TUI-032-R9).
        """
        instances = self._instances
        now = datetime.now()
        cur_h, cur_m = now.hour, now.minute
        out: list[str] = []
        min_col_w = 18  # BR-TUI-032-R13: largura mínima por coluna
        fw = 38  # largura total da área de conteúdo

        sorted_inst = sorted(instances, key=lambda x: x.get("start_minutes", 0))
        col_of, total_cols_of = self._assign_columns(sorted_inst)

        # Mapa: linha de 15min → [(inst, role, col)]
        # role: "start" (título) ou "body" (accent bar + fill)
        line_info: dict[int, list[tuple[dict, str, int]]] = {}
        for inst in sorted_inst:
            sm = inst.get("start_minutes", 0)
            em = inst.get("end_minutes", sm + 60)
            col = col_of[id(inst)]
            start_line = sm // 15
            last_temporal = (em - 1) // 15
            r10_line = em // 15

            # R10 só se aplica quando o bloco tem linhas de corpo
            # (bloco > 15min). Bloco mínimo de 15min = só título.
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
            """Label de hora com destaque no slot atual (BR-TUI-003-R16)."""
            if h == cur_h and m <= cur_m < m + 30:
                return f"[bold {C_ACCENT}]{now.strftime('%H:%M')}[/bold {C_ACCENT}]"
            return f"[dim]{h:02d}:{m:02d}[/dim]"

        # Converte range de 30min slots para linhas de 15min
        range_start, range_end = compute_agenda_range(instances)
        line_start = range_start * 2
        line_end = range_end * 2 + 1

        for li in range(line_start, line_end + 1):
            minute = li * 15
            h = minute // 60
            m = minute % 60
            show_label = m % 30 == 0

            if show_label:
                prefix = f"  {_time_label(h, m)}  [dim]│[/dim]"
            else:
                prefix = "         [dim]│[/dim]"

            entries = line_info.get(li, [])

            if not entries:
                out.append(prefix)
                continue

            # Total de colunas para esta linha
            n_cols = max(total_cols_of[id(e[0])] for e in entries)
            gap = n_cols - 1  # BR-TUI-032-R14: 1 char entre colunas
            col_w = max(min_col_w, (fw - gap) // n_cols)

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
                        # Título + ícone, sem accent bar (BR-TUI-032-R4)
                        max_nm = max(1, col_w - 5)
                        if len(nm) > max_nm:
                            display_nm = nm[: max(1, max_nm - 1)] + "\u2026"
                        else:
                            display_nm = nm
                        if bold:
                            parts.append(
                                f"[bold {color}]{display_nm}[/bold {color}]"
                                f" [dim]\u00b7[/dim] "
                                f"[bold {color}]{icon}[/bold {color}]"
                            )
                        else:
                            parts.append(
                                f"[{color}]{display_nm}[/{color}]"
                                f" [dim]\u00b7[/dim] "
                                f"[{color}]{icon}[/{color}]"
                            )
                    else:
                        # Corpo: accent bar + fill (BR-TUI-032-R5)
                        parts.append(
                            f"[{color}]\u258c[/{color}][{fcolor}]{fc * (col_w - 1)}[/{fcolor}]"
                        )
                else:
                    parts.append(" " * col_w)

            out.append(f"{prefix} {' '.join(parts)}")

        return out

    def scroll_to_current_time(self) -> None:
        """Auto-scroll para posicionar hora atual no terco superior (BR-TUI-003-R15).

        Calcula offset em linhas baseado no slot atual e faz scroll
        no container pai (agenda-content tem overflow-y: auto).
        """
        now = datetime.now()
        current_slot = (now.hour * 60 + now.minute) // 30
        range_start, _ = compute_agenda_range(self._instances)
        slot_offset = current_slot - range_start
        if slot_offset < 0:
            return
        # Cada slot 30min = 2 linhas de 15min
        line_offset = slot_offset * 2
        # Scroll no container pai (VerticalScroll), não no Static
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
