"""HelpOverlay - Overlay de ajuda com keybindings."""

from textual.widgets import Static


class HelpOverlay(Static):
    """Overlay exibindo lista de keybindings disponíveis."""

    DEFAULT_CSS = """
    HelpOverlay {
        width: 60;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: solid $primary;
        padding: 1 2;
        layer: overlay;
        align: center middle;
        dock: top;
        margin: 4 10;
    }
    """

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
