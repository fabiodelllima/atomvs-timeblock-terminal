"""Testes para BR-TUI-007: Status Bar.

Valida widget StatusBar com três seções: rotina ativa, timer e hora.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from timeblock.tui.widgets.status_bar import StatusBar

# ============================================================
# BR-TUI-007 R01: Status bar existe e é dockável
# ============================================================


class TestBRTUI007R01StatusBarWidget:
    """BR-TUI-007 R01: Status bar como widget Textual."""

    def test_br_tui_007_r01_widget_exists(self) -> None:
        """StatusBar é instanciável."""
        bar = StatusBar()
        assert bar is not None

    def test_br_tui_007_r01_widget_has_id(self) -> None:
        """StatusBar tem ID padrão para seleção CSS."""
        bar = StatusBar()
        assert bar.id == "status-bar"

    def test_br_tui_007_r01_docked_bottom_in_theme(self) -> None:
        """StatusBar tem dock: bottom no theme.tcss."""
        from pathlib import Path

        theme_path = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "timeblock"
            / "tui"
            / "styles"
            / "theme.tcss"
        )
        css = theme_path.read_text()
        assert "#status-bar" in css, "StatusBar deve ter regra CSS no tema"
        # Verifica dock bottom
        in_block = False
        for line in css.splitlines():
            if "#status-bar" in line and "{" in line:
                in_block = True
            if in_block:
                if "dock:" in line and "bottom" in line:
                    break
                if "}" in line:
                    in_block = False
        else:
            pytest.fail("StatusBar deve ter dock: bottom no theme.tcss")


# ============================================================
# BR-TUI-007 R02: Seção esquerda - rotina ativa
# ============================================================


class TestBRTUI007R02ActiveRoutine:
    """BR-TUI-007 R02: Exibe nome da rotina ativa."""

    def test_br_tui_007_r02_shows_routine_name(self) -> None:
        """Exibe nome da rotina quando definida."""
        bar = StatusBar()
        bar.routine_name = "Rotina Matinal"
        assert bar.routine_name == "Rotina Matinal"

    def test_br_tui_007_r02_default_is_no_routine(self) -> None:
        """Padrão é sem rotina."""
        bar = StatusBar()
        assert bar.routine_name == ""

    def test_br_tui_007_r02_render_contains_routine(self) -> None:
        """Render inclui nome da rotina."""
        bar = StatusBar()
        bar.routine_name = "Rotina Matinal"
        rendered = bar._build_left_section()
        assert "Rotina Matinal" in rendered


# ============================================================
# BR-TUI-007 R07: Placeholder sem rotina
# ============================================================


class TestBRTUI007R07NoRoutinePlaceholder:
    """BR-TUI-007 R07: Exibe '[Sem rotina]' quando nenhuma rotina ativa."""

    def test_br_tui_007_r07_no_routine_placeholder(self) -> None:
        """Exibe placeholder quando routine_name vazio."""
        bar = StatusBar()
        bar.routine_name = ""
        rendered = bar._build_left_section()
        assert "[Sem rotina]" in rendered

    def test_br_tui_007_r07_routine_replaces_placeholder(self) -> None:
        """Placeholder desaparece quando rotina definida."""
        bar = StatusBar()
        bar.routine_name = "Minha Rotina"
        rendered = bar._build_left_section()
        assert "[Sem rotina]" not in rendered
        assert "Minha Rotina" in rendered


# ============================================================
# BR-TUI-007 R03: Seção central - timer ativo
# ============================================================


class TestBRTUI007R03ActiveTimer:
    """BR-TUI-007 R03: Exibe timer ativo com tempo decorrido."""

    def test_br_tui_007_r03_shows_timer_habit(self) -> None:
        """Exibe nome do habit no timer."""
        bar = StatusBar()
        bar.timer_habit = "Academia"
        bar.timer_elapsed = "00:45:30"
        rendered = bar._build_center_section()
        assert "Academia" in rendered

    def test_br_tui_007_r03_shows_timer_elapsed(self) -> None:
        """Exibe tempo decorrido."""
        bar = StatusBar()
        bar.timer_habit = "Academia"
        bar.timer_elapsed = "00:45:30"
        rendered = bar._build_center_section()
        assert "00:45:30" in rendered

    def test_br_tui_007_r03_no_timer_returns_empty(self) -> None:
        """Sem timer, seção central vazia."""
        bar = StatusBar()
        bar.timer_habit = ""
        bar.timer_elapsed = ""
        rendered = bar._build_center_section()
        assert rendered == ""

    def test_br_tui_007_r03_timer_default_is_empty(self) -> None:
        """Timer padrão é vazio."""
        bar = StatusBar()
        assert bar.timer_habit == ""
        assert bar.timer_elapsed == ""


# ============================================================
# BR-TUI-007 R04: Seção direita - hora atual
# ============================================================


class TestBRTUI007R04CurrentTime:
    """BR-TUI-007 R04: Exibe hora atual HH:MM."""

    def test_br_tui_007_r04_shows_formatted_time(self) -> None:
        """Exibe hora no formato HH:MM."""
        bar = StatusBar()
        with patch("timeblock.tui.widgets.status_bar.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 11, 14, 14, 30, 0)
            rendered = bar._build_right_section()
        assert "14:30" in rendered

    def test_br_tui_007_r04_time_with_leading_zero(self) -> None:
        """Hora com zero à esquerda."""
        bar = StatusBar()
        with patch("timeblock.tui.widgets.status_bar.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 11, 14, 8, 5, 0)
            rendered = bar._build_right_section()
        assert "08:05" in rendered


# ============================================================
# BR-TUI-007 R05/R06: Intervalos de atualização
# ============================================================


class TestBRTUI007R05R06UpdateIntervals:
    """BR-TUI-007 R05/R06: Clock 60s, timer 1s."""

    def test_br_tui_007_r05_clock_interval_60s(self) -> None:
        """Clock usa intervalo de 60 segundos."""
        assert StatusBar.CLOCK_INTERVAL == 60

    def test_br_tui_007_r06_timer_interval_1s(self) -> None:
        """Timer usa intervalo de 1 segundo."""
        assert StatusBar.TIMER_INTERVAL == 1
