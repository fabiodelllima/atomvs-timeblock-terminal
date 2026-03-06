"""FormModal - Modal de formulário para criação e edição (BR-TUI-020).

Suporta campos tipados (text, time, number, select) com validação inline.
Tab navega entre campos, Enter submete, Esc cancela.

Referências:
    - BR-TUI-020: FormModal
    - ADR-034: Dashboard-first CRUD
"""

from collections.abc import Callable
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label


class FormField:
    """Definição de um campo do formulário."""

    def __init__(
        self,
        name: str,
        label: str,
        field_type: str = "text",
        required: bool = False,
        default: str = "",
        placeholder: str = "",
        options: list[tuple[str, str]] | None = None,
    ) -> None:
        self.name = name
        self.label = label
        self.field_type = field_type
        self.required = required
        self.default = default
        self.placeholder = placeholder
        self.options = options or []


class FormModal(ModalScreen[dict[str, Any] | None]):
    """Modal de formulário reutilizável com validação inline."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape", "cancel", "Cancelar", show=False),
    ]

    DEFAULT_CSS = """
    FormModal {
        align: center middle;
    }

    FormModal > Vertical {
        width: 60;
        height: auto;
        max-height: 24;
        border: thick #89B4FA;
        background: #181825;
        padding: 1 2;
    }

    FormModal > Vertical > #fm-title {
        text-align: center;
        text-style: bold;
        color: #89B4FA;
        margin-bottom: 1;
    }

    FormModal > Vertical > .fm-label {
        color: #CDD6F4;
        margin-top: 1;
    }

    FormModal > Vertical > .fm-error {
        color: #F38BA8;
        margin-bottom: 0;
    }

    FormModal > Vertical > #fm-hint {
        text-align: center;
        color: #6C7086;
        margin-top: 1;
    }

    FormModal > Vertical > Input {
        border: tall #585B70;
        margin-bottom: 0;
    }

    FormModal > Vertical > Input:focus {
        border: tall #89B4FA;
    }
    """

    def __init__(
        self,
        title: str = "Formulário",
        fields: list[FormField] | None = None,
        on_submit: Callable[[dict[str, Any]], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
        edit_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__()
        self._title = title
        self._fields = fields or []
        self._on_submit = on_submit
        self._on_cancel = on_cancel
        self._edit_data = edit_data or {}

    @property
    def is_edit_mode(self) -> bool:
        """Retorna True se formulário está em modo edição."""
        return bool(self._edit_data)

    def compose(self) -> ComposeResult:
        """Compõe layout: título, campos com labels, hint."""
        with Vertical():
            yield Label(self._title, id="fm-title")
            for field in self._fields:
                yield Label(field.label, classes="fm-label")
                default = self._edit_data.get(field.name, field.default)
                yield Input(
                    value=str(default) if default else "",
                    placeholder=field.placeholder or field.label,
                    id=f"fm-input-{field.name}",
                )
                yield Label("", classes="fm-error", id=f"fm-err-{field.name}")
            yield Label("Tab navegar  Enter salvar  Esc cancelar", id="fm-hint")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Enter em qualquer campo submete o formulário."""
        self._try_submit()

    def action_cancel(self) -> None:
        """Cancela formulário e fecha modal."""
        if self._on_cancel:
            self._on_cancel()
        self.dismiss(None)

    def _try_submit(self) -> None:
        """Valida campos e submete se tudo válido."""
        data: dict[str, Any] = {}
        has_errors = False

        for field in self._fields:
            input_widget = self.query_one(f"#fm-input-{field.name}", Input)
            error_label = self.query_one(f"#fm-err-{field.name}", Label)
            value = input_widget.value.strip()

            error = self._validate_field(field, value)
            if error:
                error_label.update(error)
                has_errors = True
            else:
                error_label.update("")
                data[field.name] = self._convert_value(field, value)

        if not has_errors:
            if self._on_submit:
                self._on_submit(data)
            self.dismiss(data)

    @staticmethod
    def _validate_field(field: FormField, value: str) -> str:
        """Valida campo e retorna mensagem de erro ou string vazia."""
        if field.required and not value:
            return f"{field.label} é obrigatório"

        if value and field.field_type == "time":
            parts = value.split(":")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                return "Formato: HH:MM"
            h, m = int(parts[0]), int(parts[1])
            if not (0 <= h <= 23 and 0 <= m <= 59):
                return "Horário inválido"

        if value and field.field_type == "number":
            if not value.isdigit() or int(value) <= 0:
                return "Deve ser número positivo"

        return ""

    @staticmethod
    def _convert_value(field: FormField, value: str) -> Any:
        """Converte valor string para tipo apropriado."""
        if not value:
            return None
        if field.field_type == "number":
            return int(value)
        return value
