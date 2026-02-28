"""TasksScreen - Placeholder para tela de tarefas."""

from textual.widgets import Static


class TasksScreen(Static):
    """Tela de Tasks (placeholder para implementação futura)."""

    DEFAULT_CSS = """
    TasksScreen {
        width: 100%;
        height: 100%;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def compose(self):
        """Compõe layout placeholder."""
        yield Static("Tasks - Em desenvolvimento")
