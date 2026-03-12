"""Tests for BR-TUI-011: Routines Screen.

Testes para a tela de Rotinas da TUI. Grade semanal com hábitos
posicionados por recorrência, painel de detalhes e CRUD contextual.

RED phase: todos devem FALHAR até implementação.
"""

import pytest

from timeblock.tui.screens.routines import (
    RoutineBlock,
    RoutinesScreen,
    calculate_visible_days,
    detect_conflicts,
)
from timeblock.tui.widgets.timeblock_grid import calculate_block_height

# =============================================================================
# BR-TUI-011-R01: Header com lista de rotinas
# =============================================================================


@pytest.mark.asyncio
class TestBRTUI011R01HeaderBar:
    """BR-TUI-011-R01: Header exibe rotinas com indicador de ativa."""

    async def test_br_tui_011_r01_header_shows_routine_names(self):
        """Header exibe nomes das rotinas disponíveis."""
        screen = RoutinesScreen(
            routines=[
                {"id": 1, "name": "Rotina Matinal", "is_active": True},
                {"id": 2, "name": "Rotina Trabalho", "is_active": False},
            ]
        )
        header_text = screen.get_header_text()
        assert "Rotina Matinal" in header_text
        assert "Rotina Trabalho" in header_text

    async def test_br_tui_011_r01_active_routine_indicator(self):
        """Rotina ativa exibe indicador visual."""
        screen = RoutinesScreen(
            routines=[
                {"id": 1, "name": "Rotina Matinal", "is_active": True},
            ]
        )
        header_text = screen.get_header_text()
        assert "\u25b8" in header_text or ">" in header_text

    async def test_br_tui_011_r01_header_shows_habit_count(self):
        """Header exibe contador de hábitos por rotina."""
        screen = RoutinesScreen(
            routines=[
                {"id": 1, "name": "Rotina Matinal", "is_active": True, "habit_count": 5},
            ]
        )
        header_text = screen.get_header_text()
        assert "5" in header_text


# =============================================================================
# BR-TUI-011-R02: Grade semanal 7 colunas
# =============================================================================


@pytest.mark.asyncio
class TestBRTUI011R02WeeklyGrid:
    """BR-TUI-011-R02: Grade semanal com 7 colunas e régua de horas."""

    async def test_br_tui_011_r02_seven_day_columns(self):
        """Grade possui 7 colunas (Seg-Dom)."""
        screen = RoutinesScreen()
        columns = screen.get_day_columns()
        assert len(columns) == 7

    async def test_br_tui_011_r02_day_labels(self):
        """Colunas possuem labels de Seg a Dom."""
        screen = RoutinesScreen()
        labels = screen.get_day_labels()
        assert labels[0] == "Seg"
        assert labels[6] == "Dom"

    async def test_br_tui_011_r02_time_ruler(self):
        """Régua vertical exibe horários de 06:00 a 22:00."""
        screen = RoutinesScreen()
        ruler = screen.get_time_ruler()
        assert ruler[0] == "06:00"
        assert ruler[-1] == "22:00"

    async def test_br_tui_011_r02_week_period_display(self):
        """Header exibe período da semana (ex: '17-23 Fev 2026')."""
        screen = RoutinesScreen()
        period = screen.get_week_period()
        assert len(period) > 0


# =============================================================================
# BR-TUI-011-R03: Blocos proporcionais
# =============================================================================


