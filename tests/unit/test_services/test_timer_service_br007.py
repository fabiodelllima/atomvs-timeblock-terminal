"""Testes unitários para BR-TIMER-007: Log Manual de Tempo.

BR-TIMER-007: Usuários podem registrar tempo manualmente sem usar timer.
Dois modos mutuamente exclusivos:
- Intervalo: start_time + end_time
- Duração: duration_minutes
"""

from datetime import date, time

import pytest
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine
from timeblock.models.enums import DoneSubstatus, Status
from timeblock.services.timer_service import TimerService


class TestBRTimer007LogManual:
    """Testes para log manual de tempo."""

    @pytest.fixture
    def setup_habit_instance(self, session: Session) -> HabitInstance:
        """Cria rotina, hábito e instância para testes."""
        routine = Routine(name="Test Routine", is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Test Habit",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),  # 60 min target
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=habit.scheduled_start,
            scheduled_end=habit.scheduled_end,
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        return instance

    # ================================================================
    # Testes de Validação de Entrada
    # ================================================================

    def test_br_timer_007_rejects_no_input(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Rejeita quando nenhum modo é fornecido."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        with pytest.raises(ValueError, match="must provide interval"):
            service.log_manual(
                habit_instance_id=instance.id,
                session=session,
            )

    def test_br_timer_007_rejects_nonexistent_instance(self, session: Session) -> None:
        """Rejeita quando HabitInstance não existe."""
        service = TimerService()

        with pytest.raises(ValueError, match="not found"):
            service.log_manual(
                habit_instance_id=99999,
                duration_minutes=30,
                session=session,
            )

    def test_br_timer_007_rejects_negative_duration(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Rejeita duração negativa."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        with pytest.raises(ValueError, match="duration must be positive"):
            service.log_manual(
                habit_instance_id=instance.id,
                duration_minutes=-10,
                session=session,
            )

    def test_br_timer_007_rejects_only_start_without_end(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Rejeita start sem end."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        with pytest.raises(ValueError, match="start requires end"):
            service.log_manual(
                habit_instance_id=instance.id,
                start_time=time(7, 0),
                session=session,
            )

    def test_br_timer_007_rejects_only_end_without_start(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Rejeita end sem start."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        with pytest.raises(ValueError, match="start requires end"):
            service.log_manual(
                habit_instance_id=instance.id,
                end_time=time(8, 0),
                session=session,
            )

    # ================================================================
    # Testes de Substatus
    # ================================================================

    def test_br_timer_007_substatus_partial_under_90_percent(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Completion < 90% resulta em substatus PARTIAL."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        # 30 min de 60 min = 50%
        timelog = service.log_manual(
            habit_instance_id=instance.id,
            duration_minutes=30,
            session=session,
        )

        session.refresh(instance)
        assert instance.done_substatus == DoneSubstatus.PARTIAL
        assert instance.completion_percentage == 50
        assert timelog.duration_seconds == 1800

    def test_br_timer_007_substatus_full_between_90_and_110_percent(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Completion entre 90% e 110% resulta em substatus FULL."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        # 60 min de 60 min = 100%
        timelog = service.log_manual(
            habit_instance_id=instance.id,
            duration_minutes=60,
            session=session,
        )

        session.refresh(instance)
        assert instance.done_substatus == DoneSubstatus.FULL
        assert instance.completion_percentage == 100
        assert timelog.duration_seconds == 3600

    def test_br_timer_007_substatus_overdone_between_110_and_150_percent(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Completion entre 110% e 150% resulta em substatus OVERDONE."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        # 80 min de 60 min = 133%
        timelog = service.log_manual(
            habit_instance_id=instance.id,
            duration_minutes=80,
            session=session,
        )

        session.refresh(instance)
        assert instance.done_substatus == DoneSubstatus.OVERDONE
        assert instance.completion_percentage == 133
        assert timelog.duration_seconds == 4800

    def test_br_timer_007_substatus_excessive_over_150_percent(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Completion > 150% resulta em substatus EXCESSIVE."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        # 120 min de 60 min = 200%
        timelog = service.log_manual(
            habit_instance_id=instance.id,
            duration_minutes=120,
            session=session,
        )

        session.refresh(instance)
        assert instance.done_substatus == DoneSubstatus.EXCESSIVE
        assert instance.completion_percentage == 200
        assert timelog.duration_seconds == 7200

    # ================================================================
    # Testes de Estado da Instância
    # ================================================================

    def test_br_timer_007_marks_instance_as_done(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Log manual marca instância como DONE."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        assert instance.status == Status.PENDING

        service.log_manual(
            habit_instance_id=instance.id,
            duration_minutes=60,
            session=session,
        )

        session.refresh(instance)
        assert instance.status == Status.DONE
        assert instance.not_done_substatus is None

    def test_br_timer_007_clears_not_done_substatus(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Log manual limpa not_done_substatus."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        service.log_manual(
            habit_instance_id=instance.id,
            start_time=time(7, 0),
            end_time=time(8, 0),
            session=session,
        )

        session.refresh(instance)
        assert instance.not_done_substatus is None

    # ================================================================
    # Testes de TimeLog Criado
    # ================================================================

    def test_br_timer_007_creates_timelog_with_interval_mode(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Modo intervalo cria TimeLog com timestamps corretos."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        timelog = service.log_manual(
            habit_instance_id=instance.id,
            start_time=time(7, 30),
            end_time=time(8, 15),
            session=session,
        )

        assert timelog.habit_instance_id == instance.id
        assert timelog.duration_seconds == 2700  # 45 min
        assert timelog.start_time is not None
        assert timelog.end_time is not None
        assert timelog.start_time.hour == 7
        assert timelog.start_time.minute == 30
        assert timelog.end_time.hour == 8
        assert timelog.end_time.minute == 15

    def test_br_timer_007_creates_timelog_with_duration_mode(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """Modo duração cria TimeLog baseado em scheduled_start."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        timelog = service.log_manual(
            habit_instance_id=instance.id,
            duration_minutes=45,
            session=session,
        )

        assert timelog.habit_instance_id == instance.id
        assert timelog.duration_seconds == 2700  # 45 min
        assert timelog.start_time is not None
        assert timelog.end_time is not None
        # Start baseado em scheduled_start (07:00)
        assert timelog.start_time.hour == 7
        assert timelog.start_time.minute == 0
        # End = start + duration
        assert timelog.end_time.hour == 7
        assert timelog.end_time.minute == 45

    # ================================================================
    # Testes de Boundary (Limites)
    # ================================================================

    def test_br_timer_007_boundary_89_percent_is_partial(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """89% é PARTIAL (limite inferior)."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        # 53.4 min de 60 min = 89%
        service.log_manual(
            habit_instance_id=instance.id,
            start_time=time(7, 0),
            end_time=time(7, 53),  # 53 min = 88.3%
            session=session,
        )

        session.refresh(instance)
        assert instance.done_substatus == DoneSubstatus.PARTIAL

    def test_br_timer_007_boundary_90_percent_is_full(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """90% é FULL (limite exato)."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        # 54 min de 60 min = 90%
        service.log_manual(
            habit_instance_id=instance.id,
            start_time=time(7, 0),
            end_time=time(7, 54),
            session=session,
        )

        session.refresh(instance)
        assert instance.done_substatus == DoneSubstatus.FULL
        assert instance.completion_percentage == 90

    def test_br_timer_007_boundary_110_percent_is_full(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """110% ainda é FULL."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        # 66 min de 60 min = 110%
        service.log_manual(
            habit_instance_id=instance.id,
            start_time=time(7, 0),
            end_time=time(8, 6),
            session=session,
        )

        session.refresh(instance)
        assert instance.done_substatus == DoneSubstatus.FULL
        assert instance.completion_percentage == 110

    def test_br_timer_007_boundary_111_percent_is_overdone(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """111% é OVERDONE."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        # 67 min de 60 min = 111.6%
        service.log_manual(
            habit_instance_id=instance.id,
            start_time=time(7, 0),
            end_time=time(8, 7),
            session=session,
        )

        session.refresh(instance)
        assert instance.done_substatus == DoneSubstatus.OVERDONE

    def test_br_timer_007_boundary_150_percent_is_overdone(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """150% ainda é OVERDONE."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        # 90 min de 60 min = 150%
        service.log_manual(
            habit_instance_id=instance.id,
            duration_minutes=90,
            session=session,
        )

        session.refresh(instance)
        assert instance.done_substatus == DoneSubstatus.OVERDONE
        assert instance.completion_percentage == 150

    def test_br_timer_007_boundary_151_percent_is_excessive(
        self, session: Session, setup_habit_instance: HabitInstance
    ) -> None:
        """151% é EXCESSIVE."""
        service = TimerService()
        instance = setup_habit_instance
        assert instance.id is not None

        # 91 min de 60 min = 151.6%
        service.log_manual(
            habit_instance_id=instance.id,
            duration_minutes=91,
            session=session,
        )

        session.refresh(instance)
        assert instance.done_substatus == DoneSubstatus.EXCESSIVE
