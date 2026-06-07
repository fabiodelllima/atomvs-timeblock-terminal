"""Service para gerenciamento de hábitos."""

from datetime import datetime, time

from sqlmodel import Session, select

from timeblock.models import Habit, Recurrence, TimeLog
from timeblock.utils.logger import get_logger

logger = get_logger(__name__)


class HabitService:
    """Serviço de gerenciamento de hábitos.

    Segue ADR-007: Service Layer com session injection.
    """

    def __init__(self, session: Session) -> None:
        """Inicializa service com session injetada."""
        self.session = session

    def create_habit(
        self,
        routine_id: int,
        title: str,
        scheduled_start: time,
        scheduled_end: time,
        recurrence: Recurrence,
        color: str | None = None,
    ) -> Habit:
        """Cria um novo hábito."""
        title = title.strip()
        if not title:
            raise ValueError("Habit title cannot be empty")
        if len(title) > 200:
            raise ValueError("Habit title cannot exceed 200 characters")
        if scheduled_start >= scheduled_end:
            raise ValueError("Start time must be before end time")

        habit = Habit(
            routine_id=routine_id,
            title=title,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            recurrence=recurrence,
            color=color,
        )
        self.session.add(habit)
        self.session.commit()
        self.session.refresh(habit)
        logger.info("Hábito criado: id=%s, title='%s'", habit.id, habit.title)
        return habit

    def get_habit(self, habit_id: int) -> Habit | None:
        """Busca hábito por ID."""
        return self.session.get(Habit, habit_id)

    def list_habits(
        self, routine_id: int | None = None, include_archived: bool = False
    ) -> list[Habit]:
        """Lista hábitos ativos (BR-HABIT-006).

        Por padrão exclui arquivados (archived_at IS NULL). Use
        include_archived=True para retornar todos.
        """
        statement = select(Habit)
        if routine_id is not None:
            statement = statement.where(Habit.routine_id == routine_id)
        if not include_archived:
            statement = statement.where(Habit.archived_at == None)  # noqa: E711
        return list(self.session.exec(statement).all())

    def list_archived_habits(self, routine_id: int | None = None) -> list[Habit]:
        """Lista apenas hábitos arquivados (BR-HABIT-006)."""
        statement = select(Habit).where(Habit.archived_at != None)  # noqa: E711
        if routine_id is not None:
            statement = statement.where(Habit.routine_id == routine_id)
        return list(self.session.exec(statement).all())

    def update_habit(
        self,
        habit_id: int,
        title: str | None = None,
        scheduled_start: time | None = None,
        scheduled_end: time | None = None,
        recurrence: Recurrence | None = None,
        color: str | None = None,
    ) -> Habit | None:
        """Atualiza hábito existente."""
        habit = self.session.get(Habit, habit_id)
        if not habit:
            return None

        if title is not None:
            title_stripped = title.strip()
            if not title_stripped:
                raise ValueError("Habit title cannot be empty")
            if len(title_stripped) > 200:
                raise ValueError("Habit title cannot exceed 200 characters")
            habit.title = title_stripped
        if scheduled_start is not None:
            habit.scheduled_start = scheduled_start
        if scheduled_end is not None:
            habit.scheduled_end = scheduled_end
        if habit.scheduled_start >= habit.scheduled_end:
            raise ValueError("Start time must be before end time")
        if recurrence is not None:
            habit.recurrence = recurrence
        if color is not None:
            habit.color = color

        self.session.add(habit)
        self.session.commit()
        self.session.refresh(habit)
        logger.info("Hábito atualizado: id=%s", habit.id)
        return habit

    def delete_habit(self, habit_id: int) -> bool:
        """Arquiva hábito (soft delete — BR-HABIT-005).

        Marca archived_at sem destruir HabitInstance/TimeLog. Para hard
        delete administrativo, ver purge_habit (BR-HABIT-006). Reversível
        via restore_habit.
        """
        habit = self.session.get(Habit, habit_id)
        if not habit:
            return False

        if habit.archived_at is None:
            habit.archived_at = datetime.now()
        self.session.add(habit)
        self.session.commit()
        logger.info("Hábito arquivado: id=%s", habit_id)
        return True

    def restore_habit(self, habit_id: int) -> Habit | None:
        """Reverte o arquivamento de um hábito (BR-HABIT-006).

        Zera archived_at; o hábito volta às listagens padrão e a geração
        de instâncias futuras é retomada no próximo ciclo.
        """
        habit = self.session.get(Habit, habit_id)
        if not habit:
            return None

        habit.archived_at = None
        self.session.add(habit)
        self.session.commit()
        self.session.refresh(habit)
        logger.info("Hábito restaurado: id=%s", habit_id)
        return habit

    def purge_habit(self, habit_id: int) -> bool:
        """Hard delete permanente de hábito (BR-HABIT-006).

        Destrói o Habit, suas HabitInstance (via cascade ORM) e os TimeLog
        associados às instâncias. O cascade ORM de Habit.instances não
        alcança TimeLog, então estes são removidos explicitamente antes da
        deleção do Habit. Operação irreversível.
        """
        habit = self.session.get(Habit, habit_id)
        if not habit:
            return False

        instance_ids = [i.id for i in habit.instances if i.id is not None]
        if instance_ids:
            logs = self.session.exec(
                select(TimeLog).where(TimeLog.habit_instance_id.in_(instance_ids))  # type: ignore[union-attr]
            ).all()
            for log in logs:
                self.session.delete(log)

        self.session.delete(habit)
        self.session.commit()
        logger.info("Hábito purgado (hard delete): id=%s", habit_id)
        return True
