"""Card - Widget reutilizável com borda, título e conteúdo.

BR-TUI-008-R02: Cards com borda arredondada, padding 1x2, margin 1.
BR-TUI-008-R03: StatusIndicator com cores semânticas.
BR-TUI-008-R04: Tipografia hierárquica (bold/normal/dim).
"""

from __future__ import annotations

from textual.widgets import Static

# =============================================================================
# BR-TUI-008-R04: Funções de tipografia
# =============================================================================


def format_title(text: str) -> str:
    """Formata texto como título (bold)."""
    return f"[bold]{text}[/bold]"


def format_metadata(text: str) -> str:
    """Formata texto como metadado (dim)."""
    return f"[dim]{text}[/dim]"


def format_content(text: str) -> str:
    """Formata texto como conteúdo (plain, sem markup)."""
    return text


# =============================================================================
# BR-TUI-008-R03: Status colors e indicadores
# =============================================================================

STATUS_MAP = {
    "done": ("success", "✓"),
    "pending": ("warning", "●"),
    "missed": ("error", "✗"),
    "not_done": ("error", "✗"),
    "skipped": ("muted", "○"),
}


class StatusIndicator:
    """Indicador visual de status com cor semântica.

    BR-TUI-008-R03: done=success(verde), pending=warning(amarelo),
    missed/not_done=error(vermelho).
    """

    def __init__(self, status: str) -> None:
        self._status = status
        color_class, symbol = STATUS_MAP.get(status, ("muted", "?"))
        self._color_class = color_class
        self._symbol = symbol

    @property
    def color_class(self) -> str:
        """Classe CSS de cor (success/warning/error/muted)."""
        return self._color_class

    @property
    def symbol(self) -> str:
        """Símbolo textual (sem emoji)."""
        return self._symbol

    def render(self) -> str:
        """Retorna markup Rich com cor e símbolo."""
        color_map = {
            "success": "#A6E3A1",
            "warning": "#F9E2AF",
            "error": "#F38BA8",
            "muted": "#6C7086",
        }
        color = color_map.get(self._color_class, "#6C7086")
        return f"[{color}]{self._symbol}[/{color}]"


# =============================================================================
# BR-TUI-008-R02: Card widget
# =============================================================================


class Card(Static):
    """Card reutilizável com borda, título bold e conteúdo.

    BR-TUI-008-R02: Borda arredondada, padding 1x2, margin 1.
    Segue paleta definida em theme.tcss.
    """

    DEFAULT_CSS = """
    Card {
        border: round $surface-lighten-2;
        padding: 1 2;
        margin: 1;
        width: 100%;
        height: auto;
        background: $surface;
    }
    """

    def __init__(
        self,
        title: str = "",
        content: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._content = content

    @property
    def title_text(self) -> str:
        """Texto do título do card."""
        return self._title

    @property
    def content_text(self) -> str:
        """Texto do conteúdo do card."""
        return self._content

    def get_rendered_title(self) -> str:
        """Retorna título formatado em bold."""
        return format_title(self._title)

    def compose(self):
        """Compõe card com título e conteúdo."""
        if self._title:
            yield Static(self.get_rendered_title(), classes="card-title")
        if self._content:
            yield Static(format_content(self._content), classes="card-content")
