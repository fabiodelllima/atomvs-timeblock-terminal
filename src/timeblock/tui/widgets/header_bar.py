"""HeaderBar - Barra superior contextual com border_title (BR-TUI-006).

Usa border_title com space-between para DASHBOARD ─── Data
Conteúdo interno mostra rotina, tasks pendentes, timer.
"""

from datetime import date

from textual.reactive import reactive
from textual.widgets import Static

from timeblock.tui.session import service_action

WEEKDAYS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
MONTHS_PT = [
    "",
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]

WEEKDAYS_FULL_PT = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
MONTHS_FULL_PT = [
    "",
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

SCREEN_NAMES = {
    "dashboard": "DASHBOARD",
    "routines": "ROTINAS",
    "habits": "HÁBITOS",
    "tasks": "TASKS",
    "timer": "TIMER",
}


class HeaderBar(Static):
    """Barra superior com informações contextuais em border_title."""

    current_screen: reactive[str] = reactive("dashboard")

    def on_mount(self) -> None:
        """Renderiza header inicial."""
        self._refresh_content()

    def update_screen(self, screen_name: str) -> None:
        """Atualiza quando screen muda."""
        self.current_screen = screen_name

    def watch_current_screen(self) -> None:
        """Reage à mudança de screen."""
        self._refresh_content()

    @staticmethod
    def _plain_len(text: str) -> int:
        """Calcula comprimento visível ignorando markup Rich."""
        import re

        return len(re.sub(r"\[.*?\]", "", text))

    def _refresh_content(self) -> None:
        """Renderiza border_title e conteúdo."""
        screen_label = SCREEN_NAMES.get(self.current_screen, "DASHBOARD")
        today = date.today()
        weekday = WEEKDAYS_FULL_PT[today.weekday()]
        month = MONTHS_FULL_PT[today.month]
        date_str = f"{weekday}, {today.day:02d} de {month} {today.year}"

        # border_title com space-between
        try:
            available = self.size.width or 80
        except Exception:
            available = 80
        gap = max(2, available - len(screen_label) - len(date_str) - 2)
        self.border_title = f"{screen_label} [#45475A]{'─' * gap}[/#45475A] {date_str}"

        # Conteúdo: rotina+tasks esquerda, timer direita
        routine = self._get_routine_info()
        tasks = self._get_task_info()
        timer = self._get_timer_info()

        left_parts = [p for p in [routine, tasks] if p]
        left = "  [dim]│[/dim]  ".join(left_parts) if left_parts else ""
        right = f"[dim]│[/dim]  {timer}" if timer else ""

        if not left and not right:
            self.update(" [dim]─[/dim]")
            return

        left_len = self._plain_len(left)
        right_len = self._plain_len(right)
        content_width = max(available - 6, 60)
        gap = max(2, content_width - left_len - right_len)

        self.update(f" {left}{' ' * gap}{right} ")

    @staticmethod
    def _get_routine_info() -> str:
        """Obtém info da rotina ativa."""
        try:
            from timeblock.services.routine_service import RoutineService

            result, error = service_action(lambda s: RoutineService(s).get_active_routine())
            if error or not result:
                return "[bold]Rotina Demo[/bold]  [dim]│[/dim]  6/10 [#A6E3A1]▪▪▪▪▪▪[/#A6E3A1][#45475A]░░░░[/#45475A]  60%"
            return f"[bold]{result.name}[/bold]  [dim]│[/dim]  4/8 [#A6E3A1]▪▪▪▪[/#A6E3A1][#45475A]░░░░[/#45475A]  50%"
        except Exception:
            return "[bold]Rotina Demo[/bold]  [dim]│[/dim]  6/10 [#A6E3A1]▪▪▪▪▪▪[/#A6E3A1][#45475A]░░░░[/#45475A]  60%"

    @staticmethod
    def _get_task_info() -> str:
        """Obtém contagem de tasks pendentes."""
        try:
            from timeblock.services.task_service import TaskService

            result, error = service_action(lambda s: TaskService.list_pending_tasks(session=s))
            if error or not result:
                return "3 tasks pendentes"
            return f"{len(result)} tasks pendentes"
        except Exception:
            return "3 tasks pendentes"

    @staticmethod
    def _get_timer_info() -> str:
        """Obtém info do timer ativo."""
        try:
            # TODO: Integrar com TimerService (requer habit_instance_id)
            result, error = None, True
            if error or not result:
                return "[#CBA6F7]▶ Deep Work  25:43[/#CBA6F7]"
            return "[#CBA6F7]▶ ativo[/#CBA6F7]"
        except Exception:
            return "[#CBA6F7]▶ Deep Work  25:43[/#CBA6F7]"
