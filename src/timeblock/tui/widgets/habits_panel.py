"""HabitsPanel - Card de hábitos do dia com substatus e esforço (BR-TUI-003).

BR-TUI-003-R14: Subtítulo com dot matrix e percentual.
BR-TUI-003-R18: Effort bar proporcional.
BR-TUI-003-R19: Ordenação por start_time.
BR-TUI-003-R27: Nome herda cor do status.
BR-TUI-012: Navegação vertical com setas/j/k e highlight.
BR-TUI-004: Quick actions — v done, s skip (ADR-037).
BR-TUI-021: t inicia timer para hábito selecionado (ADR-037).
"""

from typing import Any

from textual.events import Key
from textual.message import Message

from timeblock.tui.colors import (
    C_HIGHLIGHT,
    is_bold_status,
    status_color,
    status_icon,
)
from timeblock.tui.formatters import format_duration_card
from timeblock.tui.widgets.focusable_panel import FocusablePanel


class HabitsPanel(FocusablePanel):
    """Card de hábitos com substatus, barra de progresso e navegação."""

    HIGHLIGHT_COLOR: str = C_HIGHLIGHT

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._instances: list[dict] = []

    def update_data(self, instances: list[dict]) -> None:
        """Recebe instâncias do coordinator e renderiza."""
        self._instances = instances
        if instances:
            self._showing_placeholders = False
            self._set_item_count(len(instances))
        self._refresh_content()

    def get_selected_item(self) -> dict | None:
        """Retorna item sob o cursor ou None."""
        if not self._instances or self._cursor_index >= len(self._instances):
            return None
        return self._instances[self._cursor_index]

    def on_key(self, event: Key) -> None:
        """Captura navegação e quick actions."""
        if event.key == "s":
            self._action_skip()
            event.stop()
        elif event.key == "v":
            self._action_done()
            event.stop()
        elif event.key == "t":
            self._action_start_timer()
            event.stop()
        elif event.key == "u":
            self._action_undo()
            event.stop()

    class HabitDoneRequest(Message):
        """Solicita marcação de hábito como done ao coordinator (RF-001)."""

        def __init__(self, instance_id: int) -> None:
            self.instance_id = instance_id
            super().__init__()

    class HabitSkipRequest(Message):
        """Solicita marcação de hábito como skipped ao coordinator (RF-001)."""

        def __init__(self, instance_id: int) -> None:
            self.instance_id = instance_id
            super().__init__()

    class TimerStartRequest(Message):
        """Solicita início de timer para hábito ao coordinator (BR-TUI-021)."""

        def __init__(self, instance_id: int) -> None:
            self.instance_id = instance_id
            super().__init__()

    class TimerStopAndDoneRequest(Message):
        """Solicita parada do timer e marcação como done (BR-TUI-021)."""

        def __init__(self, instance_id: int) -> None:
            self.instance_id = instance_id
            super().__init__()

    def _action_done(self) -> None:
        """Emite HabitDoneRequest ou TimerStopAndDoneRequest conforme status.

        Se o hábito está running (timer ativo), para o timer e marca done.
        Caso contrário, marca done diretamente (BR-TUI-004, BR-TUI-021).
        """
        item = self.get_selected_item()
        if not item or not item.get("id"):
            return
        if item.get("status") in ("running", "paused"):
            self.post_message(self.TimerStopAndDoneRequest(item["id"]))
        else:
            self.post_message(self.HabitDoneRequest(item["id"]))

    def _action_skip(self) -> None:
        """Emite HabitSkipRequest para o coordinator (BR-TUI-004, RF-001)."""
        item = self.get_selected_item()
        if not item or not item.get("id"):
            return
        self.post_message(self.HabitSkipRequest(item["id"]))

    class HabitUndoRequest(Message):
        """Solicita reverter hábito para pending (ADR-037)."""

        def __init__(self, instance_id: int) -> None:
            self.instance_id = instance_id
            super().__init__()

    def _action_undo(self) -> None:
        """Emite HabitUndoRequest (ADR-037)."""
        item = self.get_selected_item()
        if not item or not item.get("id"):
            return
        self.post_message(self.HabitUndoRequest(item["id"]))

    def _action_start_timer(self) -> None:
        """Emite TimerStartRequest para o coordinator (BR-TUI-021)."""
        item = self.get_selected_item()
        if not item or not item.get("id"):
            return
        if item.get("status") not in ("pending", "running"):
            return
        self.post_message(self.TimerStartRequest(item["id"]))

    def _refresh_content(self) -> None:
        """Constrói linhas do card e atualiza border_title + conteúdo."""
        instances = self._instances
        done = sum(1 for i in instances if i["status"] == "done")
        total = len(instances)
        if total > 0:
            pct = int((done / total) * 100)
            dots = "●" * done + "○" * (total - done)
            self.border_title = "Hábitos"
            self.border_subtitle = f"{dots} {done}/{total} {pct}%"
        else:
            self.border_title = "Hábitos"
            self.border_subtitle = "0/0"
        self.update("\n".join(self._build_lines()))

    def _build_lines(self) -> list[str]:
        """Monta linhas de hábitos com ícone, nome, horário, duração e barra."""
        instances = self._instances
        lines: list[str] = []
        max_bars = 4
        if not instances:
            return self._enter_placeholder_mode(
                "---              · --:-- · --min",
                "Crie uma rotina: atomvs routine add",
            )
        else:
            for idx, inst in enumerate(instances[:12]):
                line = self._format_instance(inst, max_bars)
                if idx == self._cursor_index and self.has_focus:
                    line = f"[on {self.HIGHLIGHT_COLOR}]{line}[/on {self.HIGHLIGHT_COLOR}]"
                lines.append(line)
        return lines

    def _format_instance(self, inst: dict, max_bars: int) -> str:
        """Formata uma linha de hábito com ícone, nome, horário, duração e barra."""
        name = inst["name"][:16]
        st = inst["status"]
        sub = inst.get("substatus")
        actual = inst.get("actual_minutes")
        sm = inst.get("start_minutes", 0)
        em = inst.get("end_minutes", 0)
        est_min = em - sm
        minutes = actual if actual else est_min
        dur = format_duration_card(minutes)
        color = status_color(st, sub)
        icon = status_icon(st, sub)
        bold = is_bold_status(st)
        if bold:
            icon_fmt = f"[bold {color}]{icon:<2s}[/bold {color}]"
        else:
            icon_fmt = f"[{color}]{icon:<2s}[/{color}]"
        if st == "pending":
            nm_fmt = f"{name:<16s}"
        elif bold:
            nm_fmt = f"[bold {color}]{name:<16s}[/bold {color}]"
        else:
            nm_fmt = f"[{color}]{name:<16s}[/{color}]"
        sh, s_min = divmod(sm, 60)
        eh, e_min = divmod(em, 60)
        time_fmt = f"[dim]{sh:02d}:{s_min:02d} - {eh:02d}:{e_min:02d}[/dim]"
        if bold:
            dur_fmt = f"[{color}]{dur:>7s}[/{color}]"
        else:
            dur_fmt = f"[dim]{dur:>7s}[/dim]"
        bar = self._build_bar(st, color, actual, est_min, max_bars)
        return f"  {icon_fmt} {nm_fmt} {time_fmt} {dur_fmt} {bar}"

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
