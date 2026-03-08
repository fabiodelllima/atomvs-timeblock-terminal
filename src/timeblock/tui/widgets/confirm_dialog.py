"""ConfirmDialog - Modal de confirmação para operações destrutivas (BR-TUI-019).

Overlay com foco exclusivo (modal trap). Enter confirma, Esc cancela.
Ao fechar, foco retorna ao widget anterior.

Referências:
    - BR-TUI-019: ConfirmDialog
    - ADR-034: Dashboard-first CRUD
"""

from collections.abc import Callable
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label


class ConfirmDialog(ModalScreen[bool]):
    """Modal de confirmação reutilizável."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("enter", "confirm", "Confirmar", show=False),
        Binding("escape", "cancel", "Cancelar", show=False),
    ]

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    ConfirmDialog > Vertical {
        width: 50;
        height: auto;
        max-height: 12;
        border: thick $error;
        background: #181825;
        padding: 1 2;
    }

    ConfirmDialog > Vertical > #cd-title {
        text-align: center;
        text-style: bold;
        color: #F38BA8;
        margin-bottom: 1;
    }

    ConfirmDialog > Vertical > #cd-message {
        text-align: center;
        color: #CDD6F4;
        margin-bottom: 1;
    }

    ConfirmDialog > Vertical > #cd-hint {
        text-align: center;
        color: #6C7086;
    }
    """

    def __init__(
        self,
        title: str = "Confirmar",
        message: str = "Tem certeza?",
        on_confirm: Callable[[], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._message = message
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

    def compose(self) -> ComposeResult:
        """Compõe layout: título, mensagem, hint."""
        with Vertical():
            yield Label(self._title, id="cd-title")
            yield Label(self._message, id="cd-message")
            yield Label("Enter confirmar  Esc cancelar", id="cd-hint")

    def action_confirm(self) -> None:
        """Confirma operação e fecha modal."""
        if self._on_confirm:
            self._on_confirm()
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancela operação e fecha modal."""
        if self._on_cancel:
            self._on_cancel()
        self.dismiss(False)
