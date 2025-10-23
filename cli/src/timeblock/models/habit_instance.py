"""HabitInstance model for concrete habit occurrences."""

from datetime import date as date_type
from datetime import datetime, time
from enum import Enum

from sqlmodel import Field, SQLModel


class HabitInstanceStatus(str, Enum):
    """Status de instância de hábito."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class HabitInstance(SQLModel, table=True):
    """Instância concreta de habit em dia específico."""

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habit.id")
    date: date_type = Field(index=True)
    scheduled_start: time
    scheduled_end: time
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    status: HabitInstanceStatus = Field(default=HabitInstanceStatus.PLANNED)
    manually_adjusted: bool = Field(default=False)
    user_override: bool = Field(default=False)
