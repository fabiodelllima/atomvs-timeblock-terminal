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
        """Monta linhas da agenda com régua de 30min e sobreposição multi-coluna.

        Formato: horário ─┼─ nome · ícone  ┆  nome · ícone
        Eventos sobrepostos são renderizados lado a lado com separador ┆.
        Bold exclusivo em running/paused. Background colorido nos fills.
        Cada slot de 30min ocupa 2 linhas uniformes.
        """
        instances = self._instances
        now = datetime.now()
        cur_h, cur_m = now.hour, now.minute
        out: list[str] = []
        fw = 38  # fill width total

        sorted_inst = sorted(instances, key=lambda x: x.get("start_minutes", 0))
        col_of, total_cols_of = self._assign_columns(sorted_inst)

        # Mapeia slot → lista de (inst, role, col)
        slot_info: dict[int, list[tuple[dict, str, int]]] = {}
        for inst in sorted_inst:
            sm = inst.get("start_minutes", 0)
            em = inst.get("end_minutes", sm + 60)
            si = sm // 30
            ei = max(si + 1, -(-em // 30))
            col = col_of[id(inst)]
            for i, s in enumerate(range(si, ei)):
                if s not in slot_info:
                    slot_info[s] = []
                slot_info[s].append((inst, "start" if i == 0 else "fill", col))

        def _tl(h: int, m: int) -> str:
            if h == cur_h and m <= cur_m < m + 30:
                return f"[bold {C_ACCENT}]{now.strftime('%H:%M')}[/bold {C_ACCENT}]"
            return f"[dim]{h:02d}:{m:02d}[/dim]"

        range_start, range_end = compute_agenda_range(instances)
        sep = " [dim]┆[/dim] "

        for idx in range(range_start, range_end + 1):
            h = idx // 2
            m = (idx % 2) * 30
            tl = _tl(h, m)

            entries = slot_info.get(idx, [])

            if not entries:
                out.append(f"  {tl}  [dim]│[/dim]")
                out.append("         [dim]│[/dim]")
                continue

            # Colunas para este slot
            n_cols = max(total_cols_of[id(e[0])] for e in entries)
            sep_chars = 3 * (n_cols - 1)  # " ┆ " = 3 chars visuais
            col_w = max(1, (fw - sep_chars) // n_cols)

            # Indexar por coluna
            col_map: dict[int, tuple[dict, str]] = {}
            for inst, role, col in entries:
                col_map[col] = (inst, role)

            has_start = any(role == "start" for _, role, _ in entries)
            header_parts: list[str] = []
            fill_parts: list[str] = []

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

                    fb = f"[{fcolor}]{fc * col_w}[/{fcolor}]"

                    if role == "start":
                        max_nm = max(1, col_w - 4)
                        display_nm = nm[:max_nm] if len(nm) > max_nm else nm
                        if bold:
                            header_parts.append(
                                f"[bold {color}]{display_nm}[/bold {color}]"
                                f" [dim]·[/dim] "
                                f"[bold {color}]{icon}[/bold {color}]"
                            )
                        else:
                            header_parts.append(
                                f"[{color}]{display_nm}[/{color}]"
                                f" [dim]·[/dim] "
                                f"[{color}]{icon}[/{color}]"
                            )
                    else:
                        header_parts.append(fb)

                    fill_parts.append(fb)
                else:
                    header_parts.append(" " * col_w)
                    fill_parts.append(" " * col_w)

            header_line = sep.join(header_parts)
            fill_line = sep.join(fill_parts)

            if has_start:
                out.append(f"  {tl} [dim]─┼─[/dim] {header_line}")
            else:
                out.append(f"  {tl}  [dim]│[/dim] {header_line}")
            out.append(f"         [dim]│[/dim] {fill_line}")

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
        # Cada slot = 2 linhas; terco superior = 1/3 do viewport
        line_offset = slot_offset * 2
        # Scroll no container pai (VerticalScroll), não no Static
        if self.parent is not None and hasattr(self.parent, "scroll_to"):
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
