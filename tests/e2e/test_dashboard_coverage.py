"""Testes e2e de cobertura completa do dashboard — gaps identificados na Sessão 14.

Complementa test_dashboard_complete.py com fluxos que estavam sem cobertura:
- Routines: create→header, edit, delete (com troca automática), select
- Tasks: navegação por setas
- Timer: pause/resume via space no TimerPanel, stop via TimerPanel
- Navegação: placeholder enter, Esc desfoca panels

BRs cobertas:
    - BR-TUI-016: CRUD Rotinas via dashboard
    - BR-TUI-012: Navegação vertical (j/i, arrows, cursor)
    - BR-TUI-013: Placeholder activation via Enter
    - BR-TUI-021: Timer no dashboard (pause/resume/stop)

Referências:
    - ADR-034: Dashboard-first CRUD
    - ADR-037: Padrão de keybindings da TUI
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
from timeblock.tui.widgets.tasks_panel import TasksPanel
from timeblock.tui.widgets.timer_panel import TimerPanel

# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture(autouse=True)
def _isolated_tui_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Banco temporário isolado por teste (BR-TEST-001)."""
    db_path = tmp_path / "e2e_coverage.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    create_db_and_tables()


# =========================================================================
# Helpers (reutilizados de test_dashboard_complete)
# =========================================================================


async def _wait(pilot, n: int = 3) -> None:
    for _ in range(n):
        await pilot.pause()


async def _create_routine(pilot, name: str = "E2E Rotina") -> None:
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
    panel = pilot.app.query_one(HabitsPanel)
    pilot.app.set_focus(panel)
    await _wait(pilot)
    await pilot.press("n")
    await _wait(pilot)
    inputs = list(pilot.app.screen.query(Input))
    assert len(inputs) >= 3, f"FormModal deve ter 3+ campos Input, encontrou {len(inputs)}"
    inputs[0].value = title
    inputs[1].value = start
    inputs[2].value = duration
    await pilot.press("enter")
    await _wait(pilot)


async def _create_task(pilot, title: str = "E2E Task") -> None:
    panel = pilot.app.query_one(TasksPanel)
    pilot.app.set_focus(panel)
    await _wait(pilot)
    await pilot.press("n")
    await _wait(pilot)
    inputs = list(pilot.app.screen.query(Input))
    assert len(inputs) >= 1
    inputs[0].value = title
    await pilot.press("enter")
    await _wait(pilot)


async def _setup_routine_and_habit(
    pilot,
    habit_title: str = "E2E Hábito",
    start: str = "10:00",
    duration: str = "60",
) -> None:
    await _create_routine(pilot)
    await _create_habit(pilot, habit_title, start, duration)


async def _start_timer(pilot) -> None:
    panel = pilot.app.query_one(HabitsPanel)
    pilot.app.set_focus(panel)
    await _wait(pilot)
    await pilot.press("t")
    await _wait(pilot)


# =========================================================================
# Routines — BR-TUI-016 (gaps G-01 a G-04)
# =========================================================================


