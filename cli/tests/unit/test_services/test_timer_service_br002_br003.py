"""Testes para BR-TIMER-002 e BR-TIMER-003.

BR-TIMER-002: Estados e Transições
BR-TIMER-003: Stop vs Reset

Valida máquina de estados e comportamento diferenciado de stop/reset.
"""

from datetime import date, time, timedelta
from unittest.mock import patch

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
        scheduled_end=time(10, 0),
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
# BR-TIMER-002: Estados e Transições
# ============================================================
class TestBRTimer002:
    """BR-TIMER-002: Timer possui estados RUNNING e PAUSED.

    Máquina de Estados:
    - start: NO TIMER -> RUNNING
    - pause: RUNNING -> PAUSED
    - resume: PAUSED -> RUNNING
    - stop: RUNNING/PAUSED -> NO TIMER (salva)
    - reset: RUNNING/PAUSED -> NO TIMER (cancela)
    """

    def test_br_timer_002_start_creates_running(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: start cria timer em estado RUNNING.

        Estado inicial: NO TIMER
        Ação: start_timer()
        Estado final: RUNNING (TimeLog com end_time=None)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)

        assert timelog is not None
        assert timelog.habit_instance_id == habit_instance.id
        assert timelog.start_time is not None
        assert timelog.end_time is None  # RUNNING = end_time None

    def test_br_timer_002_pause_from_running(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: pause muda de RUNNING para PAUSED.

        Estado inicial: RUNNING
        Ação: pause_timer()
        Estado final: PAUSED (_active_pause_start setado)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)
        assert TimerService._active_pause_start is None  # RUNNING

        TimerService.pause_timer(timelog.id, session)

        assert TimerService._active_pause_start is not None  # PAUSED

    def test_br_timer_002_resume_from_paused(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: resume muda de PAUSED para RUNNING.

        Estado inicial: PAUSED
        Ação: resume_timer()
        Estado final: RUNNING (_active_pause_start limpo)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)
        assert TimerService._active_pause_start is not None  # PAUSED

        TimerService.resume_timer(timelog.id, session)

        assert TimerService._active_pause_start is None  # RUNNING

    def test_br_timer_002_stop_from_running(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: stop de RUNNING salva e finaliza.

        Estado inicial: RUNNING
        Ação: stop_timer()
        Estado final: NO TIMER (TimeLog com end_time setado)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)

        result = TimerService.stop_timer(timelog.id, session)

        assert result.end_time is not None  # NO TIMER (finalizado)
        assert result.duration_seconds is not None

    def test_br_timer_002_stop_from_paused(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: stop de PAUSED salva e finaliza.

        Estado inicial: PAUSED
        Ação: stop_timer()
        Estado final: NO TIMER (acumula pausa antes de salvar)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)

        result = TimerService.stop_timer(timelog.id, session)

        assert result.end_time is not None  # NO TIMER
        assert TimerService._active_pause_start is None  # Pausa limpa

    def test_br_timer_002_reset_cancels(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: reset (cancel) de RUNNING cancela sem salvar.

        Estado inicial: RUNNING
        Ação: cancel_timer()
        Estado final: NO TIMER (TimeLog deletado)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)
        timelog_id = timelog.id

        TimerService.cancel_timer(timelog.id, session)

        assert session.get(TimeLog, timelog_id) is None  # Deletado

    def test_br_timer_002_invalid_pause_when_not_running(self, session: Session):
        """BR-TIMER-002: pause sem timer ativo falha."""
        with pytest.raises(ValueError, match="not found"):
            TimerService.pause_timer(99999, session)

    def test_br_timer_002_invalid_resume_when_not_paused(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: resume sem estar pausado falha."""
        timelog = TimerService.start_timer(habit_instance.id, session)

        with pytest.raises(ValueError, match="not paused"):
            TimerService.resume_timer(timelog.id, session)


# ============================================================
# BR-TIMER-003: Stop vs Reset
# ============================================================
class TestBRTimer003:
    """BR-TIMER-003: stop e reset finalizam com comportamentos diferentes.

    stop:
    - Salva sessão no banco
    - Marca instance como DONE
    - Calcula completion percentage

    reset:
    - Cancela SEM salvar
    - Instance continua PENDING
    """

    def test_br_timer_003_stop_saves_session(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: stop salva TimeLog no banco com duração."""
        timelog = TimerService.start_timer(habit_instance.id, session)
        timelog_id = timelog.id

        result = TimerService.stop_timer(timelog.id, session)

        # TimeLog existe e tem dados
        saved = session.get(TimeLog, timelog_id)
        assert saved is not None
        assert saved.end_time is not None
        assert saved.duration_seconds is not None

    def test_br_timer_003_stop_marks_done(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: stop marca HabitInstance como DONE."""
        timelog = TimerService.start_timer(habit_instance.id, session)

        TimerService.stop_timer(timelog.id, session)

        session.refresh(habit_instance)
        assert habit_instance.status == Status.DONE
        assert habit_instance.done_substatus is not None

    def test_br_timer_003_stop_calculates_completion(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: stop calcula completion percentage."""
        timelog = TimerService.start_timer(habit_instance.id, session)

        TimerService.stop_timer(timelog.id, session)

        session.refresh(habit_instance)
        assert habit_instance.completion_percentage is not None
        assert habit_instance.completion_percentage >= 0

    def test_br_timer_003_reset_no_save(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: reset (cancel) deleta TimeLog sem salvar."""
        timelog = TimerService.start_timer(habit_instance.id, session)
        timelog_id = timelog.id

        TimerService.cancel_timer(timelog.id, session)

        # TimeLog foi deletado
        assert session.get(TimeLog, timelog_id) is None

    def test_br_timer_003_reset_keeps_pending(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: reset mantém HabitInstance PENDING."""
        timelog = TimerService.start_timer(habit_instance.id, session)

        TimerService.cancel_timer(timelog.id, session)

        session.refresh(habit_instance)
        assert habit_instance.status == Status.PENDING
        assert habit_instance.done_substatus is None

    def test_br_timer_003_stop_allows_new_session(
        self, session: Session, habit: Habit
    ):
        """BR-TIMER-003: após stop, pode iniciar nova sessão."""
        # Criar duas instances
        instance1 = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            status=Status.PENDING,
        )
        session.add(instance1)
        session.commit()
        session.refresh(instance1)

        # Primeira sessão
        timelog1 = TimerService.start_timer(instance1.id, session)
        TimerService.stop_timer(timelog1.id, session)

        # Segunda sessão no mesmo instance (múltiplas sessões)
        timelog2 = TimerService.start_timer(instance1.id, session)

        assert timelog2 is not None
        assert timelog2.id != timelog1.id