class TestBRTUI011R03BlockRendering:
    """BR-TUI-011-R03: Blocos proporcionais na grade (1h = 2 linhas)."""

    def test_br_tui_011_r03_one_hour_block(self):
        """Hábito de 1h ocupa 2 linhas."""
        assert calculate_block_height(60) == 2

    def test_br_tui_011_r03_thirty_min_block(self):
        """Hábito de 30min ocupa 1 linha."""
        assert calculate_block_height(30) == 1

    def test_br_tui_011_r03_ninety_min_block(self):
        """Hábito de 1h30 ocupa 3 linhas."""
        assert calculate_block_height(90) == 3

    def test_br_tui_011_r03_fifteen_min_minimum(self):
        """Hábito menor que 30min ocupa mínimo 1 linha."""
        assert calculate_block_height(15) == 1

    def test_br_tui_011_r03_block_has_habit_color(self):
        """Bloco exibe cor do hábito como preenchimento."""
        block = RoutineBlock(
            habit_name="Academia",
            start="07:00",
            end="08:00",
            color="#CBA6F7",
        )
        assert block.color == "#CBA6F7"

    def test_br_tui_011_r03_block_shows_title(self):
        """Bloco exibe título do hábito."""
        block = RoutineBlock(
            habit_name="Academia",
            start="07:00",
            end="08:00",
        )
        assert block.habit_name == "Academia"


# =============================================================================
# BR-TUI-011-R04: Navegação na grade
# =============================================================================


@pytest.mark.asyncio
class TestBRTUI011R04GridNavigation:
    """BR-TUI-011-R04: Navegação por setas, colchetes e atalhos."""

    async def test_br_tui_011_r04_arrow_right_moves_day(self):
        """Seta direita move foco para próximo dia."""
        from timeblock.tui.app import TimeBlockApp

        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("2")
            routines = pilot.app.query_one("#routines-view")
            initial_day = routines.focused_day
            await pilot.press("right")
            assert routines.focused_day == initial_day + 1

    async def test_br_tui_011_r04_arrow_left_moves_day(self):
        """Seta esquerda move foco para dia anterior."""
        from timeblock.tui.app import TimeBlockApp

        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("2")
            routines = pilot.app.query_one("#routines-view")
            await pilot.press("right")
            await pilot.press("left")
            assert routines.focused_day == 0

    async def test_br_tui_011_r04_bracket_right_next_week(self):
        """']' avança uma semana."""
        from timeblock.tui.app import TimeBlockApp

        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("2")
            routines = pilot.app.query_one("#routines-view")
            initial_week = routines.current_week_offset
            await pilot.press("]")
            assert routines.current_week_offset == initial_week + 1

    async def test_br_tui_011_r04_bracket_left_prev_week(self):
        """'[' retrocede uma semana."""
        from timeblock.tui.app import TimeBlockApp

        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("2")
            routines = pilot.app.query_one("#routines-view")
            await pilot.press("]")
            await pilot.press("[")
            assert routines.current_week_offset == 0

    async def test_br_tui_011_r04_t_goes_to_today(self):
        """'T' retorna para a semana corrente."""
        from timeblock.tui.app import TimeBlockApp

        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("2")
            routines = pilot.app.query_one("#routines-view")
            await pilot.press("]")
            await pilot.press("]")
            await pilot.press("shift+t")
            assert routines.current_week_offset == 0


# =============================================================================
# BR-TUI-011-R05: Painel de detalhes
# =============================================================================


@pytest.mark.asyncio
class TestBRTUI011R05DetailPanel:
    """BR-TUI-011-R05: Painel lateral com informações do hábito selecionado."""

    async def test_br_tui_011_r05_panel_shows_habit_name(self):
        """Painel exibe nome do hábito selecionado."""
        screen = RoutinesScreen()
        screen.select_habit(habit_id=1, name="Academia")
        panel = screen.get_detail_panel()
        assert panel["name"] == "Academia"

    async def test_br_tui_011_r05_panel_shows_schedule(self):
        """Painel exibe horário e duração."""
        screen = RoutinesScreen()
        screen.select_habit(
            habit_id=1,
            name="Academia",
            start="07:00",
            end="08:00",
        )
        panel = screen.get_detail_panel()
        assert panel["start"] == "07:00"
        assert panel["end"] == "08:00"
        assert panel["duration"] == "60min"

    async def test_br_tui_011_r05_panel_updates_on_navigation(self):
        """Painel atualiza quando cursor move para outro bloco."""
        screen = RoutinesScreen()
        screen.select_habit(habit_id=1, name="Academia")
        assert screen.get_detail_panel()["name"] == "Academia"

        screen.select_habit(habit_id=2, name="Meditação")
        assert screen.get_detail_panel()["name"] == "Meditação"


