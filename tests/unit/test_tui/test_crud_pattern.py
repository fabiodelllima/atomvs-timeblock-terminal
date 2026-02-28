"""Testes para BR-TUI-005: CRUD Operations Pattern.

Valida CRUDScreen base com keybindings, formulários e confirmações.
"""

from textual.binding import Binding

from timeblock.tui.widgets.crud_screen import CRUDScreen

# ============================================================
# BR-TUI-005 R01: Keybindings CRUD consistentes
# ============================================================


class TestBRTUI005R01CRUDKeybindings:
    """BR-TUI-005 R01: Keybindings n/e/x/enter em toda CRUD screen."""

    def _get_binding_keys(self) -> list[str]:
        """Extrai teclas dos bindings."""
        return [b.key if isinstance(b, Binding) else b[0] for b in CRUDScreen.BINDINGS]

    def test_br_tui_005_r01_create_keybinding_n(self) -> None:
        """'n' abre formulário de criação."""
        keys = self._get_binding_keys()
        assert "n" in keys

    def test_br_tui_005_r01_create_keybinding_a(self) -> None:
        """'a' também abre formulário de criação."""
        keys = self._get_binding_keys()
        assert "a" in keys

    def test_br_tui_005_r01_edit_keybinding(self) -> None:
        """'e' abre formulário de edição."""
        keys = self._get_binding_keys()
        assert "e" in keys

    def test_br_tui_005_r01_delete_keybinding(self) -> None:
        """'x' abre confirmação de delete."""
        keys = self._get_binding_keys()
        assert "x" in keys

    def test_br_tui_005_r01_details_keybinding(self) -> None:
        """'enter' exibe detalhes."""
        keys = self._get_binding_keys()
        assert "enter" in keys


# ============================================================
# BR-TUI-005 R02: Estado do formulário
# ============================================================


class TestBRTUI005R02FormState:
    """BR-TUI-005 R02: Formulário inline com estados."""

    def test_br_tui_005_r02_default_mode_is_list(self) -> None:
        """Modo padrão é list (sem formulário aberto)."""
        screen = CRUDScreen(title="Test")
        assert screen.mode == "list"

    def test_br_tui_005_r02_mode_create(self) -> None:
        """Modo create ao abrir formulário."""
        screen = CRUDScreen(title="Test")
        screen.mode = "create"
        assert screen.mode == "create"

    def test_br_tui_005_r02_mode_edit(self) -> None:
        """Modo edit ao editar item."""
        screen = CRUDScreen(title="Test")
        screen.mode = "edit"
        assert screen.mode == "edit"

    def test_br_tui_005_r02_mode_confirm_delete(self) -> None:
        """Modo confirm_delete ao solicitar exclusão."""
        screen = CRUDScreen(title="Test")
        screen.mode = "confirm_delete"
        assert screen.mode == "confirm_delete"


# ============================================================
# BR-TUI-005 R03: Seleção de item
# ============================================================


class TestBRTUI005R03ItemSelection:
    """BR-TUI-005 R03: Item selecionado para operações."""

    def test_br_tui_005_r03_no_item_selected_by_default(self) -> None:
        """Nenhum item selecionado inicialmente."""
        screen = CRUDScreen(title="Test")
        assert screen.selected_index == 0

    def test_br_tui_005_r03_selected_index_tracks_position(self) -> None:
        """Índice de seleção rastreável."""
        screen = CRUDScreen(title="Test")
        screen.selected_index = 3
        assert screen.selected_index == 3

    def test_br_tui_005_r03_items_list_default_empty(self) -> None:
        """Lista de items inicia vazia."""
        screen = CRUDScreen(title="Test")
        assert screen.items == []


# ============================================================
# BR-TUI-005 R04: Navegação na lista
# ============================================================


