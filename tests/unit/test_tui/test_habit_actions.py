"""Testes para BR-TUI-010: Habit Instance Actions.

Valida HabitsScreen com ações done/skip e display de status.
"""

from datetime import date

from timeblock.models.enums import (
    DoneSubstatus,
    SkipReason,
)
from timeblock.tui.screens.habits import HabitsScreen

# ============================================================
# BR-TUI-010 R01: Lista instâncias do dia
# ============================================================


class TestBRTUI010R01ListInstances:
    """BR-TUI-010 R01: Lista instâncias do dia agrupadas por hábito."""

    def test_br_tui_010_r01_default_date_is_today(self) -> None:
        """Data padrão é hoje."""
        screen = HabitsScreen()
        assert screen.current_date == date.today()

    def test_br_tui_010_r01_instances_default_empty(self) -> None:
        """Lista de instâncias inicia vazia."""
        screen = HabitsScreen()
        assert screen.instances == []

    def test_br_tui_010_r01_group_by_habit(self) -> None:
        """Instâncias agrupadas por nome do hábito."""
        screen = HabitsScreen()
        screen.instances = [
            {"habit_name": "Academia", "time": "07:00", "status": "pending"},
            {"habit_name": "Academia", "time": "07:00", "status": "pending"},
            {"habit_name": "Leitura", "time": "21:00", "status": "pending"},
        ]
        groups = screen._group_by_habit()
        assert "Academia" in groups
        assert "Leitura" in groups
        assert len(groups["Academia"]) == 2
        assert len(groups["Leitura"]) == 1

    def test_br_tui_010_r01_display_shows_time_and_status(self) -> None:
        """Display mostra horário e status de cada instância."""
        screen = HabitsScreen()
        screen.instances = [
            {"habit_name": "Academia", "time": "07:00", "status": "pending"},
        ]
        display = screen._build_instance_line(screen.instances[0])
        assert "07:00" in display
        assert "Academia" in display


# ============================================================
# BR-TUI-010 R02: Menu de ação
# ============================================================


class TestBRTUI010R02ActionMenu:
    """BR-TUI-010 R02: Menu done/skip em instância pendente."""

    def test_br_tui_010_r02_default_action_mode_none(self) -> None:
        """Sem menu de ação por padrão."""
        screen = HabitsScreen()
        assert screen.action_mode is None

    def test_br_tui_010_r02_open_action_menu_on_pending(self) -> None:
        """Abre menu em instância pendente."""
        screen = HabitsScreen()
        screen.instances = [
            {"habit_name": "Academia", "time": "07:00", "status": "pending", "id": 1},
        ]
        screen.selected_index = 0
        screen._open_action_menu()
        assert screen.action_mode == "action_select"

    def test_br_tui_010_r02_no_menu_on_completed(self) -> None:
        """Não abre menu em instância concluída."""
        screen = HabitsScreen()
        screen.instances = [
            {"habit_name": "Academia", "time": "07:00", "status": "done", "id": 1},
        ]
        screen.selected_index = 0
        screen._open_action_menu()
        assert screen.action_mode is None

    def test_br_tui_010_r02_no_menu_on_not_done(self) -> None:
        """Não abre menu em instância NOT_DONE."""
        screen = HabitsScreen()
        screen.instances = [
            {"habit_name": "Academia", "time": "07:00", "status": "not_done", "id": 1},
        ]
        screen.selected_index = 0
        screen._open_action_menu()
        assert screen.action_mode is None

    def test_br_tui_010_r02_build_action_menu(self) -> None:
        """Menu contém opções Done e Skip."""
        screen = HabitsScreen()
        menu = screen._build_action_menu()
        assert "Done" in menu or "done" in menu.lower()
        assert "Skip" in menu or "skip" in menu.lower()


# ============================================================
# BR-TUI-010 R03: Done solicita duração
# ============================================================