# =============================================================================
# BR-TUI-011-R08: Conflitos lado a lado
# =============================================================================


class TestBRTUI011R08ConflictDisplay:
    """BR-TUI-011-R08: Hábitos conflitantes exibidos lado a lado."""

    def test_br_tui_011_r08_overlapping_detected(self):
        """Hábitos sobrepostos são detectados como conflito."""
        habits = [
            {"id": 1, "start": "07:00", "end": "08:00"},
            {"id": 2, "start": "07:30", "end": "08:30"},
        ]
        conflicts = detect_conflicts(habits)
        assert len(conflicts) > 0
        assert {1, 2} in [set(c) for c in conflicts]

    def test_br_tui_011_r08_no_conflict_for_adjacent(self):
        """Hábitos adjacentes (sem sobreposição) não são conflito."""
        habits = [
            {"id": 1, "start": "07:00", "end": "08:00"},
            {"id": 2, "start": "08:00", "end": "09:00"},
        ]
        conflicts = detect_conflicts(habits)
        assert len(conflicts) == 0

    def test_br_tui_011_r08_conflicts_never_blocked(self):
        """Conflitos são exibidos, nunca bloqueados (BR-REORDER-001)."""
        habits = [
            {"id": 1, "start": "07:00", "end": "08:00"},
            {"id": 2, "start": "07:00", "end": "08:00"},
            {"id": 3, "start": "07:30", "end": "08:30"},
        ]
        detect_conflicts(habits)
        assert len(habits) == 3


# =============================================================================
# BR-TUI-011-R09: Rotina vazia
# =============================================================================


@pytest.mark.asyncio
class TestBRTUI011R09EmptyRoutine:
    """BR-TUI-011-R09: Rotina sem hábitos exibe mensagem orientativa."""

    async def test_br_tui_011_r09_empty_message(self):
        """Rotina vazia exibe mensagem com instrução de criar hábito."""
        screen = RoutinesScreen(habits=[])
        message = screen.get_empty_message()
        assert "n" in message.lower() or "pressione" in message.lower()

    async def test_br_tui_011_r09_no_grid_when_empty(self):
        """Grade não renderiza blocos quando rotina está vazia."""
        screen = RoutinesScreen(habits=[])
        blocks = screen.get_rendered_blocks()
        assert len(blocks) == 0


# =============================================================================
# BR-TUI-011-R10: Responsividade
# =============================================================================


class TestBRTUI011R10Responsiveness:
    """BR-TUI-011-R10: Layout adapta a largura do terminal."""

    def test_br_tui_011_r10_wide_shows_seven_days(self):
        """Terminal >= 120 cols exibe 7 dias completos."""
        assert calculate_visible_days(120) == 7
        assert calculate_visible_days(160) == 7

    def test_br_tui_011_r10_medium_shows_five_days(self):
        """Terminal 80-119 cols exibe 5 dias com scroll."""
        assert calculate_visible_days(80) == 5
        assert calculate_visible_days(119) == 5

    def test_br_tui_011_r10_narrow_shows_three_days(self):
        """Terminal < 80 cols exibe 3 dias com overlay panel."""
        assert calculate_visible_days(79) == 3
        assert calculate_visible_days(60) == 3


# =============================================================================
# BR-TUI-011-R11: Refresh
# =============================================================================


@pytest.mark.asyncio
class TestBRTUI011R11Refresh:
    """BR-TUI-011-R11: Grade recarrega ao entrar na tela e após CRUD."""

    async def test_br_tui_011_r11_refresh_on_focus(self):
        """Dados recarregam quando tela recebe foco."""
        screen = RoutinesScreen()
        screen._data_loaded = False
        screen.on_focus()
        assert screen._data_loaded is True
