"""Testes para BR-TUI-006: Timer Screen Live Display.

Valida TimerScreen com display live, keybindings e integração StatusBar.
"""

from textual.binding import Binding

from timeblock.tui.screens.timer import TimerScreen

# ============================================================
# BR-TUI-006 R01: Display atualiza a cada 1 segundo
# ============================================================


class TestBRTUI006R01LiveDisplay:
    """BR-TUI-006 R01: Timer display com atualização live."""

    def test_br_tui_006_r01_has_update_interval(self) -> None:
        """TimerScreen define intervalo de 1 segundo."""
        assert TimerScreen.TIMER_INTERVAL == 1

    def test_br_tui_006_r01_elapsed_format_zero(self) -> None:
        """Tempo zero formata como 00:00:00."""
        screen = TimerScreen()
        assert screen._format_elapsed(0) == "00:00:00"

    def test_br_tui_006_r01_elapsed_format_minutes(self) -> None:
        """45 minutos e 30 segundos formatados corretamente."""
        screen = TimerScreen()
        assert screen._format_elapsed(2730) == "00:45:30"

    def test_br_tui_006_r01_elapsed_format_hours(self) -> None:
        """1 hora 30 minutos formatados corretamente."""
        screen = TimerScreen()
        assert screen._format_elapsed(5400) == "01:30:00"

    def test_br_tui_006_r01_elapsed_format_large(self) -> None:
        """Valores grandes formatados corretamente."""
        screen = TimerScreen()
        assert screen._format_elapsed(36000) == "10:00:00"


# ============================================================
# BR-TUI-006 R02: Keybindings de timer
# ============================================================


class TestBRTUI006R02Keybindings:
    """BR-TUI-006 R02: Keybindings s/p/enter/c."""

    def _get_binding_keys(self) -> list[str]:
        """Extrai teclas dos bindings."""
        return [b.key if isinstance(b, Binding) else b[0] for b in TimerScreen.BINDINGS]

    def test_br_tui_006_r02_start_keybinding(self) -> None:
        """'s' inicia timer."""
        keys = self._get_binding_keys()
        assert "s" in keys

    def test_br_tui_006_r02_pause_resume_keybinding(self) -> None:
        """'p' pausa/resume timer."""
        keys = self._get_binding_keys()
        assert "p" in keys

    def test_br_tui_006_r02_stop_keybinding(self) -> None:
        """'enter' para timer."""
        keys = self._get_binding_keys()
        assert "enter" in keys

    def test_br_tui_006_r02_cancel_keybinding(self) -> None:
        """'c' cancela timer."""
        keys = self._get_binding_keys()
        assert "c" in keys


# ============================================================
# BR-TUI-006 R03: Display mostra informações
# ============================================================


class TestBRTUI006R03DisplayInfo:
    """BR-TUI-006 R03: Display exibe habit, status e tempo."""

    def test_br_tui_006_r03_default_state_idle(self) -> None:
        """Estado inicial é idle."""
        screen = TimerScreen()
        assert screen.timer_state == "idle"

    def test_br_tui_006_r03_default_habit_empty(self) -> None:
        """Habit padrão é vazio."""
        screen = TimerScreen()
        assert screen.current_habit == ""

    def test_br_tui_006_r03_default_elapsed_zero(self) -> None:
        """Elapsed padrão é zero."""
        screen = TimerScreen()
        assert screen.elapsed_seconds == 0

    def test_br_tui_006_r03_state_running(self) -> None:
        """Estado RUNNING após start."""
        screen = TimerScreen()
        screen.timer_state = "running"
        assert screen.timer_state == "running"

    def test_br_tui_006_r03_state_paused(self) -> None:
        """Estado PAUSED após pause."""
        screen = TimerScreen()
        screen.timer_state = "paused"
        assert screen.timer_state == "paused"

    def test_br_tui_006_r03_build_display_idle(self) -> None:
        """Display idle mostra mensagem de orientação."""
        screen = TimerScreen()
        screen.timer_state = "idle"
        display = screen._build_timer_display()
        assert "s" in display.lower() or "start" in display.lower()

    def test_br_tui_006_r03_build_display_running(self) -> None:
        """Display running mostra habit e tempo."""
        screen = TimerScreen()
        screen.timer_state = "running"
        screen.current_habit = "Academia"
        screen.elapsed_seconds = 2730
        display = screen._build_timer_display()
        assert "Academia" in display
        assert "00:45:30" in display

    def test_br_tui_006_r03_build_display_paused(self) -> None:
        """Display paused mostra indicação de pausa."""
        screen = TimerScreen()
        screen.timer_state = "paused"
        screen.current_habit = "Academia"
        screen.elapsed_seconds = 600
        display = screen._build_timer_display()
        assert "PAUSED" in display.upper() or "PAUSADO" in display.upper()


