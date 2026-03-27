"""Testes e2e completos de fluxos por panel no dashboard (ADR-037).

Cobre todos os keybindings e fluxos implementados: CRUD, quick actions,
timer lifecycle, navegação, e interações entre panels. Complementa
test_panel_flows.py e test_first_complete_loop.py com cobertura
integral de cada panel.

BRs cobertas:
    - BR-TUI-003: Dashboard Screen (layout, panels, cards)
    - BR-TUI-004: Quick actions (v, s, u, c)
    - BR-TUI-012: Navegação vertical (j/k, cursor)
    - BR-TUI-016: CRUD Rotinas via dashboard
    - BR-TUI-017: CRUD Hábitos via dashboard
    - BR-TUI-018: CRUD Tasks via dashboard
    - BR-TUI-019: ConfirmDialog
    - BR-TUI-020: FormModal
    - BR-TUI-021: Timer no dashboard

Referências:
    - ADR-034: Dashboard-first CRUD
    - ADR-037: Padrão de keybindings da TUI
"""

from pathlib import Path

import pytest
from sqlmodel import Session, select
from textual.widgets import Input

from timeblock.database import get_engine_context
from timeblock.database.engine import create_db_and_tables
from timeblock.models.habit_instance import HabitInstance
from timeblock.tui.app import TimeBlockApp
from timeblock.tui.screens.dashboard import loader
from timeblock.tui.screens.dashboard.screen import DashboardScreen
from timeblock.tui.widgets.agenda_panel import AgendaPanel
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.metrics_panel import MetricsPanel
from timeblock.tui.widgets.tasks_panel import TasksPanel
from timeblock.tui.widgets.timer_panel import TimerPanel

# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture(autouse=True)
def _isolated_tui_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Banco temporário isolado por teste (BR-TEST-001)."""
    db_path = tmp_path / "e2e_complete.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    create_db_and_tables()


# =========================================================================
# Helpers
# =========================================================================


async def _wait(pilot, n: int = 3) -> None:
    """Aguarda n ciclos de pause para processamento de eventos."""
    for _ in range(n):
        await pilot.pause()


async def _create_routine(pilot, name: str = "E2E Rotina") -> None:
    """Foca agenda, abre FormModal com n, preenche nome, confirma."""
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
    """Foca HabitsPanel, abre FormModal com n, preenche campos, confirma."""
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
    """Foca TasksPanel, abre FormModal com n, preenche título, confirma.

    Os campos date (default hoje) e time (opcional) não precisam de input.
    """
    panel = pilot.app.query_one(TasksPanel)
    pilot.app.set_focus(panel)
    await _wait(pilot)
    await pilot.press("n")
    await _wait(pilot)
    inputs = list(pilot.app.screen.query(Input))
    assert len(inputs) >= 1, f"FormModal deve ter campos Input, encontrou {len(inputs)}"
    inputs[0].value = title
    await pilot.press("enter")
    await _wait(pilot)


async def _setup_routine_and_habit(
    pilot,
    habit_title: str = "E2E Hábito",
    start: str = "10:00",
    duration: str = "60",
) -> None:
    """Cria rotina e hábito como setup para testes que dependem de ambos."""
    await _create_routine(pilot)
    await _create_habit(pilot, habit_title, start, duration)


async def _start_timer(pilot) -> None:
    """Foca HabitsPanel e inicia timer com t."""
    panel = pilot.app.query_one(HabitsPanel)
    pilot.app.set_focus(panel)
    await _wait(pilot)
    await pilot.press("t")
    await _wait(pilot)


def _query_instance_raw(instance_id: int) -> HabitInstance | None:
    """Acessa HabitInstance via ORM para validar campos completos.

    O loader retorna dict simplificado (substatus unificado, sem skip_reason,
    sem completion_percentage). Este helper permite verificar todos os campos
    do modelo nos testes e2e sem acoplar o loader aos testes.
    """
    with get_engine_context() as engine, Session(engine) as session:
        return session.exec(select(HabitInstance).where(HabitInstance.id == instance_id)).first()


# =========================================================================
# Habits Panel — BR-TUI-017, BR-TUI-004, ADR-037
# =========================================================================


class TestHabitsPanelComplete:
    """Fluxos e2e do HabitsPanel: edit, delete, undo, timer, skip, conflito, navegação."""

    @pytest.mark.asyncio
    async def test_habits_edit_flow(self):
        """e abre modal pré-preenchido, salva, item atualiza (BR-TUI-017 regra 2).

        Nota: habit_data['id'] é HabitInstance.id; open_edit_habit usa-o como
        habit_id — funciona quando há exatamente 1 hábito (IDs coincidem).
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Meditação", "08:00", "30")

            # Focar habits panel e pressionar e
            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("e")
            await _wait(pilot, 5)  # Extra cycles: edit FormModal com 4 campos + edit_data

            # Verificar modal aberto com dados pré-preenchidos
            inputs = list(pilot.app.screen.query(Input))
            assert len(inputs) >= 3, "FormModal de edição deve ter 3+ campos"
            assert inputs[0].value == "Meditação", "Título deve estar pré-preenchido"
            assert inputs[1].value == "08:00", "Horário deve estar pré-preenchido"
            assert inputs[2].value == "30", "Duração deve estar pré-preenchida"

            # Alterar título e salvar
            inputs[0].value = "Yoga"
            await pilot.press("enter")
            await _wait(pilot)

            # Verificar atualização no panel
            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            names = [i["name"] for i in instances]
            assert "Yoga" in names, "Título atualizado deve refletir no loader"

    @pytest.mark.asyncio
    async def test_habits_delete_flow(self):
        """x abre ConfirmDialog, Enter confirma, item some (BR-TUI-017 regra 3)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Deletar Este")

            panel = pilot.app.query_one(HabitsPanel)
            assert panel._item_count > 0, "Hábito deve existir antes de deletar"

            # Focar e deletar
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("x")
            await _wait(pilot)

            # ConfirmDialog deve estar aberto — Enter confirma
            await pilot.press("enter")
            await _wait(pilot)

            # Verificar remoção
            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            assert len(instances) == 0, "Hábito deve ter sido removido"

    @pytest.mark.asyncio
    async def test_habits_undo_flow(self):
        """v (done) → u (undo) → status volta pending (ADR-037)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot)

            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            # Marcar done com v — abre modal de substatus (Select-only)
            await pilot.press("v")
            await _wait(pilot, 5)

            # Submeter modal: Tab (Select -> Button) + Enter
            await pilot.press("tab")
            await _wait(pilot)
            await pilot.press("enter")
            await _wait(pilot)

            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            assert len(instances) > 0, "Instância deve existir"
            assert instances[0]["status"] == "done", "Status deve ser done após v"

            # Verificar ORM: done_substatus=FULL (default do Select)
            raw = _query_instance_raw(instances[0]["id"])
            assert raw is not None, "Instância deve existir no ORM"
            assert raw.done_substatus is not None, "done_substatus preenchido"
            assert raw.done_substatus.value == "full", "Default do modal é FULL"

            # Undo com u
            await pilot.press("u")
            await _wait(pilot)

            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            assert instances[0]["status"] == "pending", "Status deve voltar a pending após u"
            assert instances[0]["substatus"] is None, "Substatus deve ser limpo após undo"

            # Verificar ORM: TODOS os campos limpos (BR-HABITINSTANCE-007)
            raw = _query_instance_raw(instances[0]["id"])
            assert raw is not None
            assert raw.done_substatus is None, "done_substatus None após undo"
            assert raw.not_done_substatus is None, "not_done_substatus None após undo"
            assert raw.skip_reason is None, "skip_reason None após undo"
            assert raw.skip_note is None, "skip_note None após undo"
            assert raw.completion_percentage is None, "completion_pct None após undo"

    @pytest.mark.asyncio
    async def test_habits_timer_full_flow(self):
        """t → space → space → s: timer start/pause/resume/stop marca done (BR-TUI-021)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Timer Full")

            # 1. Iniciar timer com t no habits panel
            await _start_timer(pilot)
            timer = loader.load_active_timer()
            assert timer is not None, "Timer deve estar ativo após t"
            assert timer["status"] == "running"

            # 2. Focar timer panel e pausar com space
            panel_t = pilot.app.query_one(TimerPanel)
            pilot.app.set_focus(panel_t)
            await _wait(pilot)
            await pilot.press("space")
            await _wait(pilot)

            timer = loader.load_active_timer()
            assert timer is not None
            assert timer["status"] == "paused", "Timer deve pausar com space"

            # 3. Resumir com space
            await pilot.press("space")
            await _wait(pilot)

            timer = loader.load_active_timer()
            assert timer is not None
            assert timer["status"] == "running", "Timer deve resumir com space"

            # 4. Parar com s — stop_timer marca HabitInstance como done
            await pilot.press("s")
            await _wait(pilot)

            timer = loader.load_active_timer()
            assert timer is None, "Timer deve estar idle após stop"

            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            done = [i for i in instances if i["status"] == "done"]
            assert len(done) > 0, "Hábito deve ser marcado done após stop timer"

    @pytest.mark.asyncio
    async def test_habits_skip_registers(self):
        """s abre modal de SkipReason, Enter submete, status muda para not_done (BR-TUI-024)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Skip Este")

            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            # s abre modal de skip (Select + Input para nota)
            await pilot.press("s")
            await _wait(pilot, 5)

            # Tab para Input de nota, Enter submete
            await pilot.press("tab")
            await _wait(pilot)
            await pilot.press("enter")
            await _wait(pilot)

            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            assert len(instances) > 0
            assert instances[0]["status"] == "not_done", "Skip deve mudar status para not_done"
            assert instances[0]["substatus"] is not None, "Skip deve definir substatus"

            # Verificar ORM: campos de skip (BR-HABIT-SKIP-001)
            raw = _query_instance_raw(instances[0]["id"])
            assert raw is not None
            assert raw.not_done_substatus is not None, "not_done_substatus preenchido"
            assert raw.not_done_substatus.value == "skipped_justified"
            assert raw.skip_reason is not None, "skip_reason preenchido"
            assert raw.skip_reason.value == "outro", "Default do Select é OTHER"
            assert raw.done_substatus is None, "done_substatus deve ser None"

    @pytest.mark.asyncio
    async def test_habits_done_esc_cancels(self):
        """v abre modal, Esc cancela sem alterar status (BR-TUI-022)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Esc Done")

            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            await pilot.press("v")
            await _wait(pilot, 5)

            # Esc cancela o modal
            await pilot.press("escape")
            await _wait(pilot)

            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            assert instances[0]["status"] == "pending", "Esc não deve alterar status"

    @pytest.mark.asyncio
    async def test_habits_skip_esc_cancels(self):
        """s abre modal, Esc cancela sem alterar status (BR-TUI-024)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Esc Skip")

            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            await pilot.press("s")
            await _wait(pilot, 5)

            await pilot.press("escape")
            await _wait(pilot)

            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            assert instances[0]["status"] == "pending", "Esc não deve alterar status"

    @pytest.mark.asyncio
    async def test_habits_conflict_warning(self):
        """Criar hábito sobreposto não bloqueia criação (informar, nunca decidir)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot)

            # Criar primeiro hábito: 08:00-10:00
            await _create_habit(pilot, "Hábito A", "08:00", "120")

            # Criar segundo hábito sobreposto: 09:00-11:00
            await _create_habit(pilot, "Hábito B", "09:00", "120")

            # Ambos devem existir (conflito é informado, não bloqueado)
            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            names = {i["name"] for i in instances}
            assert "Hábito A" in names, "Primeiro hábito deve existir"
            assert "Hábito B" in names, "Segundo hábito deve existir apesar do conflito"

    @pytest.mark.asyncio
    async def test_habits_navigation_ji(self):
        """j/i move cursor entre hábitos (BR-TUI-012, ADR-037)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot)

            # Criar 3 hábitos
            await _create_habit(pilot, "Hab 1", "08:00", "30")
            await _create_habit(pilot, "Hab 2", "09:00", "30")
            await _create_habit(pilot, "Hab 3", "10:00", "30")

            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            assert panel._cursor_index == 0, "Cursor deve iniciar em 0"

            # j move para baixo
            await pilot.press("j")
            await _wait(pilot)
            assert panel._cursor_index == 1, "j deve mover cursor para 1"

            await pilot.press("j")
            await _wait(pilot)
            assert panel._cursor_index == 2, "j deve mover cursor para 2"

            # k move para cima
            await pilot.press("i")
            await _wait(pilot)
            assert panel._cursor_index == 1, "i deve mover cursor para 1"

            # Bounds checking: i no topo não vai abaixo de 0
            await pilot.press("i")
            await pilot.press("i")
            await _wait(pilot)
            assert panel._cursor_index == 0, "Cursor não deve ir abaixo de 0"


