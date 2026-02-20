"""DashboardScreen - Tela principal com grade temporal e tasks."""

from textual.containers import Horizontal, Vertical
from textual.widgets import Static


class DashboardScreen(Static):
    """Tela do Dashboard com timeblocks proporcionais e coluna de tasks."""

    DEFAULT_CSS = """
    DashboardScreen {
        width: 100%;
        height: 100%;
    }

    #timeblock-column {
        width: 70%;
        height: 100%;
        overflow-y: auto;
    }

    #tasks-column {
        width: 30%;
        height: 100%;
        border-left: solid $surface-lighten-2;
    }
    """

    def __init__(self, routine_name: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._routine_name = routine_name

    def compose(self):
        """Compõe layout de duas colunas."""
        with Horizontal():
            yield Vertical(
                Static(self._get_header()),
                id="timeblock-column",
            )
            yield Vertical(
                Static("Tasks"),
                id="tasks-column",
            )

    def get_no_routine_label(self) -> str:
        """Retorna mensagem quando não há rotina ativa."""
        return "[Nenhuma rotina ativa] - Crie uma com: timeblock routine add"

    def _get_header(self) -> str:
        """Retorna header do dashboard."""
        if self._routine_name:
            return self._routine_name
        return self.get_no_routine_label()
