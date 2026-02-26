"""HelpOverlay - Overlay de ajuda com keybindings."""

from textual.widgets import Static


class HelpOverlay(Static):
    """Overlay exibindo lista de keybindings disponíveis."""

    def __init__(self) -> None:
        content = (
            "[bold]Atalhos Globais[/]\n"
            "\n"
            "  1 / d    Dashboard\n"
            "  2 / r    Rotinas\n"
            "  3 / h    Hábitos\n"
            "  4 / t    Tasks\n"
            "  5 / m    Timer\n"
            "\n"
            "  ?        Ajuda\n"
            "  escape   Fechar / Dashboard\n"
            "  q        Sair\n"
        )
        super().__init__(content, id="help-overlay")