# ============================================================
# BR-TUI-006 R04: Pause congela display
# ============================================================


class TestBRTUI006R04PauseFreeze:
    """BR-TUI-006 R04: Timer pausado não incrementa elapsed."""

    def test_br_tui_006_r04_tick_increments_when_running(self) -> None:
        """Tick incrementa elapsed quando running."""
        screen = TimerScreen()
        screen.timer_state = "running"
        screen.elapsed_seconds = 100
        screen._tick()
        assert screen.elapsed_seconds == 101

    def test_br_tui_006_r04_tick_freezes_when_paused(self) -> None:
        """Tick NÃO incrementa elapsed quando paused."""
        screen = TimerScreen()
        screen.timer_state = "paused"
        screen.elapsed_seconds = 100
        screen._tick()
        assert screen.elapsed_seconds == 100

    def test_br_tui_006_r04_tick_freezes_when_idle(self) -> None:
        """Tick NÃO incrementa elapsed quando idle."""
        screen = TimerScreen()
        screen.timer_state = "idle"
        screen.elapsed_seconds = 0
        screen._tick()
        assert screen.elapsed_seconds == 0


# ============================================================
# BR-TUI-006 R05: Stop exibe resumo
# ============================================================


class TestBRTUI006R05SessionSummary:
    """BR-TUI-006 R05: Stop exibe resumo da sessão."""

    def test_br_tui_006_r05_build_summary(self) -> None:
        """Resumo contém duração total."""
        screen = TimerScreen()
        summary = screen._build_session_summary(
            habit_name="Academia",
            elapsed_seconds=5400,
            expected_minutes=90,
        )
        assert "Academia" in summary
        assert "90" in summary or "1:30" in summary or "5400" in summary

    def test_br_tui_006_r05_summary_completion_full(self) -> None:
        """Resumo exibe completion percentage - FULL."""
        screen = TimerScreen()
        summary = screen._build_session_summary(
            habit_name="Academia",
            elapsed_seconds=5400,
            expected_minutes=90,
        )
        assert "100" in summary

    def test_br_tui_006_r05_summary_completion_partial(self) -> None:
        """Resumo exibe completion percentage - PARTIAL."""
        screen = TimerScreen()
        summary = screen._build_session_summary(
            habit_name="Academia",
            elapsed_seconds=3600,
            expected_minutes=90,
        )
        assert "67" in summary or "66" in summary

    def test_br_tui_006_r05_summary_completion_excessive(self) -> None:
        """Resumo exibe completion percentage - EXCESSIVE."""
        screen = TimerScreen()
        summary = screen._build_session_summary(
            habit_name="Academia",
            elapsed_seconds=10800,
            expected_minutes=90,
        )
        assert "200" in summary


# ============================================================
# BR-TUI-006 R07: Timer visível na StatusBar
# ============================================================


class TestBRTUI006R07StatusBarIntegration:
    """BR-TUI-006 R07: Timer ativo atualiza StatusBar."""

    def test_br_tui_006_r07_status_bar_data_format(self) -> None:
        """Dados formatados para StatusBar."""
        screen = TimerScreen()
        screen.timer_state = "running"
        screen.current_habit = "Academia"
        screen.elapsed_seconds = 2730
        data = screen._get_status_bar_data()
        assert data["habit"] == "Academia"
        assert data["elapsed"] == "00:45:30"

    def test_br_tui_006_r07_status_bar_data_empty_when_idle(self) -> None:
        """Dados vazios quando idle."""
        screen = TimerScreen()
        screen.timer_state = "idle"
        data = screen._get_status_bar_data()
        assert data["habit"] == ""
        assert data["elapsed"] == ""
