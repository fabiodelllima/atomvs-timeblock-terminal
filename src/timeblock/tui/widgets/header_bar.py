"""HeaderBar - Barra superior contextual com border_title (BR-TUI-006).

Usa border_title com space-between para DASHBOARD ─── Data
Conteúdo interno mostra rotina, tasks pendentes, timer.
"""

from datetime import date

from textual.reactive import reactive
from textual.widgets import Static

from timeblock.tui.session import service_action
from timeblock.utils.logger import get_logger

logger = get_logger(__name__)

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
    "tasks": "TAREFAS",
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
        """Renderiza border_title, border_subtitle e conteúdo interno."""
        today = date.today()
        weekday = WEEKDAYS_FULL_PT[today.weekday()]
        month = MONTHS_FULL_PT[today.month]
        date_str = f"{weekday}, {today.day:02d} de {month} de {today.year}"

        routine_name = self._get_active_routine_name()
        self.border_title = routine_name if routine_name else "Sem rotina ativa"
        self.border_subtitle = date_str

        try:
            available = self.size.width or 80
        except Exception:
            logger.debug("Exceção capturada", exc_info=True)
            available = 80

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
    def _get_active_routine_name() -> str:
        """Retorna apenas o nome da rotina ativa, ou string vazia."""
        try:
            from timeblock.services.routine_service import RoutineService

            result, error = service_action(lambda s: RoutineService(s).get_active_routine())
            if error or not result:
                return ""
            if isinstance(result, dict):
                return result.get("name", "")
            return str(getattr(result, "name", ""))
        except Exception:
            logger.debug("Exceção em _get_active_routine_name", exc_info=True)
            return ""

    @staticmethod
    def _get_routine_info() -> str:
        """Obtém info da rotina ativa. Vazio se sem rotina."""
        try:
            from timeblock.services.routine_service import RoutineService

            result, error = service_action(lambda s: RoutineService(s).get_active_routine())
            if error or not result:
                return (
                    "[dim][Sem rotina][/dim]  [dim]│[/dim]  0/0 [#45475A]░░░░░░░░░░[/#45475A]  0%"
                )
            return (
                f"[bold]{result.name}[/bold]  [dim]│[/dim]  0/0 [#45475A]░░░░░░░░░░[/#45475A]  0%"
            )
        except Exception:
            logger.debug("Exceção capturada", exc_info=True)
            return "[dim][Sem rotina][/dim]  [dim]│[/dim]  0/0 [#45475A]░░░░░░░░░░[/#45475A]  0%"

    @staticmethod
    def _get_task_info() -> str:
        """Obtém contagem de tasks pendentes."""
        try:
            from timeblock.services.task_service import TaskService

            result, error = service_action(lambda s: TaskService.list_pending_tasks(session=s))
            if error or not result:
                return "[dim]0 tasks[/dim]"
            return f"{len(result)} tasks pendentes"
        except Exception:
            logger.debug("Exceção capturada", exc_info=True)
            return "[dim]0 tasks[/dim]"

    @staticmethod
    def _get_timer_info() -> str:
        """Obtém info do timer ativo. Vazio se sem timer."""
        try:
            # TODO: Integrar com TimerService (requer habit_instance_id)
            return "[dim]⏹ --:--[/dim]"
        except Exception:
            logger.debug("Exceção capturada", exc_info=True)
            return "[dim]⏹ --:--[/dim]"
