"""Testes unitários para cálculo de substatus via timer.

BRs Cobertas:
    - BR-TIMER-005: Cálculo de Completion (formula completion_percentage)
    - BR-TIMER-006: Pause Tracking (substatus calculado ao parar)
    - BR-HABITINSTANCE-002: Substatus Obrigatório (status DONE requer done_substatus)
    - BR-HABITINSTANCE-003: Completion Thresholds (mapeamento % -> substatus)

Thresholds (BR-HABITINSTANCE-003):
    - < 80%: PARTIAL
    - 80-120%: FULL
    - 120-150%: OVERDONE
    - > 150%: EXCESSIVE
"""

from datetime import date, datetime, time, timedelta

import pytest
from sqlmodel import Session

from timeblock.models.enums import DoneSubstatus, Status
from timeblock.models.habit import Habit, Recurrence
from timeblock.models.habit_instance import HabitInstance
from timeblock.models.routine import Routine
from timeblock.models.time_log import TimeLog
from timeblock.services.timer_service import TimerService


@pytest.fixture
def routine(session: Session) -> Routine:
    """Cria Routine para testes."""
    routine = Routine(name="Test Routine")
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


@pytest.fixture
def habit(session: Session, routine: Routine) -> Habit:
    """Cria Habit para testes."""
    assert routine.id is not None, "Routine must have ID after commit"

    habit = Habit(
        routine_id=routine.id,
        title="Test Habit",
        scheduled_start=time(8, 0),
        scheduled_end=time(9, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)

    assert habit.id is not None, "Habit must have ID after commit"
    return habit


class TestBRTimerSubstatusCalculation:
    """Testes de cálculo de substatus ao parar timer.

    Valida integração entre:
        - BR-TIMER-005: completion_percentage = (actual / expected) * 100
        - BR-TIMER-006: substatus calculado automaticamente ao stop
        - BR-HABITINSTANCE-002: status DONE requer done_substatus preenchido
        - BR-HABITINSTANCE-003: thresholds definem qual substatus
    """

    def test_br_habitinstance_003_partial_75_percent(self, session: Session, habit: Habit):
        """BR-HABITINSTANCE-003: 75% completion -> PARTIAL.

        Referências:
            - BR-TIMER-005: Cálculo completion = 45/60 = 75%
            - BR-HABITINSTANCE-003: < 80% -> PARTIAL
            - BR-HABITINSTANCE-002: DONE requer done_substatus
        """
        assert habit.id is not None

        # DADO: HabitInstance com meta 60 minutos
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),  # 60 min meta
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        # Timer iniciado
        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        # Criar TimeLog ativo
        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None, "TimeLog must have ID after commit"

        # QUANDO: Para timer após 45 minutos (75%)
        from unittest.mock import patch

        stop_time = start_time + timedelta(minutes=45)

        with patch("timeblock.services.timer_service.datetime") as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            result_timelog = timer_service.stop_timer(timelog_id=timelog.id, session=session)

        # Refresh instance para pegar mudanças
        session.refresh(instance)

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.PARTIAL
        assert instance.completion_percentage == 75
        assert instance.not_done_substatus is None
        assert result_timelog.duration_seconds == 2700  # 45min

    def test_br_habitinstance_003_full_90_percent(self, session: Session, habit: Habit):
        """BR-HABITINSTANCE-003: 90% completion -> FULL.

        Referências:
            - BR-TIMER-005: Cálculo completion = 54/60 = 90%
            - BR-HABITINSTANCE-003: 80-120% -> FULL
        """
        assert habit.id is not None

        # DADO
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None

        # QUANDO: 54 minutos = 90%
        from unittest.mock import patch

        stop_time = start_time + timedelta(minutes=54)

        with patch("timeblock.services.timer_service.datetime") as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            timer_service.stop_timer(timelog_id=timelog.id, session=session)

        session.refresh(instance)

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.FULL
        assert instance.completion_percentage == 90
        assert instance.not_done_substatus is None

    def test_br_habitinstance_003_full_100_percent(self, session: Session, habit: Habit):
        """BR-HABITINSTANCE-003: 100% completion -> FULL.

        Referências:
            - BR-TIMER-005: Cálculo completion = 60/60 = 100%
            - BR-HABITINSTANCE-003: 80-120% -> FULL
        """
        assert habit.id is not None

        # DADO
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None

        # QUANDO: 60 minutos = 100%
        from unittest.mock import patch

        stop_time = start_time + timedelta(minutes=60)

        with patch("timeblock.services.timer_service.datetime") as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            timer_service.stop_timer(timelog_id=timelog.id, session=session)

        session.refresh(instance)

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.FULL
        assert instance.completion_percentage == 100

    def test_br_habitinstance_003_overdone_130_percent(self, session: Session, habit: Habit):
        """BR-HABITINSTANCE-003: 130% completion -> OVERDONE.

        Referências:
            - BR-TIMER-005: Cálculo completion = 78/60 = 130%
            - BR-HABITINSTANCE-003: 120-150% -> OVERDONE
        """
        assert habit.id is not None

        # DADO
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None

        # QUANDO: 78 minutos = 130%
        from unittest.mock import patch

        stop_time = start_time + timedelta(minutes=78)

        with patch("timeblock.services.timer_service.datetime") as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            timer_service.stop_timer(timelog_id=timelog.id, session=session)

        session.refresh(instance)

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.OVERDONE
        assert instance.completion_percentage == 130

    def test_br_habitinstance_003_excessive_200_percent(self, session: Session, habit: Habit):
        """BR-HABITINSTANCE-003: 200% completion -> EXCESSIVE.

        Referências:
            - BR-TIMER-005: Cálculo completion = 120/60 = 200%
            - BR-HABITINSTANCE-003: > 150% -> EXCESSIVE
        """
        assert habit.id is not None

        # DADO
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None

        # QUANDO: 120 minutos = 200%
        from unittest.mock import patch

        stop_time = start_time + timedelta(minutes=120)

        with patch("timeblock.services.timer_service.datetime") as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            timer_service.stop_timer(timelog_id=timelog.id, session=session)

        session.refresh(instance)

        # ENTÃO
        assert instance.status == Status.DONE
        assert instance.done_substatus == DoneSubstatus.EXCESSIVE
        assert instance.completion_percentage == 200


