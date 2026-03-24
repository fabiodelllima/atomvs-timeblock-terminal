"""Task model (ADR-036: Task Lifecycle Evolution)."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .tag import Tag


class Task(SQLModel, table=True):
    """Tarefa pontual com lifecycle rastreável.

    Status derivado de timestamps (BR-TASK-007):
      1. cancelled_datetime is not None → CANCELLED
      2. completed_datetime is not None → COMPLETED
      3. scheduled_datetime < now()     → OVERDUE
      4. else                           → PENDING
    """

    __tablename__ = "tasks"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=200)
    scheduled_datetime: datetime = Field(index=True)
    original_scheduled_datetime: datetime = Field(index=False)
    completed_datetime: datetime | None = Field(default=None)
    cancelled_datetime: datetime | None = Field(default=None)
    postponement_count: int = Field(default=0)
    description: str | None = Field(default=None)
    color: str | None = Field(default=None)
    tag_id: int | None = Field(default=None, foreign_key="tags.id")

    # Relationships
    tag: Optional["Tag"] = Relationship(back_populates="tasks")

    @property
    def derived_status(self) -> str:
        """Deriva status a partir de timestamps (BR-TASK-007).

        Ordem de precedência fixa: cancelamento prevalece sobre tudo.
        """
        if self.cancelled_datetime is not None:
            return "cancelled"
        if self.completed_datetime is not None:
            return "completed"
        if self.scheduled_datetime < datetime.now():
            return "overdue"
        return "pending"
