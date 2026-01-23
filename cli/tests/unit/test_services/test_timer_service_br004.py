"""Testes para BR-TIMER-004: Múltiplas Sessões.

BR-TIMER-004: Usuário pode fazer múltiplas sessões do mesmo habit no mesmo dia.

Workflow:
    - Sessão 1: start → stop (salva 60min)
    - Sessão 2: start → stop (salva 30min)
    - Total acumulado: 90min

Substatus é calculado sobre tempo acumulado de todas sessões.
"""

from datetime import date, datetime, time

import pytest
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine, TimeLog
from timeblock.models.enums import Status
from timeblock.services.timer_service import TimerService


# ============================================================
# Fixtures
# ============================================================
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
    habit = Habit(
        title="Test Habit",
        routine_id=routine.id,
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),  # 60 min meta
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@pytest.fixture
def habit_instance(session: Session, habit: Habit) -> HabitInstance:
    """Cria HabitInstance PENDING para testes."""
    instance = HabitInstance(
        habit_id=habit.id,
        date=date.today(),
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance


@pytest.fixture(autouse=True)
def reset_timer_state():
    """Reseta estado de pausa entre testes."""
    TimerService._active_pause_start = None
    yield
    TimerService._active_pause_start = None


# ============================================================
# BR-TIMER-004: Múltiplas Sessões
# ============================================================
class TestBRTimer004:
    """BR-TIMER-004: Múltiplas sessões permitidas no mesmo habit/dia.

    Usuário pode:
        - Fazer start → stop → start → stop no mesmo HabitInstance
        - Ter múltiplos TimeLogs para mesma instance
        - Acumular duração total de todas sessões
    """

    def test_br_timer_004_allows_multiple_sessions(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-004: Pode iniciar segunda sessão após stop."""
        # Sessão 1
        timelog1 = TimerService.start_timer(habit_instance.id, session)
        TimerService.stop_timer(timelog1.id, session)

        # Sessão 2
        timelog2 = TimerService.start_timer(habit_instance.id, session)

        assert timelog2 is not None
        assert timelog2.id != timelog1.id
        assert timelog2.habit_instance_id == habit_instance.id

    def test_br_timer_004_creates_multiple_timelogs(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-004: Cada sessão cria TimeLog separado."""
        # Sessão 1
        timelog1 = TimerService.start_timer(habit_instance.id, session)
        TimerService.stop_timer(timelog1.id, session)

        # Sessão 2
        timelog2 = TimerService.start_timer(habit_instance.id, session)
        TimerService.stop_timer(timelog2.id, session)

        # Listar timelogs da instance
        service = TimerService()
        timelogs = service.list_timelogs(habit_instance_id=habit_instance.id, session=session)

        assert len(timelogs) == 2
        assert timelogs[0].id == timelog1.id
        assert timelogs[1].id == timelog2.id

    def test_br_timer_004_accumulates_duration(self, session: Session, habit: Habit):
        """BR-TIMER-004: Duração total é soma de todas sessões."""
        # Criar instance com meta de 60 min
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        # Sessão 1: 30 minutos
        timelog1 = TimeLog(
            habit_instance_id=instance.id,
            start_time=datetime.combine(date.today(), time(9, 0)),
            end_time=datetime.combine(date.today(), time(9, 30)),
            duration_seconds=1800,  # 30 min
        )
        session.add(timelog1)
        session.commit()

        # Sessão 2: 25 minutos
        timelog2 = TimeLog(
            habit_instance_id=instance.id,
            start_time=datetime.combine(date.today(), time(14, 0)),
            end_time=datetime.combine(date.today(), time(14, 25)),
            duration_seconds=1500,  # 25 min
        )
        session.add(timelog2)
        session.commit()

        # Calcular total acumulado
        service = TimerService()
        timelogs = service.list_timelogs(habit_instance_id=instance.id, session=session)
        total_seconds = sum(t.duration_seconds or 0 for t in timelogs)

        assert len(timelogs) == 2
        assert total_seconds == 3300  # 55 min (30 + 25)

    def test_br_timer_004_three_sessions_same_day(self, session: Session, habit: Habit):
        """BR-TIMER-004: Três sessões no mesmo dia acumulam corretamente."""
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        # Criar 3 sessões manualmente
        durations = [1200, 900, 600]  # 20min, 15min, 10min
        for i, duration in enumerate(durations):
            timelog = TimeLog(
                habit_instance_id=instance.id,
                start_time=datetime.combine(date.today(), time(9 + i * 2, 0)),
                end_time=datetime.combine(date.today(), time(9 + i * 2, duration // 60)),
                duration_seconds=duration,
            )
            session.add(timelog)
        session.commit()

        # Verificar acumulação
        service = TimerService()
        timelogs = service.list_timelogs(habit_instance_id=instance.id, session=session)
        total_seconds = sum(t.duration_seconds or 0 for t in timelogs)

        assert len(timelogs) == 3
        assert total_seconds == 2700  # 45 min total

    def test_br_timer_004_completion_based_on_accumulated(self, session: Session, habit: Habit):
        """BR-TIMER-004: Completion percentage considera tempo acumulado."""
        # Meta: 60 minutos
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            status=Status.PENDING,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        # Sessão 1: 30 min (50%)
        timelog1 = TimeLog(
            habit_instance_id=instance.id,
            start_time=datetime.combine(date.today(), time(9, 0)),
            end_time=datetime.combine(date.today(), time(9, 30)),
            duration_seconds=1800,
        )
        session.add(timelog1)

        # Sessão 2: 24 min (40%)
        timelog2 = TimeLog(
            habit_instance_id=instance.id,
            start_time=datetime.combine(date.today(), time(14, 0)),
            end_time=datetime.combine(date.today(), time(14, 24)),
            duration_seconds=1440,
        )
        session.add(timelog2)
        session.commit()

        # Calcular completion acumulado
        service = TimerService()
        timelogs = service.list_timelogs(habit_instance_id=instance.id, session=session)
        total_seconds = sum(t.duration_seconds or 0 for t in timelogs)

        # Meta em segundos
        target_seconds = 60 * 60  # 60 min = 3600s
        completion = int((total_seconds / target_seconds) * 100)

        assert total_seconds == 3240  # 54 min
        assert completion == 90  # 90% do objetivo
