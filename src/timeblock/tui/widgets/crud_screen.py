"""CRUDScreen - Widget base reutilizável para screens CRUD (BR-TUI-005).

Fornece padrão consistente de interação: keybindings, formulários inline,
confirmação de delete, navegação na lista e erro inline.
Todas as screens CRUD (Habits, Tasks, Routines) estendem esta base.
"""

from typing import Any, ClassVar

from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class CRUDScreen(Widget):
    """Base reutilizável para screens com operações CRUD."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("n", "open_create", "Novo", show=True),
        Binding("a", "open_create", "Novo", show=False),
        Binding("e", "open_edit", "Editar", show=True),
        Binding("x", "open_delete", "Deletar", show=True),
        Binding("enter", "view_details", "Detalhes", show=True),
        Binding("j", "move_down", "Baixo", show=False),
        Binding("k", "move_up", "Cima", show=False),
    ]

    mode: reactive[str] = reactive("list")
    selected_index: reactive[int] = reactive(0)
    error_message: reactive[str] = reactive("")
    items: list[dict[str, Any]]

    def __init__(self, title: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.screen_title = title
        self.items = []

    def compose(self):
        """Compõe layout base CRUD."""
        yield Vertical(
            Static(id="crud-header"),
            Static(id="crud-list"),
            Static(id="crud-form"),
            Static(id="crud-error"),
            Static(id="crud-actions"),
            id="crud-content",
        )

    def on_mount(self) -> None:
        """Inicializa display."""
        self._refresh_display()

    # ==================== Navegação ====================

    def _move_selection(self, delta: int) -> None:
        """Move seleção na lista com clamping."""
        if not self.items:
            return
        new_index = self.selected_index + delta
        self.selected_index = max(0, min(new_index, len(self.items) - 1))

    def action_move_down(self) -> None:
        """Move seleção para baixo."""
        self._move_selection(1)

    def action_move_up(self) -> None:
        """Move seleção para cima."""
        self._move_selection(-1)

    # ==================== CRUD Actions ====================

    def action_open_create(self) -> None:
        """Abre formulário de criação."""
        self.error_message = ""
        self.mode = "create"

    def action_open_edit(self) -> None:
        """Abre formulário de edição com dados do item selecionado."""
        if not self.items:
            return
        self.error_message = ""
        self.mode = "edit"

    def action_open_delete(self) -> None:
        """Abre confirmação de delete."""
        if not self.items:
            return
        self.error_message = ""
        self.mode = "confirm_delete"

    def action_view_details(self) -> None:
        """Exibe detalhes do item selecionado."""
        if not self.items:
            return
        self.mode = "detail"

    # ==================== Delete Confirmation ====================

    def _build_delete_confirmation(self, item_name: str) -> str:
        """Constrói mensagem de confirmação de delete."""
        return (
            f"[bold red]Deletar '{item_name}'?[/bold red]\n\n"
            f"  [dim]y[/dim] Confirmar  "
            f"[dim]n/esc[/dim] Cancelar"
        )

    # ==================== Display ====================

    def _build_list_display(self) -> str:
        """Constrói display da lista de items (override nas subclasses)."""
        if not self.items:
            return "[dim]Nenhum item encontrado[/dim]"

        lines = []
        for i, item in enumerate(self.items):
            prefix = "▶ " if i == self.selected_index else "  "
            name = item.get("name", item.get("title", f"Item {i}"))
            lines.append(f"{prefix}{name}")
        return "\n".join(lines)

    def _refresh_display(self) -> None:
        """Atualiza widgets visuais."""
        try:
            self.query_one("#crud-header", Static).update(f"[bold]{self.screen_title}[/bold]")

            if self.mode == "list":
                self.query_one("#crud-list", Static).update(self._build_list_display())
                self.query_one("#crud-form", Static).update("")
            elif self.mode == "confirm_delete" and self.items:
                item = self.items[self.selected_index]
                name = item.get("name", item.get("title", "item"))
                self.query_one("#crud-form", Static).update(self._build_delete_confirmation(name))

            # Erro inline
            if self.error_message:
                self.query_one("#crud-error", Static).update(
                    f"[bold red]{self.error_message}[/bold red]"
                )
            else:
                self.query_one("#crud-error", Static).update("")

            # Ações contextuais
            if self.mode == "list":
                self.query_one("#crud-actions", Static).update(
                    "[dim]n[/dim] Novo  [dim]e[/dim] Editar  "
                    "[dim]x[/dim] Deletar  [dim]enter[/dim] Detalhes"
                )
            elif self.mode in ("create", "edit"):
                self.query_one("#crud-actions", Static).update(
                    "[dim]enter[/dim] Salvar  [dim]esc[/dim] Cancelar"
                )
            elif self.mode == "confirm_delete":
                self.query_one("#crud-actions", Static).update(
                    "[dim]y[/dim] Confirmar  [dim]n/esc[/dim] Cancelar"
                )
        except Exception:
            pass

    # ==================== Watchers ====================

    def watch_mode(self, _value: str) -> None:
        """Reage à mudança de modo."""
        self._refresh_display()

    def watch_selected_index(self, _value: int) -> None:
        """Reage à mudança de seleção."""
        self._refresh_display()

    def watch_error_message(self, _value: str) -> None:
        """Reage à mudança de erro."""
        self._refresh_display()

    # ==================== Hooks para subclasses ====================

    def load_items(self) -> None:
        """Carrega items do service (override nas subclasses)."""

    def on_create_submit(self, data: dict[str, Any]) -> None:
        """Callback ao submeter criação (override nas subclasses)."""

    def on_edit_submit(self, data: dict[str, Any]) -> None:
        """Callback ao submeter edição (override nas subclasses)."""

    def on_delete_confirm(self) -> None:
        """Callback ao confirmar delete (override nas subclasses)."""

    def get_item_name(self, item: dict[str, Any]) -> str:
        """Retorna nome do item para display (override nas subclasses)."""
        return str(item.get("name", item.get("title", "item")))
