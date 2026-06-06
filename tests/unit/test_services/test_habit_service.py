"""Testes unitários do HabitService — Archive Lifecycle (BR-HABIT-006).

Cobre archive (soft delete via delete_habit), purge (hard delete),
restore, semântica de listagem e o skip de geração de instâncias para
hábitos arquivados.

Referências:
    - ADR-057: Archive Lifecycle para Habit
    - BR-HABIT-005: Deleção de Habit (semântica de archive)
    - BR-HABIT-006: Archive Lifecycle
"""

from datetime import date, datetime, time

from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, TimeLog
from timeblock.models.enums import Status
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.habit_service import HabitService


def _make_habit(session: Session, routine_service, title: str = "Leitura matinal") -> Habit:
    """Cria uma rotina e um hábito ativo para os cenários de archive."""
    routine = routine_service.create_routine("Rotina Teste")
    assert routine.id is not None
    service = HabitService(session)
    return service.create_habit(
        routine_id=routine.id,
        title=title,
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        recurrence=Recurrence.EVERYDAY,
    )


def _add_instance_with_timelog(session: Session, habit_id: int) -> tuple[int, int]:
    """Adiciona uma HabitInstance e um TimeLog vinculado. Retorna (inst_id, log_id)."""
    instance = HabitInstance(
        habit_id=habit_id,
        date=date.today(),
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)

    log = TimeLog(habit_instance_id=instance.id, start_time=datetime.now())
    session.add(log)
    session.commit()
    session.refresh(log)
    assert instance.id is not None
    assert log.id is not None
    return instance.id, log.id


class TestBRHabit006Archive:
    """BR-HABIT-006: Archive Lifecycle (archive / purge / restore)."""

    def test_br_habit_006_delete_sets_archived_at(self, session: Session, routine_service):
        """delete_habit marca archived_at em vez de remover o registro."""
        habit = _make_habit(session, routine_service)
        assert habit.id is not None
        service = HabitService(session)

        assert service.delete_habit(habit.id) is True

        refreshed = service.get_habit(habit.id)
        assert refreshed is not None
        assert refreshed.archived_at is not None

    def test_br_habit_006_archive_preserves_instances(self, session: Session, routine_service):
        """Archive preserva HabitInstance associadas."""
        habit = _make_habit(session, routine_service)
        assert habit.id is not None
        inst_id, _ = _add_instance_with_timelog(session, habit.id)
        service = HabitService(session)

        service.delete_habit(habit.id)

        assert session.get(HabitInstance, inst_id) is not None

    def test_br_habit_006_archive_preserves_timelogs(self, session: Session, routine_service):
        """Archive preserva TimeLog associados às instâncias."""
        habit = _make_habit(session, routine_service)
        assert habit.id is not None
        _, log_id = _add_instance_with_timelog(session, habit.id)
        service = HabitService(session)

        service.delete_habit(habit.id)

        assert session.get(TimeLog, log_id) is not None

    def test_br_habit_006_list_habits_excludes_archived_by_default(
        self, session: Session, routine_service
    ):
        """list_habits() omite arquivados por padrão."""
        habit = _make_habit(session, routine_service)
        assert habit.id is not None
        service = HabitService(session)
        service.delete_habit(habit.id)

        ids = [h.id for h in service.list_habits()]
        assert habit.id not in ids

    def test_br_habit_006_list_habits_include_archived_returns_all(
        self, session: Session, routine_service
    ):
        """list_habits(include_archived=True) retorna também os arquivados."""
        habit = _make_habit(session, routine_service)
        assert habit.id is not None
        service = HabitService(session)
        service.delete_habit(habit.id)

        ids = [h.id for h in service.list_habits(include_archived=True)]
        assert habit.id in ids

    def test_br_habit_006_get_habit_returns_archived(self, session: Session, routine_service):
        """get_habit não filtra arquivados (inspeção administrativa)."""
        habit = _make_habit(session, routine_service)
        assert habit.id is not None
        service = HabitService(session)
        service.delete_habit(habit.id)

        assert service.get_habit(habit.id) is not None

    def test_br_habit_006_restore_clears_archived_at(self, session: Session, routine_service):
        """restore_habit zera archived_at e devolve o hábito às listagens."""
        habit = _make_habit(session, routine_service)
        assert habit.id is not None
        service = HabitService(session)
        service.delete_habit(habit.id)

        restored = service.restore_habit(habit.id)

        assert restored is not None
        assert restored.archived_at is None
        assert habit.id in [h.id for h in service.list_habits()]

    def test_br_habit_006_purge_destroys_cascade(self, session: Session, routine_service):
        """purge_habit destrói o hábito, suas instâncias e os TimeLog."""
        habit = _make_habit(session, routine_service)
        assert habit.id is not None
        inst_id, log_id = _add_instance_with_timelog(session, habit.id)
        service = HabitService(session)

        assert service.purge_habit(habit.id) is True

        assert service.get_habit(habit.id) is None
        assert session.get(HabitInstance, inst_id) is None
        assert session.get(TimeLog, log_id) is None

    def test_br_habit_006_generate_instances_skips_archived(
        self, session: Session, routine_service
    ):
        """generate_instances retorna [] para hábito arquivado."""
        habit = _make_habit(session, routine_service)
        assert habit.id is not None
        service = HabitService(session)
        service.delete_habit(habit.id)

        result = HabitInstanceService.generate_instances(
            habit_id=habit.id,
            start_date=date.today(),
            end_date=date.today(),
            session=session,
        )
        assert result == []
