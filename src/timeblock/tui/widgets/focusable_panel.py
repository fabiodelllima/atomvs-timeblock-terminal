"""FocusablePanel - Base para panels com navegação por cursor (BR-TUI-012).

Adiciona foco, cursor interno e handlers de teclado (setas/j/k)
sobre Static, preservando o padrão update() com Rich markup.
"""

from textual.events import Key
from textual.widgets import Static


class FocusablePanel(Static):
    """Panel focável com cursor interno para navegação vertical."""

    can_focus = True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cursor_index: int = 0
        self._item_count: int = 0

    @property
    def cursor_index(self) -> int:
        """Índice do item selecionado."""
        return self._cursor_index

    def _set_item_count(self, count: int) -> None:
        """Atualiza total de itens e ajusta cursor se necessário."""
        self._item_count = count
        if self._item_count == 0:
            self._cursor_index = 0
        elif self._cursor_index >= self._item_count:
            self._cursor_index = self._item_count - 1

    def on_key(self, event: Key) -> None:
        """Captura setas e j/k para navegação vertical."""
        if event.key in ("down", "j"):
            self._move_cursor(1)
            event.stop()
        elif event.key in ("up", "k"):
            self._move_cursor(-1)
            event.stop()

    def _move_cursor(self, delta: int) -> None:
        """Move cursor com bounds checking e re-renderiza."""
        if self._item_count == 0:
            return
        new_index = self._cursor_index + delta
        new_index = max(0, min(self._item_count - 1, new_index))
        if new_index != self._cursor_index:
            self._cursor_index = new_index
            self._refresh_content()

    def _refresh_content(self) -> None:
        """Subclasses implementam renderização com highlight no cursor."""
        raise NotImplementedError
