"""HelpOverlay - Overlay de ajuda com keybindings (ADR-035)."""

from textual.widgets import Static


class HelpOverlay(Static):
    """Overlay exibindo lista de keybindings disponíveis."""

    def __init__(self) -> None:
        content = (
            "[bold]Atalhos Globais[/]\n"
            "\n"
            "  1..5     Alternar screens\n"
            "  Ctrl+Q     Sair\n"
            "  ?          Ajuda\n"
            "  Escape     Fechar / Dashboard\n"
            "\n"
            "[bold]Navegação[/]\n"
            "\n"
            "  Tab        Próximo panel\n"
            "  ↑↓ / j/k   Cursor\n"
            "  n / e / x  Novo / Editar / Deletar\n"
            "\n"
            "[bold]Quick Actions[/]\n"
            "\n"
            "  Ctrl+Enter  Done / Concluir\n"
            "  Ctrl+S      Skip (hábitos)\n"
        )
        super().__init__(content, id="help-overlay")
