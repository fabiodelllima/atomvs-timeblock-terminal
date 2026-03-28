"""Snapshot tests complementares — gaps identificados na Sessão 14.

Cobre estados visuais que não tinham snapshots:
- Routine select modal (S-01)
- Timer paused state (S-02)
- Help overlay (S-03)
- Dashboard após routine delete (S-04)
- Task completed (S-05)
- Task cancelled (S-06)
- Habit undo → pending (S-07)
- Múltiplos hábitos ordenados (S-08)
- Placeholder empty state (S-09)

Referências:
    - ADR-034: Dashboard-first CRUD
    - ADR-037: Padrão de keybindings da TUI
    - Sprint 5.5 Fase 5
"""

from datetime import date, datetime, time, timedelta
from pathlib import Path

import pytest
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.database.engine import create_db_and_tables
from timeblock.models import Habit, HabitInstance, Recurrence, Routine, Task
from timeblock.models.enums import (
    Status,
    TimerStatus,
)
from timeblock.models.time_log import TimeLog
from timeblock.tui.app import TimeBlockApp
from timeblock.tui.widgets.habits_panel import HabitsPanel


@pytest.fixture(autouse=True)
def _isolated_snapshot_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Banco temporário isolado para snapshots."""
    db_path = tmp_path / "snapshot_coverage.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    create_db_and_tables()


def _make_app() -> TimeBlockApp:
    return TimeBlockApp()


async def _wait(pilot, n: int = 3) -> None:
    for _ in range(n):
        await pilot.pause()


# =========================================================================
# Seeds
# =========================================================================


def _seed_two_routines() -> None:
    """Cria 2 rotinas (segunda ativa)."""
    with get_engine_context() as engine, Session(engine) as session:
        r1 = Routine(name="Rotina Manhã", is_active=False)
        r2 = Routine(name="Rotina Noite", is_active=True)
        session.add_all([r1, r2])
        session.commit()


def _seed_routine_only() -> None:
    """Cria 1 rotina ativa sem hábitos (para placeholder test)."""
    with get_engine_context() as engine, Session(engine) as session:
        r = Routine(name="Rotina Vazia", is_active=True)
        session.add(r)
        session.commit()


def _seed_routine_and_habit() -> None:
    """Cria rotina + hábito + instância pending."""
    with get_engine_context() as engine, Session(engine) as session:
        routine = Routine(name="Rotina Matinal", is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Leitura",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()


def _seed_multiple_habits_sorted() -> None:
    """Cria rotina com 3 hábitos em horários distintos para testar ordenação."""
    with get_engine_context() as engine, Session(engine) as session:
        routine = Routine(name="Rotina Completa", is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habits_data = [
            ("Meditação", time(6, 0), time(6, 30)),
            ("Exercício", time(7, 0), time(8, 0)),
            ("Leitura", time(9, 0), time(10, 0)),
        ]

        for title, start, end in habits_data:
            habit = Habit(
                routine_id=routine.id,
                title=title,
                scheduled_start=start,
                scheduled_end=end,
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)

            instance = HabitInstance(
                habit_id=habit.id,
                date=date.today(),
                scheduled_start=start,
                scheduled_end=end,
                status=Status.PENDING,
            )
            session.add(instance)
            session.commit()


def _seed_timer_paused() -> None:
    """Cria rotina + hábito + timer pausado."""
    with get_engine_context() as engine, Session(engine) as session:
        routine = Routine(name="Rotina Timer", is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Estudo Focado",
            scheduled_start=time(10, 0),
            scheduled_end=time(11, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(10, 0),
            scheduled_end=time(11, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer = TimeLog(
            habit_instance_id=instance.id,
            start_time=datetime.now() - timedelta(minutes=15),
            status=TimerStatus.PAUSED,
            pause_start=datetime.now() - timedelta(minutes=5),
            paused_duration=0,
        )
        session.add(timer)
        session.commit()


def _seed_task_completed() -> None:
    """Cria task completada."""
    with get_engine_context() as engine, Session(engine) as session:
        task = Task(
            title="Relatório Entregue",
            scheduled_datetime=datetime.combine(date.today(), time(14, 0)),
            original_scheduled_datetime=datetime.combine(date.today(), time(14, 0)),
            completed_at=datetime.now(),
        )
        session.add(task)
        session.commit()


def _seed_task_cancelled() -> None:
    """Cria task cancelada."""
    with get_engine_context() as engine, Session(engine) as session:
        task = Task(
            title="Reunião Cancelada",
            scheduled_datetime=datetime.combine(date.today(), time(16, 0)),
            original_scheduled_datetime=datetime.combine(date.today(), time(16, 0)),
            cancelled_at=datetime.now(),
        )
        session.add(task)
        session.commit()


# =========================================================================
# S-01: Routine Select Modal
# =========================================================================


class TestSnapshotRoutineSelect:
    """Snapshot do modal de seleção de rotinas."""

    def test_snapshot_routine_select_modal(self, snap_compare) -> None:
        """r com 2 rotinas abre FormModal com Select (DT-047)."""
        _seed_two_routines()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            await pilot.press("r")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# S-02: Timer Paused State
# =========================================================================


class TestSnapshotTimerPaused:
    """Snapshot do dashboard com timer pausado."""

    def test_snapshot_dashboard_timer_paused(self, snap_compare) -> None:
        """TimerPanel mostra estado paused (pause_start set)."""
        _seed_timer_paused()

        async def run_before(pilot) -> None:
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# S-03: Help Overlay
# =========================================================================


class TestSnapshotHelpOverlay:
    """Snapshot do help overlay aberto."""

    def test_snapshot_help_overlay(self, snap_compare) -> None:
        """? abre overlay com lista de keybindings (ADR-037)."""

        async def run_before(pilot) -> None:
            await _wait(pilot)
            await pilot.press("?")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# S-04: Dashboard After Routine Delete
# =========================================================================


class TestSnapshotAfterRoutineDelete:
    """Snapshot do dashboard sem rotina ativa."""

    def test_snapshot_dashboard_no_routine(self, snap_compare) -> None:
        """Dashboard sem rotina ativa — empty state em todos os panels."""

        async def run_before(pilot) -> None:
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# S-05: Task Completed State
# =========================================================================


class TestSnapshotTaskCompleted:
    """Snapshot do dashboard com task completada."""

    def test_snapshot_dashboard_task_completed(self, snap_compare) -> None:
        """TasksPanel mostra task com status completed."""
        _seed_task_completed()

        async def run_before(pilot) -> None:
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# S-06: Task Cancelled State
# =========================================================================


class TestSnapshotTaskCancelled:
    """Snapshot do dashboard com task cancelada."""

    def test_snapshot_dashboard_task_cancelled(self, snap_compare) -> None:
        """TasksPanel mostra task com status cancelled."""
        _seed_task_cancelled()

        async def run_before(pilot) -> None:
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# S-07: Habit Undo → Pending State
# =========================================================================


class TestSnapshotHabitUndo:
    """Snapshot do dashboard após undo (hábito volta a pending)."""

    def test_snapshot_dashboard_habit_after_undo(self, snap_compare) -> None:
        """done → undo → hábito aparece pending (BR-HABITINSTANCE-007)."""
        _seed_routine_and_habit()

        async def run_before(pilot) -> None:
            await _wait(pilot)
            # Focar habits, marcar done
            panel = pilot.app.query_one(HabitsPanel)
            pilot.app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("v")
            await _wait(pilot)
            # Confirmar done (select modal — enter direto)
            await pilot.press("enter")
            await _wait(pilot)
            # Undo
            await pilot.press("u")
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# S-08: Multiple Habits Sorted by Time
# =========================================================================


class TestSnapshotMultipleHabitsSorted:
    """Snapshot com múltiplos hábitos ordenados por horário (DT-068)."""

    def test_snapshot_dashboard_habits_sorted(self, snap_compare) -> None:
        """3 hábitos aparecem em ordem: 06:00, 07:00, 09:00."""
        _seed_multiple_habits_sorted()

        async def run_before(pilot) -> None:
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )


# =========================================================================
# S-09: Placeholder Empty State (rotina ativa, sem hábitos)
# =========================================================================


class TestSnapshotPlaceholder:
    """Snapshot do dashboard com rotina ativa mas sem hábitos."""

    def test_snapshot_dashboard_empty_habits_placeholder(self, snap_compare) -> None:
        """HabitsPanel mostra placeholders quando rotina existe mas sem hábitos."""
        _seed_routine_only()

        async def run_before(pilot) -> None:
            await _wait(pilot, 5)

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
            run_before=run_before,
        )
