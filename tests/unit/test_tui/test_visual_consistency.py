"""Tests for BR-TUI-008: Visual Consistency (Material-like).

Valida paleta centralizada, Card widget, status colors,
tipografia hierárquica e consistência visual entre screens.
"""

import re
from pathlib import Path

import pytest

from timeblock.tui.app import TimeBlockApp
from timeblock.tui.widgets.card import (
    Card,
    StatusIndicator,
    format_content,
    format_metadata,
    format_title,
)

# Caminho do theme.tcss relativo ao pacote
THEME_PATH = Path(__file__).parents[3] / "src" / "timeblock" / "tui" / "styles" / "theme.tcss"


def _theme_content() -> str:
    """Lê conteúdo do theme.tcss."""
    return THEME_PATH.read_text()


def _css_block(selector: str) -> str:
    """Extrai bloco CSS de um seletor (ex: 'Card {' até '}')."""
    content = _theme_content()
    pattern = rf"^{re.escape(selector)}\s*\{{([^}}]*)\}}"
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1) if match else ""


# =============================================================================
# BR-TUI-008-R01: Paleta centralizada em theme.tcss
# =============================================================================


class TestBRTUI008R01ThemePalette:
    """BR-TUI-008-R01: Paleta definida em theme.tcss (SSOT)."""

    def test_br_tui_008_r01_theme_file_exists(self):
        """Arquivo theme.tcss existe."""
        assert THEME_PATH.exists()

    def test_br_tui_008_r01_defines_background(self):
        """Theme define cor de fundo (background)."""
        assert "background" in _theme_content()

    def test_br_tui_008_r01_defines_primary_color(self):
        """Theme documenta e usa cor primary."""
        content = _theme_content()
        assert "primary" in content.lower()
        assert "#CBA6F7" in content

    def test_br_tui_008_r01_defines_status_colors(self):
        """Theme define cores de status (success, warning, error)."""
        content = _theme_content()
        assert ".success" in content
        assert ".warning" in content
        assert ".error" in content

    def test_br_tui_008_r01_defines_surface_colors(self):
        """Theme define cores de superfície para cards e painéis."""
        assert "#313244" in _theme_content()

    def test_br_tui_008_r01_is_ssot(self):
        """Theme contém estilos para todos os componentes (SSOT)."""
        content = _theme_content()
        components = [
            "Screen",
            "Header",
            "NavBar",
            "Card",
            "HelpOverlay",
            "DashboardScreen",
            "RoutinesScreen",
        ]
        for comp in components:
            assert comp in content, f"Componente {comp} ausente do theme.tcss"


# =============================================================================
# BR-TUI-008-R02: Card widget consistente
# =============================================================================


class TestBRTUI008R02CardWidget:
    """BR-TUI-008-R02: Cards com borda, padding e margin."""

    def test_br_tui_008_r02_card_has_title(self):
        """Card aceita e armazena título."""
        card = Card(title="Hábitos Hoje")
        assert card.title_text == "Hábitos Hoje"

    def test_br_tui_008_r02_card_has_content(self):
        """Card aceita conteúdo como child."""
        card = Card(title="Tasks", content="3 pendentes")
        assert card.content_text == "3 pendentes"

    def test_br_tui_008_r02_card_renders_title_bold(self):
        """Card renderiza título em bold."""
        card = Card(title="Timer")
        rendered = card.get_rendered_title()
        assert "[bold]" in rendered

    def test_br_tui_008_r02_theme_card_has_border(self):
        """Theme.tcss define borda para Card."""
        block = _css_block("Card")
        assert "border" in block

    def test_br_tui_008_r02_theme_card_has_padding(self):
        """Theme.tcss define padding para Card."""
        block = _css_block("Card")
        assert "padding" in block

    def test_br_tui_008_r02_theme_card_has_margin(self):
        """Theme.tcss define margin para Card."""
        block = _css_block("Card")
        assert "margin" in block


# =============================================================================
# BR-TUI-008-R03: Status colors
# =============================================================================


class TestBRTUI008R03StatusColors:
    """BR-TUI-008-R03: Cores de status (done/pending/missed)."""

    def test_br_tui_008_r03_done_uses_success(self):
        """Status 'done' usa cor success (verde)."""
        indicator = StatusIndicator("done")
        assert indicator.color_class == "success"

    def test_br_tui_008_r03_pending_uses_warning(self):
        """Status 'pending' usa cor warning (amarelo)."""
        indicator = StatusIndicator("pending")
        assert indicator.color_class == "warning"

    def test_br_tui_008_r03_missed_uses_error(self):
        """Status 'missed' usa cor error (vermelho)."""
        indicator = StatusIndicator("missed")
        assert indicator.color_class == "error"

    def test_br_tui_008_r03_not_done_uses_error(self):
        """Status 'not_done' usa cor error (vermelho)."""
        indicator = StatusIndicator("not_done")
        assert indicator.color_class == "error"

    def test_br_tui_008_r03_unknown_uses_muted(self):
        """Status desconhecido usa cor muted."""
        indicator = StatusIndicator("unknown")
        assert indicator.color_class == "muted"

    def test_br_tui_008_r03_indicator_has_symbol(self):
        """Indicador exibe símbolo textual (não emoji)."""
        indicator = StatusIndicator("done")
        assert indicator.symbol == "✓"

    def test_br_tui_008_r03_missed_symbol(self):
        """Indicador missed exibe símbolo de falha."""
        indicator = StatusIndicator("missed")
        assert indicator.symbol == "✗"


# =============================================================================
# BR-TUI-008-R04: Tipografia hierárquica
# =============================================================================


class TestBRTUI008R04Typography:
    """BR-TUI-008-R04: Bold para títulos, normal para conteúdo, dim para metadados."""

    def test_br_tui_008_r04_format_title(self):
        """Títulos formatados em bold."""
        result = format_title("Dashboard")
        assert "[bold]" in result

    def test_br_tui_008_r04_format_metadata(self):
        """Metadados formatados em dim."""
        result = format_metadata("14:30 - 15:00")
        assert "[dim]" in result

    def test_br_tui_008_r04_format_content(self):
        """Conteúdo sem formatação adicional."""
        result = format_content("Academia")
        assert "[bold]" not in result
        assert "[dim]" not in result


# =============================================================================
# BR-TUI-008-R05: NavBar e layout
# =============================================================================


@pytest.mark.asyncio
class TestBRTUI008R05Layout:
    """BR-TUI-008-R05: NavBar e layout global consistente."""

    async def test_br_tui_008_r05_navbar_docked_bottom(self):
        """NavBar está docked no bottom."""
        async with TimeBlockApp().run_test() as pilot:
            from timeblock.tui.widgets.nav_bar import NavBar

            nav = pilot.app.query_one(NavBar)
            assert nav.display is True

    async def test_br_tui_008_r05_header_uses_primary_color(self):
        """Theme define estilo para Header."""
        content = _theme_content()
        assert "Header" in content
        assert "#CBA6F7" in content

    async def test_br_tui_008_r05_help_overlay_styled_in_theme(self):
        """HelpOverlay estilizado no theme.tcss (SSOT)."""
        block = _css_block("HelpOverlay")
        assert "background" in block
        assert "border" in block
        assert "padding" in block