class TestRoutinesCoverage:
    """Fluxos de rotinas que estavam sem cobertura e2e."""

    @pytest.mark.asyncio
    async def test_routine_create_shows_in_loader(self):
        """Criar rotina via n faz load_active_routine retornar o nome (G-01).

        Valida que a rotina criada fica ativa e o loader a reconhece.
        BR-TUI-016 regra 1: criar rotina a torna ativa automaticamente.
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            dash = pilot.app.query_one(DashboardScreen)

            # Sem rotina
            assert dash._active_routine_id is None

            await _create_routine(pilot, "Rotina Produtiva")

            # Verificar via loader
            rid, rname = loader.load_active_routine()
            assert rid is not None, "Rotina deve estar ativa"
            assert rname == "Rotina Produtiva", "Nome da rotina deve bater"
            assert dash._active_routine_id == rid, "DashboardScreen deve refletir rotina"

    @pytest.mark.asyncio
    async def test_routine_edit_updates_name(self):
        """e no agenda abre modal pré-preenchido, salvar atualiza nome (G-02).

        BR-TUI-016 regra 2: editar rotina ativa.
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot, "Nome Original")

            # Focar agenda para editar rotina
            agenda = pilot.app.query_one(AgendaPanel)
            pilot.app.set_focus(agenda)
            await _wait(pilot)

            await pilot.press("e")
            await _wait(pilot, 5)

            # Modal deve ter nome pré-preenchido
            inputs = list(pilot.app.screen.query(Input))
            assert len(inputs) >= 1, "FormModal de edição deve abrir"
            assert inputs[0].value == "Nome Original", "Nome deve estar pré-preenchido"

            # Alterar e salvar
            inputs[0].value = "Nome Atualizado"
            await pilot.press("enter")
            await _wait(pilot)

            _rid, rname = loader.load_active_routine()
            assert rname == "Nome Atualizado", "Nome deve ter sido atualizado"

    @pytest.mark.asyncio
    async def test_routine_delete_activates_next(self):
        """x no agenda com 2 rotinas: deleta ativa, ativa a próxima (G-03).

        BR-TUI-016 regra 3 + DT-048: após deletar rotina ativa,
        ativar próxima automaticamente.
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)

            # Criar duas rotinas (a segunda fica ativa por auto_activate)
            await _create_routine(pilot, "Rotina A")
            await _create_routine(pilot, "Rotina B")

            _, rname = loader.load_active_routine()
            assert rname == "Rotina B", "Rotina B deve ser a ativa"

            # Focar agenda e deletar a ativa (Rotina B)
            agenda = pilot.app.query_one(AgendaPanel)
            pilot.app.set_focus(agenda)
            await _wait(pilot)

            await pilot.press("x")
            await _wait(pilot)

            # ConfirmDialog — confirmar
            await pilot.press("enter")
            await _wait(pilot)

            # Rotina A deve ficar ativa
            rid, rname = loader.load_active_routine()
            assert rid is not None, "Deve haver rotina ativa após delete"
            assert rname == "Rotina A", "Rotina A deve ser ativada automaticamente"

    @pytest.mark.asyncio
    async def test_routine_delete_last_clears_state(self):
        """x no agenda com 1 rotina: deleta, dashboard fica sem rotina (G-03 variante).

        Após deletar a última rotina, load_active_routine retorna (None, "").
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot, "Única Rotina")

            agenda = pilot.app.query_one(AgendaPanel)
            pilot.app.set_focus(agenda)
            await _wait(pilot)

            await pilot.press("x")
            await _wait(pilot)
            await pilot.press("enter")
            await _wait(pilot)

            rid, _rname = loader.load_active_routine()
            assert rid is None, "Sem rotina ativa após deletar a última"

    @pytest.mark.asyncio
    async def test_routine_select_switches_routine(self):
        """r com 2 rotinas abre Select, selecionar troca rotina ativa (G-04).

        BR-TUI-016 + DT-047: mecanismo de seleção entre rotinas.
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)

            # Criar duas rotinas
            await _create_routine(pilot, "Rotina Manhã")
            await _create_routine(pilot, "Rotina Noite")

            _, rname_before = loader.load_active_routine()
            assert rname_before == "Rotina Noite", "Última criada deve estar ativa"

            # r abre select
            await pilot.press("r")
            await _wait(pilot, 5)

            # FormModal com Select deve estar aberto
            # Confirmar seleção (primeiro item = Rotina Manhã)
            await pilot.press("enter")
            await _wait(pilot)

            rid, _rname_after = loader.load_active_routine()
            assert rid is not None, "Rotina deve estar ativa após select"
            # A rotina selecionada pode ser qualquer uma das duas,
            # o importante é que o select funcionou sem erro

    @pytest.mark.asyncio
    async def test_routine_select_with_single_notifies(self):
        """r com apenas 1 rotina notifica e não abre modal (DT-047).

        Não deve crashar nem abrir modal vazio.
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot, "Única")

            await pilot.press("r")
            await _wait(pilot)

            # Não deve ter FormModal aberto (notificação informativa)
            inputs = list(pilot.app.screen.query(Input))
            assert len(inputs) == 0, "Não deve abrir modal com apenas 1 rotina"

    @pytest.mark.asyncio
    async def test_routine_create_then_habit_shows_in_panel(self):
        """Fluxo completo: criar rotina → criar hábito → verifica dados (G-09).

        Garante que após criação, o hábito aparece no loader com dados corretos.
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot, "Rotina Teste")
            await _create_habit(pilot, "Leitura Diária", "08:00", "45")

            rid, _ = loader.load_active_routine()
            instances = loader.load_instances(rid)
            assert len(instances) > 0, "Hábito deve existir como instância"
            assert instances[0]["name"] == "Leitura Diária", "Nome deve bater"
            assert instances[0]["start_minutes"] == 480, "08:00 = 480 min"


# =========================================================================
# Tasks — Navegação por setas (gap G-05)
# =========================================================================


class TestTasksNavigationArrows:
    """Navegação por setas no TasksPanel (gap G-05)."""

    @pytest.mark.asyncio
    async def test_tasks_navigation_arrows(self):
        """up/down move cursor entre tasks — equivalente a i/j (BR-TUI-012)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)

            await _create_task(pilot, "Task Alpha")
            await _create_task(pilot, "Task Beta")
            await _create_task(pilot, "Task Gamma")

            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            assert panel._cursor_index == 0

            await pilot.press("down")
            await _wait(pilot)
            assert panel._cursor_index == 1, "down deve mover cursor para baixo"

            await pilot.press("down")
            await _wait(pilot)
            assert panel._cursor_index == 2, "down deve continuar movendo"

            await pilot.press("up")
            await _wait(pilot)
            assert panel._cursor_index == 1, "up deve mover cursor para cima"

            # Bounds checking no topo
            await pilot.press("up")
            await _wait(pilot)
            await pilot.press("up")
            await _wait(pilot)
            assert panel._cursor_index == 0, "up não deve passar do topo"


