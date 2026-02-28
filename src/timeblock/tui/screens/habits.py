"""HabitsScreen - Tela de hábitos com ações de instância (BR-TUI-010).

Lista instâncias do dia agrupadas por hábito, permitindo marcar como
done (com duração para substatus) ou skip (com categoria e nota).
"""

from datetime import date
from typing import Any, ClassVar

from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from timeblock.models.enums import DoneSubstatus, SkipReason


class HabitsScreen(Widget):
    """Tela de Hábitos com ações de instância."""

    DEFAULT_CSS = """
    HabitsScreen {
        width: 100%;
        height: 100%;
    }
    """

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("enter", "open_action", "Ação", show=True),
        Binding("d", "select_done", "Done", show=False),
        Binding("s", "select_skip", "Skip", show=False),
        Binding("j", "move_down", "Baixo", show=False),
        Binding("k", "move_up", "Cima", show=False),
        Binding("escape", "cancel_action", "Voltar", show=True),
    ]

    current_date: reactive[date] = reactive(date.today)
    selected_index: reactive[int] = reactive(0)
    action_mode: reactive[str | None] = reactive(None)
    selected_skip_reason: SkipReason | None = None
    instances: list[dict[str, Any]]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.instances = []

    def compose(self):
        """Compõe layout da tela de hábitos."""
        yield Vertical(
            Static(id="habits-header"),
            Static(id="habits-list"),
            Static(id="habits-action"),
            Static(id="habits-status"),
            id="habits-content",
        )

    def on_mount(self) -> None:
        """Inicializa display."""
        self._refresh_display()

    # ==================== Agrupamento e Display ====================

    def _group_by_habit(self) -> dict[str, list[dict[str, Any]]]:
        """Agrupa instâncias por nome do hábito."""
        groups: dict[str, list[dict[str, Any]]] = {}
        for inst in self.instances:
            name = inst.get("habit_name", "Sem nome")
            if name not in groups:
                groups[name] = []
            groups[name].append(inst)
        return groups

    def _build_instance_line(self, instance: dict[str, Any]) -> str:
        """Constrói linha de display para uma instância."""
        name = instance.get("habit_name", "?")
        time_str = instance.get("time", "??:??")
        status = instance.get("status", "pending")
        indicator = self._get_status_indicator(status)
        return f"{indicator} {time_str} {name}"

    def _get_status_indicator(self, status: str) -> str:
        """Retorna indicador visual com cor para o status."""
        if status == "done":
            return "[#A6E3A1]✓[/#A6E3A1]"
        elif status == "not_done":
            return "[#F9E2AF]✗[/#F9E2AF]"
        else:  # pending
            return "[dim]·[/dim]"

    # ==================== Menu de Ação ====================

    def _open_action_menu(self) -> None:
        """Abre menu de ação se instância é pendente."""
        if not self.instances:
            return
        instance = self.instances[self.selected_index]
        if instance.get("status") != "pending":
            return
        self.action_mode = "action_select"

    def _build_action_menu(self) -> str:
        """Constrói menu de ação Done/Skip."""
        return (
            "[bold]Ação:[/bold]\n\n"
            "  [dim]d[/dim] [#A6E3A1]Done[/#A6E3A1] - Marcar como concluído\n"
            "  [dim]s[/dim] [#F9E2AF]Skip[/#F9E2AF] - Pular instância\n\n"
            "  [dim]esc[/dim] Cancelar"
        )

    # ==================== Done ====================

    def _select_done(self) -> None:
        """Entra no modo de input de duração."""
        self.action_mode = "duration_input"

    @staticmethod
    def _calculate_substatus(actual_minutes: int, expected_minutes: int) -> DoneSubstatus:
        """Calcula substatus baseado no percentual de completude.

        Regras:
        - < 90% → PARTIAL
        - 90-110% → FULL
        - 110-150% → OVERDONE
        - > 150% → EXCESSIVE
        """
        if expected_minutes <= 0:
            return DoneSubstatus.FULL

        percentage = (actual_minutes / expected_minutes) * 100

        if percentage < 90:
            return DoneSubstatus.PARTIAL
        elif percentage <= 110:
            return DoneSubstatus.FULL
        elif percentage <= 150:
            return DoneSubstatus.OVERDONE
        else:
            return DoneSubstatus.EXCESSIVE

    # ==================== Skip ====================

    def _select_skip(self) -> None:
        """Entra no modo de seleção de razão de skip."""
        self.action_mode = "skip_reason"

    @staticmethod
    def _get_skip_reasons() -> list[SkipReason]:
        """Retorna todas as SkipReason disponíveis."""
        return list(SkipReason)

    def _build_skip_reason_menu(self) -> str:
        """Constrói menu de seleção de razão de skip."""
        lines = ["[bold]Razão do skip:[/bold]\n"]
        for i, reason in enumerate(SkipReason, 1):
            lines.append(f"  [dim]{i}[/dim] {reason.value}")
        lines.append("\n  [dim]esc[/dim] Cancelar")
        return "\n".join(lines)

    def _select_skip_reason(self, reason: SkipReason) -> None:
        """Seleciona razão de skip e entra em modo de nota."""
        self.selected_skip_reason = reason
        self.action_mode = "skip_note"

    # ==================== Navegação ====================

    def _move_selection(self, delta: int) -> None:
        """Move seleção na lista com clamping."""
        if not self.instances:
            return
        new_index = self.selected_index + delta
        self.selected_index = max(0, min(new_index, len(self.instances) - 1))

    def action_move_down(self) -> None:
        """Move seleção para baixo."""
        self._move_selection(1)

    def action_move_up(self) -> None:
        """Move seleção para cima."""
        self._move_selection(-1)

    def action_open_action(self) -> None:
        """Abre menu de ação."""
        self._open_action_menu()

    def action_select_done(self) -> None:
        """Seleciona ação Done."""
        if self.action_mode == "action_select":
            self._select_done()

    def action_select_skip(self) -> None:
        """Seleciona ação Skip."""
        if self.action_mode == "action_select":
            self._select_skip()

    def action_cancel_action(self) -> None:
        """Cancela ação em andamento."""
        self.action_mode = None
        self.selected_skip_reason = None

    # ==================== Display ====================

    def _build_list_display(self) -> str:
        """Constrói display da lista de instâncias."""
        if not self.instances:
            return "[dim]Nenhuma instância para hoje[/dim]"

        lines = []
        groups = self._group_by_habit()
        flat_index = 0
        for habit_name, instances in groups.items():
            lines.append(f"\n[bold]{habit_name}[/bold]")
            for inst in instances:
                prefix = "▶ " if flat_index == self.selected_index else "  "
                line = self._build_instance_line(inst)
                lines.append(f"{prefix}{line}")
                flat_index += 1
        return "\n".join(lines)

    def _refresh_display(self) -> None:
        """Atualiza widgets visuais."""
        try:
            self.query_one("#habits-header", Static).update(
                f"[bold]Hábitos[/bold] - {self.current_date.strftime('%d/%m/%Y')}"
            )
            self.query_one("#habits-list", Static).update(self._build_list_display())

            # Menu de ação contextual
            if self.action_mode == "action_select":
                self.query_one("#habits-action", Static).update(self._build_action_menu())
            elif self.action_mode == "duration_input":
                self.query_one("#habits-action", Static).update(
                    "[bold]Duração real (minutos):[/bold] _"
                )
            elif self.action_mode == "skip_reason":
                self.query_one("#habits-action", Static).update(self._build_skip_reason_menu())
            elif self.action_mode == "skip_note":
                reason_label = self.selected_skip_reason.value if self.selected_skip_reason else "?"
                self.query_one("#habits-action", Static).update(
                    f"[bold]Razão:[/bold] {reason_label}\n"
                    "[bold]Nota (opcional, enter para pular):[/bold] _"
                )
            else:
                self.query_one("#habits-action", Static).update("")
        except Exception:
            pass

    # ==================== Watchers ====================

    def watch_selected_index(self, _value: int) -> None:
        """Reage à mudança de seleção."""
        self._refresh_display()

    def watch_action_mode(self, _value: str | None) -> None:
        """Reage à mudança de modo de ação."""
        self._refresh_display()
