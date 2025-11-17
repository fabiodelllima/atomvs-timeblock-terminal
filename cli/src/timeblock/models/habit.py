"""Habit model."""

from datetime import time
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from sqlmodel import Field, Relationship, SQLModel

from .habit_instance import HabitInstance
from .routine import Routine

if TYPE_CHECKING:
    from .tag import Tag


class Recurrence(Enum):
    """Padrões de recorrência."""

    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    WEEKDAYS = "WEEKDAYS"
    WEEKENDS = "WEEKENDS"
    EVERYDAY = "EVERYDAY"


class Habit(SQLModel, table=True):
    """Evento recorrente da rotina."""

    __tablename__ = "habits"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    routine_id: int = Field(
        foreign_key="routines.id",
        ondelete="RESTRICT",  # BR-ROUTINE-002: Bloqueia delete com habits
    )
    title: str = Field(max_length=200)
    scheduled_start: time
    scheduled_end: time
    recurrence: Recurrence
    color: str | None = Field(default=None, max_length=7)
    tag_id: int | None = Field(default=None, foreign_key="tags.id")

    # Relationships
    routine: Routine | None = Relationship(back_populates="habits")
    instances: list[HabitInstance] = Relationship(back_populates="habit", cascade_delete=True)
    tag: Optional["Tag"] = Relationship(back_populates="habits")

    def __init__(self, **data: Any):
        """Valida recurrence antes de criar instância."""
        if "recurrence" in data:
            recurrence = data["recurrence"]

            if isinstance(recurrence, Recurrence):
                pass  # Já está correto

            elif isinstance(recurrence, str):
                valid_names = {r.name for r in Recurrence}
                if recurrence not in valid_names:
                    raise ValueError(
                        f"Invalid recurrence pattern '{recurrence}'. "
                        f"Must be one of: {sorted(valid_names)}"
                    )
                data["recurrence"] = Recurrence[recurrence]

            else:
                raise ValueError(
                    f"Invalid recurrence type: {type(recurrence).__name__}. "
                    f"Expected Recurrence enum or string."
                )

        super().__init__(**data)
