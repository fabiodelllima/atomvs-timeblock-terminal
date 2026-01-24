"""Modelo TimeLog unificado para tracking de tempo."""

from datetime import datetime

from sqlmodel import Field, SQLModel

from timeblock.models.enums import TimerStatus


class TimeLog(SQLModel, table=True):
    """Registro de sessão de timer.

    Cada TimeLog representa uma sessão de tracking.
    Uma HabitInstance pode ter múltiplas sessões (BR-TIMER-004).
    """

    __tablename__ = "time_log"

    id: int | None = Field(default=None, primary_key=True)

    # Foreign keys opcionais (apenas um preenchido por registro)
    event_id: int | None = Field(foreign_key="event.id", default=None, index=True)
    task_id: int | None = Field(foreign_key="tasks.id", default=None, index=True)
    habit_instance_id: int | None = Field(foreign_key="habitinstance.id", default=None, index=True)

    # Estado do timer (BR-TIMER-002)
    status: TimerStatus | None = Field(default=TimerStatus.RUNNING, index=True)
    pause_start: datetime | None = Field(default=None)

    # Timestamps
    start_time: datetime
    end_time: datetime | None = None

    # Durações
    duration_seconds: int | None = None
    paused_duration: int | None = Field(default=0)

    # Anotações e cancelamento
    notes: str | None = Field(default=None, max_length=500)
    cancel_reason: str | None = Field(default=None, max_length=500)
