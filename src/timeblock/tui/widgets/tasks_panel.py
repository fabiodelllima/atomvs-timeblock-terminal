"""TasksPanel - Card de tarefas com heat de proximidade (BR-TUI-003).

BR-TUI-003-R20: Ordenação por urgência (overdue > pending > done > cancelled).
BR-TUI-003-R22: Strikethrough em done/cancelled.
BR-TUI-003-R23: Subtítulo com contadores por status.
BR-TUI-003-R27: Nome herda cor do status.
"""

from textual.widgets import Static

from timeblock.tui.colors import (
    C_ERROR,
    C_MUTED,
    C_SUCCESS,
    task_proximity_color,
)
from timeblock.tui.formatters import spaced_title


class TasksPanel(Static):
    """Card de tarefas com 4 seções e heat de proximidade."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._tasks: list[dict] = []

    def update_data(self, tasks: list[dict]) -> None:
        """Recebe tasks do coordinator e renderiza."""
        self._tasks = tasks
        self._refresh_content()

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

        self.border_title = spaced_title("Tarefas", counts)
        self.update("\n".join(self._build_lines(pending, completed, cancelled, overdue)))

    def _build_lines(
        self,
        pending: list[dict],
        completed: list[dict],
        cancelled: list[dict],
        overdue: list[dict],
    ) -> list[str]:
        """Monta linhas das 4 seções de tarefas."""
        lines: list[str] = []

        for task in pending:
            nm = task.get("name", "")[:18]
            prox = task.get("proximity", "")
            dt = task.get("date", "")
            tm = task.get("time", "--:--")
            days = task.get("days", 999)
            color = task_proximity_color(days)
            ind = "!" if days is not None and days <= 1 else "·"
            lines.append(
                f"  [{color}]{ind}[/{color}]  [{color}]{nm:<18s}[/{color}]"
                f"  [{color}]{prox:<8s}[/{color}]"
                f"  [{color}]{dt:<7s}[/{color}]"
                f"  [dim]{tm}[/dim]"
            )

        for task in completed:
            lines.append(self._format_done_task(task, C_SUCCESS, "✓"))

        for task in cancelled:
            lines.append(self._format_done_task(task, C_MUTED, "✗"))

        for task in overdue:
            nm = task.get("name", "")[:18]
            dt = task.get("date", "")
            tm = task.get("time", "--:--")
            prox = task.get("proximity", "")
            lines.append(
                f"  [{C_ERROR}]✗[/{C_ERROR}]"
                f"  [{C_ERROR}]{nm:<18s}[/{C_ERROR}]"
                f"  [{C_ERROR}]{prox:<8s}[/{C_ERROR}]"
                f"  [{C_ERROR}]{dt:<7s}[/{C_ERROR}]"
                f"  [{C_ERROR}]{tm}[/{C_ERROR}]"
            )

        if not lines:
            lines.append("  [dim]Nenhuma task[/dim]")

        return lines

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