class TestBRHabitInstance002StatusConsistency:
    """BR-HABITINSTANCE-002: Status DONE requer substatus obrigatório."""

    def test_br_habitinstance_002_done_requires_substatus(self, session: Session, habit: Habit):
        """BR-HABITINSTANCE-002: Validação de consistência status/substatus.

        DADO: Timer parado com completion válido
        QUANDO: Validação de consistência executada
        ENTÃO: Não lança exceção (substatus preenchido corretamente)
        """
        assert habit.id is not None

        # DADO
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()
        start_time = datetime.combine(date.today(), time(8, 0))

        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        assert timelog.id is not None

        # QUANDO
        from unittest.mock import patch

        stop_time = start_time + timedelta(minutes=55)

        with patch("timeblock.services.timer_service.datetime") as mock_dt:
            mock_dt.now.return_value = stop_time
            mock_dt.combine = datetime.combine

            timer_service.stop_timer(timelog_id=timelog.id, session=session)

        session.refresh(instance)

        # ENTÃO: Validação deve passar
        instance.validate_status_consistency()  # Não deve lançar exceção

        # Verificar consistência manual
        assert instance.status == Status.DONE
        assert instance.done_substatus is not None
        assert instance.not_done_substatus is None
        assert instance.skip_reason is None


class TestBRTimerValidation:
    """Validações de erro do TimerService."""

    def test_br_timer_stop_nonexistent_raises_error(self, session: Session, habit: Habit):
        """Timer stop com ID inexistente -> ValueError.

        Referências:
            - BR-TIMER-002: Estados e Transições (validação)
        """
        assert habit.id is not None

        # DADO: HabitInstance sem timer ativo
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        timer_service = TimerService()

        # QUANDO: Tentar parar timer inexistente
        # ENTÃO: Deve lançar ValueError
        with pytest.raises(ValueError, match="TimeLog 99999 not found"):
            timer_service.stop_timer(timelog_id=99999, session=session)
