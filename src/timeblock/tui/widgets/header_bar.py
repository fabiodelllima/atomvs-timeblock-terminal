"""HeaderBar - Barra superior contextual com métricas agregadas (BR-TUI-035).

Widget fino: delega busca de dados a header_data e formatação a header_renderer.
Responsabilidade única: lifecycle Textual e orquestração.

Referências:
    - ADR-052 (Redesign do conteúdo interno do HeaderBar)
    - BR-TUI-035 (Conteúdo interno do HeaderBar)
"""

from datetime import date, datetime

from textual.reactive import reactive
from textual.widgets import Static

from timeblock.tui.widgets.header_data import (
    compute_daily_tasks_progress,
    compute_weekly_habits_progress,
    fetch_active_routine,
    find_next_pending_item,
)
from timeblock.tui.widgets.header_renderer import (
    build_habits_progress,
    build_header_content,
    build_next_item,
    build_tasks_progress,
    truncate_next_name,
)
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
    """Barra superior com métricas agregadas em conteúdo interno."""

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

    def _refresh_content(self) -> None:
        """Orquestra busca de dados e renderização.

        BR-TUI-035 regra 24: uma única chamada ao RoutineService
        alimenta tanto o border_title quanto a seção de hábitos.
        """
        today = date.today()
        now = datetime.now()

        self._update_border_subtitle(today)

        routine = fetch_active_routine()
        self.border_title = routine.name if routine else "Sem rotina ativa"

        content_width = self._get_content_width()

        habits_section = build_habits_progress(
            *compute_weekly_habits_progress(routine, today),
        )
        tasks_section = build_tasks_progress(
            *compute_daily_tasks_progress(today),
        )

        next_name, next_minutes = find_next_pending_item(routine, now)
        if next_name and len(next_name) > 20:
            next_name = truncate_next_name(next_name, 20)
        next_section = build_next_item(next_name, next_minutes)

        self.update(
            build_header_content(
                habits_section,
                tasks_section,
                next_section,
                content_width,
            )
        )

    def _update_border_subtitle(self, today: date) -> None:
        """Atualiza data por extenso no border_subtitle."""
        weekday = WEEKDAYS_FULL_PT[today.weekday()]
        month = MONTHS_FULL_PT[today.month]
        self.border_subtitle = f"{weekday}, {today.day:02d} de {month} de {today.year}"

    def _get_content_width(self) -> int:
        """Retorna largura útil do conteúdo interno."""
        try:
            available = self.size.width or 80
        except Exception:
            logger.debug("Exceção capturada", exc_info=True)
            available = 80
        return max(available - 6, 40)
