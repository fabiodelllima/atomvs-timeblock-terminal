"""Data models for TimeBlock application."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class EventStatus(str, Enum):
    """Event lifecycle status."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Event(SQLModel, table=True):
    """Time-blocked event with scheduling information."""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    # Optional color for visual organization (hex format: #RRGGBB)
    color: Optional[str] = Field(default=None, max_length=7)
    status: EventStatus = Field(default=EventStatus.PLANNED)
    # Scheduled time window
    scheduled_start: datetime = Field(index=True)
    scheduled_end: datetime
    # Audit timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TimeLog(SQLModel, table=True):
    """Actual execution time record for an event."""

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", index=True)
    # Actual execution timeframe
    actual_start: datetime
    actual_end: Optional[datetime] = Field(default=None)
    # Accumulated pause time in seconds
    paused_duration: int = Field(default=0)
    # Audit timestamp
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PauseLog(SQLModel, table=True):
    """Individual pause intervals for time tracking."""

    id: Optional[int] = Field(default=None, primary_key=True)
    timelog_id: int = Field(foreign_key="timelog.id", index=True)
    # Pause interval
    pause_start: datetime
    pause_end: Optional[datetime] = Field(default=None)
    # Audit timestamp
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChangeType(str, Enum):
    """Types of changes for audit logging."""

    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    RESCHEDULED = "rescheduled"
    DELETED = "deleted"


class ChangeLog(SQLModel, table=True):
    """Audit trail for event modifications."""

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", index=True)
    change_type: ChangeType
    field_name: Optional[str] = Field(default=None, max_length=50)
    old_value: Optional[str] = Field(default=None, max_length=500)
    new_value: Optional[str] = Field(default=None, max_length=500)
    # Audit timestamp (indexed for chronological queries)
    changed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )
