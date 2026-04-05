"""FormModal - Modal de formulário para criação e edição (BR-TUI-020).

Suporta campos tipados (text, time, number, select) com validação inline.
Tab navega entre campos, Enter submete (em Input) ou clique no botão
Confirmar. Esc cancela.

Referências:
    - BR-TUI-020: FormModal
    - ADR-034: Dashboard-first CRUD
    - DT-043: CSS movido para styles/forms.tcss
"""

from collections.abc import Callable
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select


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
        """Compõe layout: título, campos com labels, botão e hint."""
        with Vertical():
            yield Label(self._title, id="fm-title")
            for field in self._fields:
                yield Label(field.label, classes="fm-label")
                default = self._edit_data.get(field.name, field.default)
                if field.field_type == "select" and field.options:
                    options = [(label, value) for value, label in field.options]
                    initial = str(default) if default else field.options[0][0]
                    yield Select(
                        options,
                        value=initial,
                        id=f"fm-input-{field.name}",
                        allow_blank=False,
                    )
                else:
                    yield Input(
                        value=str(default) if default else "",
                        placeholder=field.placeholder or field.label,
                        id=f"fm-input-{field.name}",
                    )
                yield Label("", classes="fm-error", id=f"fm-err-{field.name}")
            yield Button("Confirmar", id="fm-submit", variant="primary")
            yield Label("Tab navegar  Enter confirmar  Esc cancelar", id="fm-hint")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Enter em qualquer campo Input submete o formulário."""
        self._try_submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Clique no botão Confirmar submete o formulário."""
        if event.button.id == "fm-submit":
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
            error_label = self.query_one(f"#fm-err-{field.name}", Label)
            if field.field_type == "select" and field.options:
                select_widget = self.query_one(f"#fm-input-{field.name}", Select)
                value = str(select_widget.value) if select_widget.value else ""
            else:
                input_widget = self.query_one(f"#fm-input-{field.name}", Input)
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

        if value and field.field_type == "date":
            parts = value.split("/")
            if len(parts) not in (2, 3):
                return "Formato: DD/MM ou DD/MM/YYYY"
            try:
                day, month = int(parts[0]), int(parts[1])
                year = int(parts[2]) if len(parts) == 3 else 2000
                if not (1 <= day <= 31 and 1 <= month <= 12 and year >= 1900):
                    return "Data inválida"
            except ValueError:
                return "Formato: DD/MM ou DD/MM/YYYY"

        return ""

    @staticmethod
    def _convert_value(field: FormField, value: str) -> Any:
        """Converte valor string para tipo apropriado."""
        if not value:
            return None
        if field.field_type == "number":
            return int(value)
        if field.field_type == "date":
            from datetime import date as _date

            parts = value.split("/")
            day, month = int(parts[0]), int(parts[1])
            year = int(parts[2]) if len(parts) == 3 else _date.today().year
            return f"{year:04d}-{month:02d}-{day:02d}"
        return value
