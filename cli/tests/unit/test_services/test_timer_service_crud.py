"""Testes CRUD para TimerService seguindo ADR-007."""

from datetime import datetime

from sqlmodel import Session

from timeblock.models import TimeLog
from timeblock.services.timer_service import TimerService


class TestTimerServiceGetTimelog:
    """ADR-007: get_timelog() pattern."""

    def test_get_timelog_returns_existing(self, session: Session):
        """ADR-007: get_timelog retorna TimeLog se existe."""
        # Arrange: criar timelog no banco
        timelog = TimeLog(
            habit_instance_id=None,
            start_time=datetime.now(),
            end_time=None,
        )
        session.add(timelog)
        session.commit()
        session.refresh(timelog)

        # Act: chamar método que não existe ainda
        service = TimerService()
        result = service.get_timelog(timelog.id, session)

        # Assert
        assert result is not None
        assert result.id == timelog.id

    def test_get_timelog_returns_none_if_not_exists(self, session: Session):
        """ADR-007: get_timelog retorna None se não existe."""
        # Act: chamar método que não existe ainda
        service = TimerService()
        result = service.get_timelog(999999, session)

        # Assert
        assert result is None
