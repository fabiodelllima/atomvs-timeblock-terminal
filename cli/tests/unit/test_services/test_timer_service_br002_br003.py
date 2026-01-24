"""Testes para BR-TIMER-002 e BR-TIMER-003.

BR-TIMER-002: Estados e Transições (4 estados persistidos)
BR-TIMER-003: Stop vs Reset

Valida máquina de estados com persistência no banco.
"""

from datetime import date, time

import pytest
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine, TimeLog
from timeblock.models.enums import Status, TimerStatus
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


# ============================================================
# BR-TIMER-002: Estados e Transições
# ============================================================


class TestBRTimer002:
    """BR-TIMER-002: Timer possui 4 estados persistidos no banco.

    Estados:
        - RUNNING: Timer contando tempo
        - PAUSED: Timer pausado temporariamente
        - DONE: Timer finalizado com stop
        - CANCELLED: Timer resetado

    Máquina de Estados:
        - start: NO TIMER -> RUNNING
        - pause: RUNNING -> PAUSED
        - resume: PAUSED -> RUNNING
        - stop: RUNNING/PAUSED -> DONE
        - reset: RUNNING/PAUSED -> CANCELLED
    """

    def test_br_timer_002_start_creates_running(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: start cria timer com status RUNNING.

        Estado inicial: NO TIMER
        Ação: start_timer()
        Estado final: RUNNING (status persistido no banco)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)

        assert timelog is not None
        assert timelog.status == TimerStatus.RUNNING
        assert timelog.start_time is not None
        assert timelog.end_time is None

    def test_br_timer_002_pause_from_running(self, session: Session, habit_instance: HabitInstance):
        """BR-TIMER-002: pause muda status de RUNNING para PAUSED.

        Estado inicial: RUNNING
        Ação: pause_timer()
        Estado final: PAUSED (status e pause_start persistidos)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)
        assert timelog.status == TimerStatus.RUNNING

        TimerService.pause_timer(timelog.id, session)

        session.refresh(timelog)
        assert timelog.status == TimerStatus.PAUSED
        assert timelog.pause_start is not None

    def test_br_timer_002_resume_from_paused(self, session: Session, habit_instance: HabitInstance):
        """BR-TIMER-002: resume muda status de PAUSED para RUNNING.

        Estado inicial: PAUSED
        Ação: resume_timer()
        Estado final: RUNNING (pause_start limpo, paused_duration acumulado)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)

        session.refresh(timelog)
        assert timelog.status == TimerStatus.PAUSED

        TimerService.resume_timer(timelog.id, session)

        session.refresh(timelog)
        assert timelog.status == TimerStatus.RUNNING
        assert timelog.pause_start is None
        assert timelog.paused_duration >= 0

    def test_br_timer_002_stop_creates_done(self, session: Session, habit_instance: HabitInstance):
        """BR-TIMER-002: stop muda status para DONE.

        Estado inicial: RUNNING
        Ação: stop_timer()
        Estado final: DONE (end_time e duration_seconds preenchidos)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)

        TimerService.stop_timer(timelog.id, session)

        session.refresh(timelog)
        assert timelog.status == TimerStatus.DONE
        assert timelog.end_time is not None
        assert timelog.duration_seconds is not None

    def test_br_timer_002_stop_from_paused_creates_done(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: stop de PAUSED também cria DONE.

        Estado inicial: PAUSED
        Ação: stop_timer()
        Estado final: DONE (acumula pausa antes de finalizar)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)

        TimerService.stop_timer(timelog.id, session)

        session.refresh(timelog)
        assert timelog.status == TimerStatus.DONE
        assert timelog.end_time is not None

    def test_br_timer_002_reset_creates_cancelled(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: reset muda status para CANCELLED.

        Estado inicial: RUNNING
        Ação: reset_timer()
        Estado final: CANCELLED (TimeLog mantido para auditoria)
        """
        timelog = TimerService.start_timer(habit_instance.id, session)
        timelog_id = timelog.id

        TimerService.reset_timer(timelog.id, session)

        # TimeLog existe mas está CANCELLED
        saved = session.get(TimeLog, timelog_id)
        assert saved is not None
        assert saved.status == TimerStatus.CANCELLED

    def test_br_timer_002_status_persists_in_db(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: status persiste no banco entre operações.

        Valida que status não é variável volátil.
        """
        timelog = TimerService.start_timer(habit_instance.id, session)
        timelog_id = timelog.id

        # Recarrega do banco
        reloaded = session.get(TimeLog, timelog_id)
        assert reloaded.status == TimerStatus.RUNNING

        # Pausa e recarrega
        TimerService.pause_timer(timelog_id, session)
        session.expire(reloaded)
        reloaded = session.get(TimeLog, timelog_id)
        assert reloaded.status == TimerStatus.PAUSED

    def test_br_timer_002_cannot_pause_when_paused(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: não pode pausar timer já pausado."""
        timelog = TimerService.start_timer(habit_instance.id, session)
        TimerService.pause_timer(timelog.id, session)

        with pytest.raises(ValueError, match="already paused"):
            TimerService.pause_timer(timelog.id, session)

    def test_br_timer_002_cannot_resume_when_running(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-002: não pode retomar timer não pausado."""
        timelog = TimerService.start_timer(habit_instance.id, session)

        with pytest.raises(ValueError, match="not paused"):
            TimerService.resume_timer(timelog.id, session)


# ============================================================
# BR-TIMER-003: Stop vs Reset
# ============================================================


class TestBRTimer003:
    """BR-TIMER-003: stop e reset finalizam com comportamentos diferentes.

    stop:
        - Muda status para DONE
        - Salva end_time e duration_seconds
        - Atualiza HabitInstance (DONE + substatus)

    reset:
        - Muda status para CANCELLED
        - Preenche cancel_reason (opcional)
        - HabitInstance permanece PENDING
    """

    def test_br_timer_003_stop_saves_session(self, session: Session, habit_instance: HabitInstance):
        """BR-TIMER-003: stop salva TimeLog com status DONE."""
        timelog = TimerService.start_timer(habit_instance.id, session)
        timelog_id = timelog.id

        TimerService.stop_timer(timelog.id, session)

        saved = session.get(TimeLog, timelog_id)
        assert saved is not None
        assert saved.status == TimerStatus.DONE
        assert saved.end_time is not None
        assert saved.duration_seconds is not None

    def test_br_timer_003_stop_updates_instance(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: stop atualiza HabitInstance para DONE."""
        timelog = TimerService.start_timer(habit_instance.id, session)

        TimerService.stop_timer(timelog.id, session)

        session.refresh(habit_instance)
        assert habit_instance.status == Status.DONE
        assert habit_instance.done_substatus is not None

    def test_br_timer_003_reset_creates_cancelled(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: reset marca TimeLog como CANCELLED."""
        timelog = TimerService.start_timer(habit_instance.id, session)
        timelog_id = timelog.id

        TimerService.reset_timer(timelog.id, session)

        saved = session.get(TimeLog, timelog_id)
        assert saved is not None
        assert saved.status == TimerStatus.CANCELLED

    def test_br_timer_003_reset_keeps_pending(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: reset mantém HabitInstance PENDING."""
        timelog = TimerService.start_timer(habit_instance.id, session)

        TimerService.reset_timer(timelog.id, session)

        session.refresh(habit_instance)
        assert habit_instance.status == Status.PENDING

    def test_br_timer_003_reset_with_reason(self, session: Session, habit_instance: HabitInstance):
        """BR-TIMER-003: reset aceita motivo opcional."""
        timelog = TimerService.start_timer(habit_instance.id, session)
        timelog_id = timelog.id

        TimerService.reset_timer(timelog.id, session, reason="Iniciei habit errado")

        saved = session.get(TimeLog, timelog_id)
        assert saved.status == TimerStatus.CANCELLED
        assert saved.cancel_reason == "Iniciei habit errado"

    def test_br_timer_003_reset_specific_session(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: reset de sessão DONE específica."""
        # Criar sessão finalizada
        timelog = TimerService.start_timer(habit_instance.id, session)
        TimerService.stop_timer(timelog.id, session)

        session.refresh(timelog)
        assert timelog.status == TimerStatus.DONE

        # Reset da sessão já finalizada
        TimerService.reset_timer(timelog.id, session, reason="Contabilizei errado")

        session.refresh(timelog)
        assert timelog.status == TimerStatus.CANCELLED
        assert timelog.cancel_reason == "Contabilizei errado"

    def test_br_timer_003_cannot_reset_cancelled(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: não pode resetar sessão já CANCELLED."""
        timelog = TimerService.start_timer(habit_instance.id, session)
        TimerService.reset_timer(timelog.id, session)

        with pytest.raises(ValueError, match="already cancelled"):
            TimerService.reset_timer(timelog.id, session)

    def test_br_timer_003_stop_allows_new_session(
        self, session: Session, habit_instance: HabitInstance
    ):
        """BR-TIMER-003: após stop, pode iniciar nova sessão."""
        # Primeira sessão
        timelog1 = TimerService.start_timer(habit_instance.id, session)
        TimerService.stop_timer(timelog1.id, session)

        # Segunda sessão (múltiplas sessões BR-TIMER-004)
        timelog2 = TimerService.start_timer(habit_instance.id, session)

        assert timelog2 is not None
        assert timelog2.id != timelog1.id
        assert timelog2.status == TimerStatus.RUNNING
