"""Testes para _find_done_timelog e open_done_modal (BR-TUI-022, DT-037).

Validates:
    - BR-TUI-022: Modal de DONE com detecção de TimeLog e restauração de substatus
    - DT-037: Handler on_habits_panel_timer_stop_and_done_request
"""

from datetime import date, datetime, time

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session

from timeblock.models.enums import DoneSubstatus, TimerStatus
from timeblock.models.habit import Habit, Recurrence
from timeblock.models.habit_instance import HabitInstance
from timeblock.models.routine import Routine
from timeblock.models.time_log import TimeLog
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.tui.screens.dashboard.crud_habits import (
    DONE_SUBSTATUS_OPTIONS,
    _find_done_timelog,
)


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch: pytest.MonkeyPatch, test_engine: Engine) -> None:
    """Mock get_engine_context para usar banco de teste."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr(
        "timeblock.services.habit_instance_service.get_engine_context",
        mock_get_engine,
    )


@pytest.fixture
def everyday_habit(session: Session) -> Habit:
    """Cria rotina + hábito diário para testes."""
    routine = Routine(name="Rotina Done Modal")
    session.add(routine)
    session.commit()
    session.refresh(routine)

    habit = Habit(
        routine_id=routine.id,
        title="Hábito Done Test",
        scheduled_start=time(8, 0),
        scheduled_end=time(9, 0),
        target_minutes=60,
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@pytest.fixture
def pending_instance(everyday_habit: Habit) -> HabitInstance:
    """Gera instância PENDING para hoje."""
    assert everyday_habit.id is not None
    instances = HabitInstanceService.generate_instances(
        everyday_habit.id, date.today(), date.today()
    )
    assert len(instances) > 0
    return instances[0]


class TestBRTui022FindDoneTimelog:
    """BR-TUI-022: _find_done_timelog detecta TimeLog DONE e calcula substatus."""

    def test_br_tui_022_find_done_timelog_full(
        self, session: Session, pending_instance: HabitInstance
    ) -> None:
        """TimeLog com 95% de conclusão retorna FULL."""
        assert pending_instance.id is not None

        # Create TimeLog DONE with 3420s (95% of 3600s target)
        start_dt = datetime.combine(pending_instance.date, time(8, 0))
        end_dt = datetime.combine(pending_instance.date, time(8, 57))
        timelog = TimeLog(
            habit_instance_id=pending_instance.id,
            status=TimerStatus.DONE,
            start_time=start_dt,
            end_time=end_dt,
            duration_seconds=3420,
        )
        session.add(timelog)
        session.commit()

        # Act
        result = _find_done_timelog(session, pending_instance.id)

        # Assert
        assert result is not None
        assert result["substatus"] == DoneSubstatus.FULL
        assert result["completion_percentage"] == 95
        assert result["minutes"] == 57

    def test_br_tui_022_find_done_timelog_no_timelog(
        self, session: Session, pending_instance: HabitInstance
    ) -> None:
        """Instância sem TimeLog retorna None."""
        assert pending_instance.id is not None

        # Act
        result = _find_done_timelog(session, pending_instance.id)

        # Assert
        assert result is None

    def test_br_tui_022_find_done_timelog_partial(
        self, session: Session, pending_instance: HabitInstance
    ) -> None:
        """TimeLog com 50% de conclusão retorna PARTIAL."""
        assert pending_instance.id is not None

        # Create TimeLog DONE with 1800s (50% of 3600s target)
        start_dt = datetime.combine(pending_instance.date, time(8, 0))
        end_dt = datetime.combine(pending_instance.date, time(8, 30))
        timelog = TimeLog(
            habit_instance_id=pending_instance.id,
            status=TimerStatus.DONE,
            start_time=start_dt,
            end_time=end_dt,
            duration_seconds=1800,
        )
        session.add(timelog)
        session.commit()

        # Act
        result = _find_done_timelog(session, pending_instance.id)

        # Assert
        assert result is not None
        assert result["substatus"] == DoneSubstatus.PARTIAL
        assert result["completion_percentage"] == 50
        assert result["minutes"] == 30

    def test_br_tui_022_find_done_timelog_overdone(
        self, session: Session, pending_instance: HabitInstance
    ) -> None:
        """TimeLog com 130% de conclusão retorna OVERDONE."""
        assert pending_instance.id is not None

        # Create TimeLog DONE with 4680s (130% of 3600s target)
        start_dt = datetime.combine(pending_instance.date, time(8, 0))
        end_dt = datetime.combine(pending_instance.date, time(9, 18))
        timelog = TimeLog(
            habit_instance_id=pending_instance.id,
            status=TimerStatus.DONE,
            start_time=start_dt,
            end_time=end_dt,
            duration_seconds=4680,
        )
        session.add(timelog)
        session.commit()

        # Act
        result = _find_done_timelog(session, pending_instance.id)

        # Assert
        assert result is not None
        assert result["substatus"] == DoneSubstatus.OVERDONE
        assert result["completion_percentage"] == 130
        assert result["minutes"] == 78

    def test_br_tui_022_find_done_timelog_excessive(
        self, session: Session, pending_instance: HabitInstance
    ) -> None:
        """TimeLog com 160% de conclusão retorna EXCESSIVE."""
        assert pending_instance.id is not None

        # Create TimeLog DONE with 5760s (160% of 3600s target)
        start_dt = datetime.combine(pending_instance.date, time(8, 0))
        end_dt = datetime.combine(pending_instance.date, time(9, 36))
        timelog = TimeLog(
            habit_instance_id=pending_instance.id,
            status=TimerStatus.DONE,
            start_time=start_dt,
            end_time=end_dt,
            duration_seconds=5760,
        )
        session.add(timelog)
        session.commit()

        # Act
        result = _find_done_timelog(session, pending_instance.id)

        # Assert
        assert result is not None
        assert result["substatus"] == DoneSubstatus.EXCESSIVE
        assert result["completion_percentage"] == 160
        assert result["minutes"] == 96


class TestBRTui022DoneSubstatusOptions:
    """BR-TUI-022: DONE_SUBSTATUS_OPTIONS tem 4 entradas válidas."""

    def test_br_tui_022_options_has_four_entries(self) -> None:
        """DONE_SUBSTATUS_OPTIONS contém exatamente 4 opções."""
        assert len(DONE_SUBSTATUS_OPTIONS) == 4

    def test_br_tui_022_options_match_enum(self) -> None:
        """Cada key de DONE_SUBSTATUS_OPTIONS é um membro válido de DoneSubstatus."""
        for key, _label in DONE_SUBSTATUS_OPTIONS:
            # Access by name should not raise
            assert hasattr(DoneSubstatus, key)
            enum_member = getattr(DoneSubstatus, key)
            assert isinstance(enum_member, DoneSubstatus)
