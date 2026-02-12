"""Service para gerenciamento de hábitos."""

from datetime import time

from sqlmodel import Session, select

from timeblock.models import Habit, Recurrence


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
        return habit

    def get_habit(self, habit_id: int) -> Habit | None:
        """Busca hábito por ID."""
        return self.session.get(Habit, habit_id)

    def list_habits(self, routine_id: int | None = None) -> list[Habit]:
        """Lista hábitos, opcionalmente filtrados por rotina."""
        statement = select(Habit)
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
        return habit

    def delete_habit(self, habit_id: int) -> bool:
        """Remove hábito."""
        habit = self.session.get(Habit, habit_id)
        if not habit:
            return False

        self.session.delete(habit)
        self.session.commit()
        return True