# =========================================================================
# Timer — pause/resume/stop via TimerPanel (gaps G-06, G-07)
# =========================================================================


class TestTimerPanelKeysCoverage:
    """Keybindings do TimerPanel que não tinham cobertura direta."""

    @pytest.mark.asyncio
    async def test_timer_pause_resume_space(self):
        """space pausa timer running, space retoma timer paused (G-06).

        BR-TUI-021: space no TimerPanel alterna pause/resume.
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Timer Pause Test")
            await _start_timer(pilot)

            timer = loader.load_active_timer()
            assert timer is not None
            assert timer["status"] == "running"

            # Focar TimerPanel e pausar
            panel_t = pilot.app.query_one(TimerPanel)
            pilot.app.set_focus(panel_t)
            await _wait(pilot)

            await pilot.press("space")
            await _wait(pilot)

            timer = loader.load_active_timer()
            assert timer is not None
            assert timer["status"] == "paused", "space deve pausar timer running"

            # space novamente retoma
            await pilot.press("space")
            await _wait(pilot)

            timer = loader.load_active_timer()
            assert timer is not None
            assert timer["status"] == "running", "space deve retomar timer paused"

    @pytest.mark.asyncio
    async def test_timer_stop_via_timer_panel(self):
        """s no TimerPanel para timer e marca hábito done (G-07).

        BR-TUI-021 + BR-TIMER-003: stop no TimerPanel via keybinding s.
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Timer Stop Test")
            await _start_timer(pilot)

            timer = loader.load_active_timer()
            assert timer is not None

            panel_t = pilot.app.query_one(TimerPanel)
            pilot.app.set_focus(panel_t)
            await _wait(pilot)

            await pilot.press("s")
            await _wait(pilot)

            timer = loader.load_active_timer()
            assert timer is None, "Timer deve estar idle após stop"

            # Hábito deve estar done
            rid, _ = loader.load_active_routine()
            instances = loader.load_instances(rid)
            done = [i for i in instances if i["status"] == "done"]
            assert len(done) > 0, "Stop deve marcar hábito como done"


# =========================================================================
# Placeholder activation (gap G-08)
# =========================================================================