class TestBRTUI005R04ListNavigation:
    """BR-TUI-005 R04: Navegação j/k na lista."""

    def _get_binding_keys(self) -> list[str]:
        """Extrai teclas dos bindings."""
        return [b.key if isinstance(b, Binding) else b[0] for b in CRUDScreen.BINDINGS]

    def test_br_tui_005_r04_navigate_down_keybinding(self) -> None:
        """'j' navega para baixo."""
        keys = self._get_binding_keys()
        assert "j" in keys

    def test_br_tui_005_r04_navigate_up_keybinding(self) -> None:
        """'k' navega para cima."""
        keys = self._get_binding_keys()
        assert "k" in keys

    def test_br_tui_005_r04_move_down_increments(self) -> None:
        """Move down incrementa selected_index."""
        screen = CRUDScreen(title="Test")
        screen.items = [{"id": 1}, {"id": 2}, {"id": 3}]
        screen.selected_index = 0
        screen._move_selection(1)
        assert screen.selected_index == 1

    def test_br_tui_005_r04_move_up_decrements(self) -> None:
        """Move up decrementa selected_index."""
        screen = CRUDScreen(title="Test")
        screen.items = [{"id": 1}, {"id": 2}, {"id": 3}]
        screen.selected_index = 2
        screen._move_selection(-1)
        assert screen.selected_index == 1

    def test_br_tui_005_r04_clamp_at_top(self) -> None:
        """Não ultrapassa topo da lista."""
        screen = CRUDScreen(title="Test")
        screen.items = [{"id": 1}, {"id": 2}]
        screen.selected_index = 0
        screen._move_selection(-1)
        assert screen.selected_index == 0

    def test_br_tui_005_r04_clamp_at_bottom(self) -> None:
        """Não ultrapassa fim da lista."""
        screen = CRUDScreen(title="Test")
        screen.items = [{"id": 1}, {"id": 2}]
        screen.selected_index = 1
        screen._move_selection(1)
        assert screen.selected_index == 1

    def test_br_tui_005_r04_empty_list_no_crash(self) -> None:
        """Lista vazia não causa erro."""
        screen = CRUDScreen(title="Test")
        screen.items = []
        screen._move_selection(1)
        assert screen.selected_index == 0


# ============================================================
# BR-TUI-005 R05: Confirmação de delete
# ============================================================


class TestBRTUI005R05DeleteConfirmation:
    """BR-TUI-005 R05: Delete requer confirmação com nome do item."""

    def test_br_tui_005_r05_build_confirmation_message(self) -> None:
        """Mensagem de confirmação contém nome do item."""
        screen = CRUDScreen(title="Test")
        msg = screen._build_delete_confirmation("Academia")
        assert "Academia" in msg

    def test_br_tui_005_r05_confirmation_requires_y(self) -> None:
        """Confirmação menciona 'y' para confirmar."""
        screen = CRUDScreen(title="Test")
        msg = screen._build_delete_confirmation("Academia")
        assert "y" in msg.lower()

    def test_br_tui_005_r05_confirmation_shows_cancel(self) -> None:
        """Confirmação mostra opção de cancelar."""
        screen = CRUDScreen(title="Test")
        msg = screen._build_delete_confirmation("Academia")
        assert "n" in msg.lower() or "cancel" in msg.lower() or "esc" in msg.lower()


# ============================================================
# BR-TUI-005 R06: Erro inline
# ============================================================


class TestBRTUI005R06InlineErrors:
    """BR-TUI-005 R06: Erros de validação exibidos inline."""

    def test_br_tui_005_r06_error_message_default_empty(self) -> None:
        """Mensagem de erro padrão é vazia."""
        screen = CRUDScreen(title="Test")
        assert screen.error_message == ""

    def test_br_tui_005_r06_set_error_message(self) -> None:
        """Erro pode ser definido."""
        screen = CRUDScreen(title="Test")
        screen.error_message = "Título não pode ser vazio"
        assert screen.error_message == "Título não pode ser vazio"

    def test_br_tui_005_r06_clear_error(self) -> None:
        """Erro pode ser limpo."""
        screen = CRUDScreen(title="Test")
        screen.error_message = "Erro"
        screen.error_message = ""
        assert screen.error_message == ""


# ============================================================
# BR-TUI-005 R07: Title configurável
# ============================================================


class TestBRTUI005R07ConfigurableTitle:
    """BR-TUI-005 R07: CRUDScreen com título configurável."""

    def test_br_tui_005_r07_title_stored(self) -> None:
        """Título passado no construtor."""
        screen = CRUDScreen(title="Hábitos")
        assert screen.screen_title == "Hábitos"

    def test_br_tui_005_r07_different_titles(self) -> None:
        """Diferentes screens com diferentes títulos."""
        habits = CRUDScreen(title="Hábitos")
        tasks = CRUDScreen(title="Tasks")
        assert habits.screen_title != tasks.screen_title
