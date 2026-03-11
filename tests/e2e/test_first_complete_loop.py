"""E2E test — First Complete Loop (Sprint 4.5).

Valida o fluxo completo de uso do ATOMVS no dashboard:
rotina → hábito → timer start → pause → resume → stop+done.

BRs cobertas:
    - BR-TUI-016: CRUD Rotinas via dashboard
    - BR-TUI-017: CRUD Hábitos via dashboard
    - BR-TUI-021: Timer no dashboard
    - BR-TUI-004: Quick actions (Ctrl+Enter done)

Referências:
    - ADR-034: Dashboard-first CRUD
    - ADR-035: Keybindings Standardization
"""

from pathlib import Path

import pytest
from textual.widgets import Input

from timeblock.database.engine import create_db_and_tables
from timeblock.tui.app import TimeBlockApp
from timeblock.tui.screens.dashboard import loader
from timeblock.tui.screens.dashboard.screen import DashboardScreen
from timeblock.tui.widgets.agenda_panel import AgendaPanel
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.timer_panel import TimerPanel


@pytest.fixture(autouse=True)
def _isolated_tui_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Banco de dados temporário isolado para E2E TUI."""
    db_path = tmp_path / "e2e_loop.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    create_db_and_tables()


async def _wait(pilot, n: int = 3) -> None:
    """Aguarda n ciclos de pause para garantir processamento."""
    for _ in range(n):
        await pilot.pause()


async def _create_routine(pilot, name: str = "E2E Rotina") -> None:
    """Helper: foca agenda, pressa n, preenche nome, confirma."""
    agenda = pilot.app.query_one(AgendaPanel)
    pilot.app.set_focus(agenda)
    await _wait(pilot)
    await pilot.press("n")
    await _wait(pilot)
    inp = pilot.app.screen.query(Input).first()
    assert inp is not None, "FormModal de rotina não abriu"
    inp.value = name
    await pilot.press("enter")
    await _wait(pilot)


async def _create_habit(
    pilot,
    title: str = "E2E Hábito",
    start: str = "10:00",
    duration: str = "60",
) -> None:
    """Helper: foca HabitsPanel, pressa n, preenche campos, confirma."""
    panel = pilot.app.query_one(HabitsPanel)
    pilot.app.set_focus(panel)
    await _wait(pilot)
    await pilot.press("n")
    await _wait(pilot)
    inputs = list(pilot.app.screen.query(Input))
    assert len(inputs) >= 3, f"FormModal deve ter 3+ campos, encontrou {len(inputs)}"
    inputs[0].value = title
    inputs[1].value = start
    inputs[2].value = duration
    await pilot.press("enter")
    await _wait(pilot)


class TestFirstCompleteLoop:
    """Sprint 4.5: Fluxo completo rotina → hábito → timer → done."""

    @pytest.mark.asyncio
    async def test_e2e_create_routine_via_dashboard(self):
        """n com foco na agenda abre FormModal e cria rotina."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot)
            dash = pilot.app.query_one(DashboardScreen)
            assert dash._active_routine_id is not None, "Rotina deve estar ativa"

    @pytest.mark.asyncio
    async def test_e2e_create_habit_via_dashboard(self):
        """Cria rotina, depois n no HabitsPanel cria hábito."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot)
            await _create_habit(pilot)
            panel = pilot.app.query_one(HabitsPanel)
            assert len(panel._instances) > 0, "HabitsPanel deve ter instância"

    @pytest.mark.asyncio
    async def test_e2e_full_loop_routine_habit_timer_done(self):
        """Fluxo completo: rotina → hábito → start → pause → resume → stop."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)

            # 1. Criar rotina e hábito
            await _create_routine(pilot, "Loop Rotina")
            await _create_habit(pilot, "Loop Hábito", "10:00", "60")

            # 2. Verificar hábito no panel
            panel_h = pilot.app.query_one(HabitsPanel)
            assert len(panel_h._instances) > 0, "Hábito deve existir"

            # 3. Shift+Enter — inicia timer
            pilot.app.set_focus(panel_h)
            await _wait(pilot)
            await pilot.press("shift+enter")
            await _wait(pilot)

            # 4. Verificar timer ativo
            timer_data = loader.load_active_timer()
            assert timer_data is not None, "Timer deve estar ativo"
            assert timer_data["status"] == "running"
            assert timer_data["name"] == "Loop Hábito"

            # 5. Shift+Enter no TimerPanel — pausa
            panel_t = pilot.app.query_one(TimerPanel)
            pilot.app.set_focus(panel_t)
            await _wait(pilot)
            await pilot.press("shift+enter")
            await _wait(pilot)

            timer_data = loader.load_active_timer()
            assert timer_data is not None
            assert timer_data["status"] == "paused"

            # 6. Shift+Enter — retoma
            await pilot.press("shift+enter")
            await _wait(pilot)

            timer_data = loader.load_active_timer()
            assert timer_data is not None
            assert timer_data["status"] == "running"

            # 7. Ctrl+Enter — stop timer
            await pilot.press("ctrl+enter")
            await _wait(pilot)

            # 8. Timer deve estar idle
            timer_data = loader.load_active_timer()
            assert timer_data is None, "Timer deve estar idle após stop"