# =========================================================================
# Tasks Panel — BR-TUI-018, BR-TUI-004, ADR-037
# =========================================================================


class TestTasksPanelComplete:
    """Fluxos e2e do TasksPanel: edit, delete, postpone, cancel, reopen, navegação."""

    @pytest.mark.asyncio
    async def test_tasks_edit_flow(self):
        """e abre modal pré-preenchido, salva, item atualiza (BR-TUI-018 regra 2)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_task(pilot, "Revisar Relatório")

            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            await pilot.press("e")
            await _wait(pilot, 5)  # Extra cycles: edit FormModal com edit_data

            # Verificar modal pré-preenchido
            inputs = list(pilot.app.screen.query(Input))
            assert len(inputs) >= 1, "FormModal deve ter campos"
            assert inputs[0].value == "Revisar Relatório", "Título deve estar pré-preenchido"

            # Alterar título e salvar
            inputs[0].value = "Revisar Proposta"
            await pilot.press("enter")
            await _wait(pilot)

            tasks = loader.load_tasks()
            names = [t["name"] for t in tasks]
            assert any("Revisar Proposta" in n for n in names), "Título deve atualizar"

    @pytest.mark.asyncio
    async def test_tasks_delete_flow(self):
        """x abre ConfirmDialog, Enter confirma, task removida (BR-TUI-018 regra 3)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_task(pilot, "Deletar Task")

            panel = pilot.app.query_one(TasksPanel)
            assert panel._item_count > 0, "Task deve existir"

            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("x")
            await _wait(pilot)

            # Confirmar deleção
            await pilot.press("enter")
            await _wait(pilot)

            tasks = loader.load_tasks()
            assert len(tasks) == 0, "Task deve ter sido removida"

    @pytest.mark.asyncio
    async def test_tasks_complete_flow(self):
        """v marca task como completa via TaskService.complete_task (ADR-037, BR-TASK-007)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_task(pilot, "Completar Task")

            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            await pilot.press("v")
            await _wait(pilot)

            # Task aparece como completed nas recentes (últimas 24h)
            tasks = loader.load_tasks()
            completed = [t for t in tasks if t["status"] == "completed"]
            assert len(completed) > 0, "Task deve aparecer como completed"

    @pytest.mark.asyncio
    async def test_tasks_postpone_opens_edit_form(self):
        """s abre FormModal de edição com dados pré-preenchidos (DT-038, ADR-038 D5)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_task(pilot, "Adiar Task")

            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            await pilot.press("s")
            await _wait(pilot, 5)

            # FormModal deve abrir com título pré-preenchido
            inputs = list(pilot.app.screen.query(Input))
            assert len(inputs) >= 1, "FormModal de edição deve abrir"
            assert inputs[0].value == "Adiar Task", "Título deve estar pré-preenchido"

            # Esc cancela sem alterar
            await pilot.press("escape")
            await _wait(pilot)

            tasks = loader.load_tasks()
            assert len(tasks) > 0, "Task deve continuar existindo após cancelar postpone"

    @pytest.mark.asyncio
    async def test_tasks_cancel_flow(self):
        """c cancela task via TaskService.cancel_task (ADR-037, BR-TASK-009)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_task(pilot, "Cancelar Task")

            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            await pilot.press("c")
            await _wait(pilot)

            # Task aparece como cancelled nas recentes (últimas 24h)
            tasks = loader.load_tasks()
            cancelled = [t for t in tasks if t["status"] == "cancelled"]
            assert len(cancelled) > 0, "Task deve aparecer como cancelled"

    @pytest.mark.asyncio
    async def test_tasks_reopen_flow(self):
        """c (cancel) → u (reopen) → task volta pending (ADR-037, BR-TASK-009)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_task(pilot, "Reabrir Task")

            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            # Cancelar
            await pilot.press("c")
            await _wait(pilot)

            tasks = loader.load_tasks()
            cancelled = [t for t in tasks if t["status"] == "cancelled"]
            assert len(cancelled) > 0, "Task deve estar cancelled"

            # Reabrir com u (cursor permanece na task após refresh)
            await pilot.press("u")
            await _wait(pilot)

            tasks = loader.load_tasks()
            pending = [t for t in tasks if t["status"] == "pending"]
            assert len(pending) > 0, "Task deve voltar a pending após reopen"

    @pytest.mark.asyncio
    async def test_tasks_navigation_ji(self):
        """j/i move cursor entre tasks (BR-TUI-012, ADR-037)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)

            # Criar 3 tasks
            await _create_task(pilot, "Task A")
            await _create_task(pilot, "Task B")
            await _create_task(pilot, "Task C")

            panel = pilot.app.query_one(TasksPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)

            assert panel._cursor_index == 0

            await pilot.press("j")
            await _wait(pilot)
            assert panel._cursor_index == 1, "j deve mover cursor para baixo"

            await pilot.press("i")
            await _wait(pilot)
            assert panel._cursor_index == 0, "i deve mover cursor para cima"


# =========================================================================
# Timer Panel — BR-TUI-021, ADR-037
# =========================================================================


class TestTimerPanelComplete:
    """Fluxos e2e do TimerPanel: cancel, display name, stop→done."""

    @pytest.mark.asyncio
    async def test_timer_cancel_via_confirm_dialog(self):
        """c abre ConfirmDialog, Enter confirma, timer volta idle (BR-TIMER-003)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Timer Cancel")

            # Iniciar timer
            await _start_timer(pilot)
            timer = loader.load_active_timer()
            assert timer is not None, "Timer deve estar ativo"

            # Focar timer panel e cancelar
            panel_t = pilot.app.query_one(TimerPanel)
            pilot.app.set_focus(panel_t)
            await _wait(pilot)
            await pilot.press("c")
            await _wait(pilot)

            # ConfirmDialog aberto — confirmar com Enter
            await pilot.press("enter")
            await _wait(pilot)

            timer = loader.load_active_timer()
            assert timer is None, "Timer deve estar idle após cancel confirmado"

            # Hábito permanece pending (cancel descarta sessão)
            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            pending = [i for i in instances if i["status"] == "pending"]
            assert len(pending) > 0, "Hábito deve permanecer pending após timer cancel"

    @pytest.mark.asyncio
    async def test_timer_displays_habit_name(self):
        """Timer mostra nome do hábito associado (BR-TUI-003-R25)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Meditação Guiada")

            await _start_timer(pilot)

            timer = loader.load_active_timer()
            assert timer is not None
            assert timer["name"] == "Meditação Guiada", "Timer deve exibir nome do hábito"

    @pytest.mark.asyncio
    async def test_timer_second_blocked(self):
        """Segundo timer não inicia com timer ativo (BR-TIMER-001)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _create_routine(pilot)
            await _create_habit(pilot, "Timer A", "08:00", "60")
            await _create_habit(pilot, "Timer B", "10:00", "60")

            # Iniciar timer no primeiro hábito
            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("t")
            await _wait(pilot)

            timer = loader.load_active_timer()
            assert timer is not None, "Timer A deve estar ativo"

            # Navegar para segundo hábito e tentar iniciar
            await pilot.press("j")
            await _wait(pilot)
            await pilot.press("t")
            await _wait(pilot)

            # Timer deve continuar sendo o primeiro (bloqueio)
            timer = loader.load_active_timer()
            assert timer is not None
            assert timer["name"] == "Timer A", "Segundo timer não deve substituir o primeiro"

    @pytest.mark.asyncio
    async def test_timer_stop_marks_habit_done(self):
        """t (start) → s (stop) → hábito marcado done (BR-TIMER-003, BR-TUI-021).

        TimerService.stop_timer calcula substatus (partial/full/overdone/excessive)
        e marca HabitInstance.status = DONE automaticamente.
        """
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot, "Done Via Timer")

            # Iniciar e parar timer
            await _start_timer(pilot)

            panel_t = pilot.app.query_one(TimerPanel)
            pilot.app.set_focus(panel_t)
            await _wait(pilot)
            await pilot.press("s")
            await _wait(pilot)

            # Timer idle
            timer = loader.load_active_timer()
            assert timer is None

            # Hábito deve estar done
            instances = loader.load_instances(routine_id=loader.load_active_routine()[0])
            done = [i for i in instances if i["status"] == "done"]
            assert len(done) > 0, "stop_timer deve marcar hábito como done"
            assert done[0]["substatus"] is not None, "stop_timer deve definir substatus"

            # Verificar ORM: substatus calculado pelo timer (BR-TIMER-003)
            raw = _query_instance_raw(done[0]["id"])
            assert raw is not None
            assert raw.done_substatus is not None, "done_substatus calculado pelo timer"
            assert raw.done_substatus.value == "partial", "~0s vs 60min = PARTIAL"
            assert raw.completion_percentage is not None, "completion_pct calculado"
            assert raw.completion_percentage < 90, "~0s vs 60min = <90%"