class TestBRTUI010R03MarkDone:
    """BR-TUI-010 R03: Done solicita duração e calcula substatus."""

    def test_br_tui_010_r03_select_done_enters_duration_mode(self) -> None:
        """Selecionar Done entra em modo de input de duração."""
        screen = HabitsScreen()
        screen.action_mode = "action_select"
        screen._select_done()
        assert screen.action_mode == "duration_input"

    def test_br_tui_010_r03_calculate_substatus_full(self) -> None:
        """90-110% → FULL."""
        screen = HabitsScreen()
        result = screen._calculate_substatus(actual_minutes=90, expected_minutes=90)
        assert result == DoneSubstatus.FULL

    def test_br_tui_010_r03_calculate_substatus_partial(self) -> None:
        """< 90% → PARTIAL."""
        screen = HabitsScreen()
        result = screen._calculate_substatus(actual_minutes=45, expected_minutes=90)
        assert result == DoneSubstatus.PARTIAL

    def test_br_tui_010_r03_calculate_substatus_overdone(self) -> None:
        """110-150% → OVERDONE."""
        screen = HabitsScreen()
        result = screen._calculate_substatus(actual_minutes=120, expected_minutes=90)
        assert result == DoneSubstatus.OVERDONE

    def test_br_tui_010_r03_calculate_substatus_excessive(self) -> None:
        """> 150% → EXCESSIVE."""
        screen = HabitsScreen()
        result = screen._calculate_substatus(actual_minutes=180, expected_minutes=90)
        assert result == DoneSubstatus.EXCESSIVE

    def test_br_tui_010_r03_calculate_substatus_zero_expected(self) -> None:
        """Expected 0 → FULL (evita divisão por zero)."""
        screen = HabitsScreen()
        result = screen._calculate_substatus(actual_minutes=30, expected_minutes=0)
        assert result == DoneSubstatus.FULL


# ============================================================
# BR-TUI-010 R04: Skip solicita categoria
# ============================================================


class TestBRTUI010R04MarkSkip:
    """BR-TUI-010 R04: Skip solicita razão e nota opcional."""

    def test_br_tui_010_r04_select_skip_enters_reason_mode(self) -> None:
        """Selecionar Skip entra em modo de seleção de razão."""
        screen = HabitsScreen()
        screen.action_mode = "action_select"
        screen._select_skip()
        assert screen.action_mode == "skip_reason"

    def test_br_tui_010_r04_skip_reasons_list(self) -> None:
        """Lista todas as SkipReason disponíveis."""
        screen = HabitsScreen()
        reasons = screen._get_skip_reasons()
        assert len(reasons) == len(SkipReason)
        for reason in SkipReason:
            assert reason in reasons

    def test_br_tui_010_r04_skip_reason_display(self) -> None:
        """SkipReasons exibidas com labels legíveis."""
        screen = HabitsScreen()
        display = screen._build_skip_reason_menu()
        # Deve conter labels das razões
        assert "saude" in display.lower() or "health" in display.lower()
        assert "trabalho" in display.lower() or "work" in display.lower()

    def test_br_tui_010_r04_after_reason_enters_note_mode(self) -> None:
        """Após selecionar razão, entra em modo nota opcional."""
        screen = HabitsScreen()
        screen.action_mode = "skip_reason"
        screen._select_skip_reason(SkipReason.HEALTH)
        assert screen.action_mode == "skip_note"
        assert screen.selected_skip_reason == SkipReason.HEALTH


# ============================================================
# BR-TUI-010 R05: Status com cor
# ============================================================


class TestBRTUI010R05StatusColors:
    """BR-TUI-010 R05: Instâncias com indicador visual por status."""

    def test_br_tui_010_r05_pending_indicator(self) -> None:
        """Pending usa indicador neutro."""
        screen = HabitsScreen()
        indicator = screen._get_status_indicator("pending")
        assert "·" in indicator or "pending" in indicator.lower()

    def test_br_tui_010_r05_done_indicator(self) -> None:
        """Done usa checkmark verde."""
        screen = HabitsScreen()
        indicator = screen._get_status_indicator("done")
        assert "✓" in indicator

    def test_br_tui_010_r05_not_done_indicator(self) -> None:
        """Not done usa cross mark."""
        screen = HabitsScreen()
        indicator = screen._get_status_indicator("not_done")
        assert "✗" in indicator

    def test_br_tui_010_r05_done_has_success_color(self) -> None:
        """Done usa cor de sucesso no markup."""
        screen = HabitsScreen()
        indicator = screen._get_status_indicator("done")
        assert "green" in indicator.lower() or "A6E3A1" in indicator

    def test_br_tui_010_r05_not_done_has_warning_color(self) -> None:
        """Not done usa cor de warning no markup."""
        screen = HabitsScreen()
        indicator = screen._get_status_indicator("not_done")
        assert "yellow" in indicator.lower() or "F9E2AF" in indicator

    def test_br_tui_010_r05_pending_has_muted_color(self) -> None:
        """Pending usa cor muted no markup."""
        screen = HabitsScreen()
        indicator = screen._get_status_indicator("pending")
        assert "dim" in indicator.lower() or "6C7086" in indicator
