"""FocusablePanel - Base para panels com navegação por cursor (BR-TUI-012).

Adiciona foco, cursor interno e handlers de teclado (setas/j/k)
sobre Static, preservando o padrão update() com Rich markup.
"""

from textual.events import Key
from textual.message import Message
from textual.widgets import Static

from timeblock.tui.colors import C_HIGHLIGHT


class FocusablePanel(Static):
    """Panel focável com cursor interno para navegação vertical."""

    can_focus = True

    class PlaceholderActivated(Message):
        """Enviada ao coordinator quando Enter é pressionado em placeholder (BR-TUI-013)."""

        def __init__(self, panel_id: str) -> None:
            self.panel_id = panel_id
            super().__init__()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cursor_index: int = 0
        self._item_count: int = 0
        self._showing_placeholders: bool = False

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
        elif event.key in ("up", "k"):
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

    def _build_empty_state(
        self,
        placeholder: str,
        hint: str,
        count: int = 3,
    ) -> list[str]:
        """Constrói linhas de empty state com highlight e hint (RF-007).

        Centraliza a lógica de placeholder repetida em subclasses.
        Placeholders são navegáveis — highlight aplica-se normalmente.
        """
        lines: list[str] = []
        for i in range(count):
            line = f"  [dim]{placeholder}[/dim]"
            if i == self._cursor_index and self.has_focus:
                line = f"[on {C_HIGHLIGHT}]{line}[/on {C_HIGHLIGHT}]"
            lines.append(line)
        lines.append("")
        lines.append(f"  [dim]{hint}[/dim]")
        return lines

    def _refresh_content(self) -> None:
        """Subclasses implementam renderização com highlight no cursor."""
        raise NotImplementedError
