"""TasksPanel - Card de tarefas com heat de proximidade (BR-TUI-003).

BR-TUI-003-R20: Ordenação por urgência (overdue > pending > done > cancelled).
BR-TUI-003-R22: Strikethrough em done/cancelled.
BR-TUI-003-R23: Subtítulo com contadores por status.
BR-TUI-003-R27: Nome herda cor do status.
BR-TUI-012: Navegação vertical com setas/j/k e highlight.
BR-TUI-004: Quick actions — Ctrl+K completa task.
"""

from textual.events import Key

from timeblock.tui.colors import (
    C_ERROR,
    C_HIGHLIGHT,
    C_MUTED,
    C_SUCCESS,
    task_proximity_color,
)
from timeblock.tui.widgets.focusable_panel import FocusablePanel


class TasksPanel(FocusablePanel):
    """Card de tarefas com 4 seções, heat de proximidade e navegação."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._tasks: list[dict] = []
        self._ordered: list[dict] = []

    def update_data(self, tasks: list[dict]) -> None:
        """Recebe tasks do coordinator e renderiza."""
        self._tasks = tasks
        self._order_tasks()
        self._set_item_count(len(self._ordered))
        self._refresh_content()

    def get_selected_item(self) -> dict | None:
        """Retorna task sob o cursor ou None."""
        if not self._ordered or self._cursor_index >= len(self._ordered):
            return None
        return self._ordered[self._cursor_index]

    def on_key(self, event: Key) -> None:
        """Captura navegação e quick actions."""
        if event.key == "ctrl+k":
            self._action_complete()
            event.stop()
        else:
            super().on_key(event)

    def _action_complete(self) -> None:
        """Completa task selecionada (BR-TUI-004)."""
        item = self.get_selected_item()
        if not item or not item.get("id"):
            return
        from timeblock.services.task_service import TaskService
        from timeblock.tui.session import service_action

        result, error = service_action(lambda s: TaskService.complete_task(item["id"], session=s))
        if not error and result:
            item["status"] = "completed"
            self._refresh_content()

    def _order_tasks(self) -> None:
        """Ordena: overdue > pending > completed > cancelled."""
        order = {"overdue": 0, "pending": 1, "completed": 2, "cancelled": 3}
        self._ordered = sorted(self._tasks, key=lambda t: order.get(t.get("status", ""), 9))

    def _refresh_content(self) -> None:
        """Constrói linhas do card e atualiza border_title + conteúdo."""
        tasks = self._tasks
        pending = [t for t in tasks if t.get("status") == "pending"]
        completed = [t for t in tasks if t.get("status") == "completed"]
        cancelled = [t for t in tasks if t.get("status") == "cancelled"]
        overdue = [t for t in tasks if t.get("status") == "overdue"]
        counts = f"{len(pending)} pend."
        if completed:
            counts += f" {len(completed)} done"
        if cancelled:
            counts += f" {len(cancelled)} canc."
        if overdue:
            counts += f" {len(overdue)} over."
        self.border_title = "Tarefas"
        self.border_subtitle = counts
        self.update("\n".join(self._build_lines()))

    def _build_lines(self) -> list[str]:
        """Monta linhas ordenadas com highlight no cursor."""
        lines: list[str] = []
        if not self._ordered:
            lines.append("  [dim]---                --/--   --:--[/dim]")
            lines.append("  [dim]---                --/--   --:--[/dim]")
            lines.append("")
            lines.append("  [dim]Crie uma task: atomvs task add[/dim]")
        else:
            for idx, task in enumerate(self._ordered):
                line = self._format_task(task)
                if idx == self._cursor_index and self.has_focus:
                    line = f"[on {C_HIGHLIGHT}]{line}[/on {C_HIGHLIGHT}]"
                lines.append(line)
        return lines

    def _format_task(self, task: dict) -> str:
        """Formata uma linha de task por status."""
        st = task.get("status", "pending")
        if st == "completed":
            return self._format_done_task(task, C_SUCCESS, "✓")
        if st == "cancelled":
            return self._format_done_task(task, C_MUTED, "✗")
        if st == "overdue":
            return self._format_overdue_task(task)
        return self._format_pending_task(task)

    @staticmethod
    def _format_pending_task(task: dict) -> str:
        """Formata task pendente com heat de proximidade."""
        nm = task.get("name", "")[:18]
        prox = task.get("proximity", "")
        dt = task.get("date", "")
        tm = task.get("time", "--:--")
        days = task.get("days", 999)
        color = task_proximity_color(days)
        ind = "!" if days is not None and days <= 1 else "·"
        return (
            f"  [{color}]{ind}[/{color}]  [{color}]{nm:<18s}[/{color}]"
            f"  [{color}]{prox:<8s}[/{color}]"
            f"  [{color}]{dt:<7s}[/{color}]"
            f"  [dim]{tm}[/dim]"
        )

    @staticmethod
    def _format_overdue_task(task: dict) -> str:
        """Formata task overdue."""
        nm = task.get("name", "")[:18]
        dt = task.get("date", "")
        tm = task.get("time", "--:--")
        prox = task.get("proximity", "")
        return (
            f"  [{C_ERROR}]✗[/{C_ERROR}]"
            f"  [{C_ERROR}]{nm:<18s}[/{C_ERROR}]"
            f"  [{C_ERROR}]{prox:<8s}[/{C_ERROR}]"
            f"  [{C_ERROR}]{dt:<7s}[/{C_ERROR}]"
            f"  [{C_ERROR}]{tm}[/{C_ERROR}]"
        )

    @staticmethod
    def _format_done_task(task: dict, color: str, icon: str) -> str:
        """Formata task concluída ou cancelada com strikethrough."""
        nm = task.get("name", "")[:18]
        dt = task.get("date", "")
        tm = task.get("time", "--:--")
        prox = task.get("proximity", "")
        return (
            f"  [{color}]{icon}[/{color}]"
            f"  [strike {color}]{nm:<18s}[/strike {color}]"
            f"  [{color}]{prox:<8s}[/{color}]"
            f"  [{color}]{dt:<7s}[/{color}]"
            f"  [{color}]{tm}[/{color}]"
        )
