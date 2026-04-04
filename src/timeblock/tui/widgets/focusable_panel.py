"""FocusablePanel - Base para panels com navegação por cursor (BR-TUI-012).

Adiciona foco, cursor interno e handlers de teclado (setas/j/k)
sobre Static, preservando o padrão update() com Rich markup.
"""

from typing import Any

from textual.events import Key
from textual.message import Message
from textual.widgets import Static


class FocusablePanel(Static):
    """Panel focável com cursor interno para navegação vertical."""

    can_focus = True
    HIGHLIGHT_COLOR: str = "#313244"

    class PlaceholderActivated(Message):
        """Enviada ao coordinator quando Enter é pressionado em placeholder (BR-TUI-013)."""

        def __init__(self, panel_id: str) -> None:
            self.panel_id = panel_id
            super().__init__()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._cursor_index: int = 0
        self._item_count: int = 0
        self._showing_placeholders: bool = False
        self._placeholder_hint: str = ""

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
        """Captura setas, j/k para navegação e Enter em placeholder (BR-TUI-013)."""
        if event.key in ("down", "j"):
            self._move_cursor(1)
            event.stop()
        elif event.key in ("up", "i"):
            self._move_cursor(-1)
            event.stop()
        elif event.key == "enter":
            if self._is_placeholder_index(self._cursor_index):
                self.post_message(self.PlaceholderActivated(self.id or ""))
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

    def _is_placeholder_index(self, index: int) -> bool:
        """Retorna True se o índice aponta para um placeholder navegável."""
        return self._showing_placeholders and 0 <= index < self._item_count

    def _enter_placeholder_mode(
        self,
        placeholder: str,
        hint: str,
        count: int = 3,
    ) -> list[str]:
        """Ativa modo placeholder e retorna linhas de empty state (DT-010, DT-011).

        Unifica _showing_placeholders e _set_item_count em chamada única,
        eliminando risco de divergência entre count visual e count do cursor.
        Hint é armazenado para exibição no footer contextual (DT-066).
        """
        self._showing_placeholders = True
        self._placeholder_hint = hint
        self._set_item_count(count)
        lines: list[str] = []
        for i in range(self._item_count):
            line = f"  [dim]{placeholder}[/dim]"
            if i == self._cursor_index and self.has_focus:
                line = f"[on {self.HIGHLIGHT_COLOR}]{line}[/on {self.HIGHLIGHT_COLOR}]"
            lines.append(line)
        return lines

    def _refresh_content(self) -> None:
        """Subclasses implementam renderização com highlight no cursor."""
        raise NotImplementedError