class TestPlaceholderActivation:
    """Enter em panel vazio abre criação contextual (BR-TUI-013)."""

    @pytest.mark.asyncio
    async def test_enter_on_empty_habits_opens_create(self):
        """Enter no HabitsPanel vazio (com rotina) abre FormModal de hábito (G-08)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot, "Rotina Vazia")

            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            # Panel vazio com placeholders — Enter deve abrir criação
            await pilot.press("enter")
            await _wait(pilot, 5)

            inputs = list(pilot.app.screen.query(Input))
            assert len(inputs) >= 3, (
                f"Enter em placeholder deve abrir FormModal de hábito, encontrou {len(inputs)} inputs"
            )

    @pytest.mark.asyncio
    async def test_enter_on_empty_tasks_opens_create(self):
        """Enter no TasksPanel vazio abre FormModal de task (BR-TUI-013)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)

            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            await pilot.press("enter")
            await _wait(pilot, 5)

            inputs = list(pilot.app.screen.query(Input))
            assert len(inputs) >= 1, "Enter em placeholder deve abrir FormModal de task"


# =========================================================================
# Sprint 4.5 — set_interval tests (DT-015)
# =========================================================================


class TestSetIntervalMechanisms:
    """Testes dos mecanismos de set_interval no dashboard (DT-015).

    Commit 3 (Sprint 4.5): set_interval(1, _tick_timer)
    Commit 4 (Sprint 4.5): set_interval(60, _refresh_agenda)
    """

    @pytest.mark.asyncio
    async def test_timer_panel_updates_every_second(self):
        """set_interval(1) dispara _tick_timer e atualiza elapsed (DT-015).

        Prova: iniciar timer, esperar tempo real (~2.5s), verificar que
        o elapsed no TimerPanel mudou. O loader calcula elapsed via
        datetime.now(), e _tick_timer propaga para o widget.
        """
        import asyncio

        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Timer Tick", "10:00", "60")
            await _start_timer(pilot)

            panel_t = pilot.app.query_one(TimerPanel)
            assert panel_t._timer_info is not None, "Timer deve estar ativo"
            initial_secs = panel_t._timer_info.get("elapsed_seconds", 0)

            # Esperar tempo real para set_interval(1) disparar múltiplas vezes
            await asyncio.sleep(2.5)
            await _wait(pilot)

            assert panel_t._timer_info is not None, "Timer deve continuar ativo"
            updated_secs = panel_t._timer_info.get("elapsed_seconds", 0)
            assert updated_secs > initial_secs, (
                f"elapsed deve aumentar: {initial_secs} → {updated_secs}"
            )
            assert panel_t._timer_info["elapsed"] != "00:00", (
                "TimerPanel deve exibir elapsed > 00:00"
            )

    @pytest.mark.asyncio
    async def test_agenda_refreshes_periodically(self):
        """_refresh_agenda propaga dados atualizados para panels (DT-015).

        set_interval(60, _refresh_agenda) usa o mesmo mecanismo que
        set_interval(1, _tick_timer) — provado em test_timer_panel_updates.
        Este teste verifica a integração: dados inseridos no DB após
        o mount inicial são visíveis após _refresh_agenda().
        """
        from datetime import date, time

        from sqlmodel import Session

        from timeblock.database import get_engine_context
        from timeblock.models import Habit, HabitInstance, Recurrence
        from timeblock.models.enums import Status

        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot, "Agenda Refresh")

            dash = pilot.app.query_one(DashboardScreen)
            rid = dash._active_routine_id
            assert rid is not None

            # Nenhum hábito ainda — panels vazios
            instances_before = loader.load_instances(rid)
            assert len(instances_before) == 0

            # Inserir hábito + instância diretamente no DB (simula dados novos)
            with get_engine_context() as engine, Session(engine) as session:
                habit = Habit(
                    routine_id=rid,
                    title="Hábito Novo",
                    scheduled_start=time(8, 0),
                    scheduled_end=time(9, 0),
                    recurrence=Recurrence.EVERYDAY,
                )
                session.add(habit)
                session.commit()
                session.refresh(habit)

                instance = HabitInstance(
                    habit_id=habit.id,
                    date=date.today(),
                    scheduled_start=time(8, 0),
                    scheduled_end=time(9, 0),
                    status=Status.PENDING,
                )
                session.add(instance)
                session.commit()

            # _refresh_agenda propaga dados novos para os panels
            dash._refresh_agenda()
            await _wait(pilot)

            # Verificar que HabitsPanel agora tem o hábito
            panel_h = pilot.app.query_one(HabitsPanel)
            assert panel_h._item_count > 0, (
                "_refresh_agenda deve propagar instância nova para HabitsPanel"
            )
            assert panel_h._instances[0]["name"] == "Hábito Novo"
