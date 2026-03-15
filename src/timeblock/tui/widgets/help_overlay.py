"""HelpOverlay - Overlay de ajuda com keybindings (ADR-037)."""

from textual.widgets import Static


class HelpOverlay(Static):
    """Overlay exibindo lista de keybindings disponíveis."""

    def __init__(self) -> None:
        content = (
            "[bold]Globais[/]\n"
            "\n"
            "  1..5       Alternar screens\n"
            "  Tab        Proximo panel\n"
            "  ?          Ajuda\n"
            "  Ctrl+Q     Sair\n"
            "\n"
            "[bold]Navegacao[/]\n"
            "\n"
            "  j/i        Cursor baixo/cima\n"
            "  t/b        Topo / Base da lista\n"
            "\n"
            "[bold]CRUD (contextual)[/]\n"
            "\n"
            "  n          Novo item\n"
            "  e          Editar item\n"
            "  x          Deletar item\n"
            "\n"
            "[bold]Habitos[/]\n"
            "\n"
            "  v          Marcar done\n"
            "  s          Skip\n"
            "  u          Desfazer\n"
            "\n"
            "[bold]Tasks[/]\n"
            "\n"
            "  v          Completar\n"
            "  s          Adiar\n"
            "  c          Cancelar\n"
            "  u          Reabrir\n"
            "\n"
            "[bold]Timer[/]\n"
            "\n"
            "  space      Pausar / Resumir\n"
            "  c          Cancelar timer\n"
            "\n"
            "[bold]Agenda[/]\n"
            "\n"
            "  a          Ir para hora atual\n"
        )
        super().__init__(content, id="help-overlay")
