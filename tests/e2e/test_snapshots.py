"""Snapshot tests para regressões visuais da TUI.

Usa pytest-textual-snapshot para capturar SVGs e comparar
com baselines aprovadas. Primeira execução gera baselines
(falha esperada). Execuções seguintes detectam regressões.

Referências:
    - docs/guides/snapshot-testing.md
    - Sprint 5.5 Fase 5
"""

from datetime import date, time
from pathlib import Path

import pytest
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.database.engine import create_db_and_tables
from timeblock.models import Habit, HabitInstance, Recurrence, Routine
from timeblock.models.enums import Status
from timeblock.tui.app import TimeBlockApp


@pytest.fixture(autouse=True)
def _isolated_snapshot_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Banco temporário isolado para snapshots."""
    db_path = tmp_path / "snapshot.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    create_db_and_tables()


def _make_app() -> TimeBlockApp:
    """Cria instância da app para snapshot."""
    return TimeBlockApp()


class TestDashboardSnapshots:
    """Snapshots do dashboard em diferentes estados."""

    def test_snapshot_dashboard_empty(self, snap_compare) -> None:
        """Dashboard sem rotina — estado inicial do first-run."""
        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
        )

    def test_snapshot_dashboard_with_routine(self, snap_compare, tmp_path, monkeypatch) -> None:
        """Dashboard com rotina ativa e hábitos."""

        with get_engine_context() as engine, Session(engine) as session:
            routine = Routine(name="Rotina Teste", is_active=True)
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

        assert snap_compare(
            _make_app(),
            terminal_size=(120, 40),
        )

    def test_snapshot_dashboard_80x24(self, snap_compare) -> None:
        """Dashboard em terminal mínimo 80x24."""
        assert snap_compare(
            _make_app(),
            terminal_size=(80, 24),
        )
