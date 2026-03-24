"""AgendaPanel - Régua de horas com blocos coloridos por status.

BR-TUI-003-R13: Régua adaptativa 05:00-23:30.
BR-TUI-003-R15: Auto-scroll na hora atual.
BR-TUI-031: Scroll horizontal para multi-coluna.
BR-TUI-032: Renderização de blocos contínuos com granularidade de 15min.

Referências:
    - HUMBLE; FARLEY, 2010, p. 179 (Humble Object Pattern)
    - A lógica pura de renderização está em agenda_renderer.py.
"""

from textual.containers import ScrollableContainer
from textual.widget import Widget
from textual.widgets import Static

from timeblock.tui.widgets.agenda_renderer import (
    build_agenda_content,
    compute_agenda_range,
)

# Re-export para backward compatibility (test_agenda_range.py importa daqui)
__all__ = ["AgendaPanel", "compute_agenda_range"]


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
        hours_lines, blocks_lines, content_width = build_agenda_content(
            self._instances,
        )
        self.query_one("#agenda-hours", Static).update("\n".join(hours_lines))
        blocks_widget = self.query_one("#agenda-blocks", Static)
        blocks_widget.styles.min_width = content_width
        blocks_widget.update("\n".join(blocks_lines))

    def scroll_to_current_time(self) -> None:
        """Auto-scroll para posicionar hora atual no terco superior (BR-TUI-003-R15)."""
        from datetime import datetime

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