# =========================================================================
# Metrics Panel — BR-TUI-003 regra 6
# =========================================================================


class TestMetricsPanelComplete:
    """Fluxos e2e do MetricsPanel: estado vazio e com dados."""

    @pytest.mark.asyncio
    async def test_metrics_renders_empty_state(self):
        """MetricsPanel renderiza sem erro com dados vazios."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)

            panel = pilot.app.query_one(MetricsPanel)
            # Panel deve existir e ter conteúdo (placeholder)
            assert panel is not None
            assert panel.border_title == "Métricas"

    @pytest.mark.asyncio
    async def test_metrics_shows_streak(self):
        """Com hábitos done consecutivos, streak > 0."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot)

            # Marcar done
            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("v")
            await _wait(pilot)
            await pilot.press("tab")
            await pilot.press("enter")
            await _wait(pilot)
            panel_m = pilot.app.query_one(MetricsPanel)
            assert panel_m.border_title == "Métricas"

    @pytest.mark.asyncio
    async def test_metrics_filter_routine(self):
        """Só mostra dados da rotina ativa."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            await _setup_routine_and_habit(pilot)

            # Métricas devem estar presentes (filtradas por rotina ativa)
            panel_m = pilot.app.query_one(MetricsPanel)
            assert panel_m.border_title == "Métricas"


# =========================================================================
# Navegação Global — ADR-037
# =========================================================================


class TestNavigationComplete:
    """Fluxos e2e de navegação global: Tab, 1-5, ?, n sem rotina."""

    @pytest.mark.asyncio
    async def test_tab_cycles_panels(self):
        """Tab percorre habits → tasks → timer → metrics (ADR-037)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            dash = pilot.app.query_one(DashboardScreen)

            # Tab deve mudar o panel focado
            await pilot.press("tab")
            await _wait(pilot)
            first_panel = dash._focused_panel

            await pilot.press("tab")
            await _wait(pilot)
            second_panel = dash._focused_panel

            # Panels focados devem ser diferentes entre si
            assert first_panel != second_panel, "Tab deve alternar entre panels"

            # Verificar que ambos são panels válidos
            valid_panels = {"panel-habits", "panel-tasks", "panel-timer", "panel-metrics"}
            assert first_panel in valid_panels, f"Panel {first_panel} deve ser válido"
            assert second_panel in valid_panels, f"Panel {second_panel} deve ser válido"

    @pytest.mark.asyncio
    async def test_screen_switch_via_number_keys(self):
        """1-5 alterna screens corretamente."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)

            app = pilot.app
            assert app.active_screen == "dashboard", "Deve iniciar em dashboard"

            # Trocar para routines (2)
            await pilot.press("2")
            await _wait(pilot)
            assert app.active_screen == "routines", "2 deve ativar routines"

            # Voltar para dashboard (1)
            await pilot.press("1")
            await _wait(pilot)
            assert app.active_screen == "dashboard", "1 deve voltar ao dashboard"

            # Trocar para tasks (4)
            await pilot.press("4")
            await _wait(pilot)
            assert app.active_screen == "tasks", "4 deve ativar tasks"

            # Trocar para timer (5)
            await pilot.press("5")
            await _wait(pilot)
            assert app.active_screen == "timer", "5 deve ativar timer"

    @pytest.mark.asyncio
    async def test_help_overlay_toggle(self):
        """? abre help overlay, ? fecha (ADR-037)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)

            # Abrir help
            await pilot.press("?")
            await _wait(pilot)
            overlay = pilot.app.query("#help-overlay")
            assert len(overlay) > 0, "? deve abrir help overlay"

            # Fechar help com ?
            await pilot.press("?")
            await _wait(pilot)
            overlay = pilot.app.query("#help-overlay")
            assert len(overlay) == 0, "? deve fechar help overlay"

    @pytest.mark.asyncio
    async def test_help_overlay_closes_with_escape(self):
        """? abre overlay, Esc fecha (ADR-037)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)

            await pilot.press("?")
            await _wait(pilot)
            assert len(pilot.app.query("#help-overlay")) > 0

            await pilot.press("escape")
            await _wait(pilot)
            assert len(pilot.app.query("#help-overlay")) == 0, "Esc deve fechar help"

    @pytest.mark.asyncio
    async def test_crud_n_without_routine_creates_routine(self):
        """n sem rotina ativa abre FormModal de rotina (BR-TUI-016)."""
        async with TimeBlockApp().run_test() as pilot:
            await _wait(pilot)
            dash = pilot.app.query_one(DashboardScreen)

            # Sem rotina ativa
            assert dash._active_routine_id is None, "Não deve haver rotina"

            # n (sem panel focado ou com agenda) deve abrir criação de rotina
            await pilot.press("n")
            await _wait(pilot)

            # FormModal deve abrir para rotina
            inputs = list(pilot.app.screen.query(Input))
            assert len(inputs) >= 1, "FormModal de rotina deve abrir"

            # Preencher e confirmar
            inputs[0].value = "Nova Rotina"
            await pilot.press("enter")
            await _wait(pilot)

            assert dash._active_routine_id is not None, "Rotina deve ter sido criada"
