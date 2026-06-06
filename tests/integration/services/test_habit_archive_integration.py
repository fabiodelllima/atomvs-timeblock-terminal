"""Integration tests - HabitService archive preserva histórico (BR-HABIT-005).

Valida que arquivar um hábito (soft delete via delete_habit) preserva as
HabitInstance e os TimeLog associados no banco — o cerne da decisão do
ADR-057 e a correção do bug de integridade referencial da issue #61.

Referências:
    - ADR-019: Test Naming Convention
    - ADR-057: Archive Lifecycle para Habit
    - BR-HABIT-005: Deleção com semântica de archive
"""

from __future__ import annotations

from datetime import date, datetime, time

import pytest
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine, TimeLog
from timeblock.models.enums import DoneSubstatus, Status, TimerStatus
from timeblock.services.habit_service import HabitService


class TestBRHabit005ArchivePreservesTimelog:
    """Integration: delete_habit arquiva sem destruir HabitInstance/TimeLog.

    Diferente do hard delete original (que disparava cascade e deixava
    TimeLog órfão — bug da issue #61), o archive apenas marca archived_at.
    """

    @pytest.fixture
    def routine(self, test_db: Session) -> Routine:
        routine = Routine(name="Test Routine", is_active=True)
        test_db.add(routine)
        test_db.flush()
        test_db.refresh(routine)
        return routine

    @pytest.fixture
    def habit(self, test_db: Session, routine: Routine) -> Habit:
        assert routine.id is not None
        habit = Habit(
            title="Test Habit",
            routine_id=routine.id,
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        test_db.add(habit)
        test_db.flush()
        test_db.refresh(habit)
        return habit

    @pytest.fixture
    def done_instance_with_timelog(
        self, test_db: Session, habit: Habit
    ) -> tuple[HabitInstance, TimeLog]:
        assert habit.id is not None
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.DONE,
            done_substatus=DoneSubstatus.FULL,
            completion_percentage=92,
        )
        test_db.add(instance)
        test_db.flush()
        test_db.refresh(instance)

        timelog = TimeLog(
            habit_instance_id=instance.id,
            status=TimerStatus.DONE,
            start_time=datetime.combine(date.today(), time(8, 0)),
            end_time=datetime.combine(date.today(), time(8, 55)),
            duration_seconds=3300,
        )
        test_db.add(timelog)
        test_db.flush()
        test_db.refresh(timelog)
        return instance, timelog

    def test_br_habit_005_archive_preserves_instance_and_timelog(
        self,
        test_db: Session,
        done_instance_with_timelog: tuple[HabitInstance, TimeLog],
    ) -> None:
        """DADO um hábito com HabitInstance DONE e TimeLog associado,
        QUANDO o hábito é arquivado via delete_habit,
        ENTÃO o hábito fica marcado como arquivado (archived_at não nulo),
        E a HabitInstance permanece no banco,
        E o TimeLog permanece inalterado (status DONE, duração preservada).
        """
        instance, timelog = done_instance_with_timelog
        instance_id = instance.id
        timelog_id = timelog.id
        habit_id = instance.habit_id

        # ACT
        result = HabitService(test_db).delete_habit(habit_id)

        # ASSERT
        assert result is True
        test_db.expire_all()

        archived = test_db.get(Habit, habit_id)
        assert archived is not None
        assert archived.archived_at is not None

        preserved_instance = test_db.get(HabitInstance, instance_id)
        assert preserved_instance is not None

        preserved_log = test_db.get(TimeLog, timelog_id)
        assert preserved_log is not None
        assert preserved_log.status == TimerStatus.DONE
        assert preserved_log.duration_seconds == 3300
