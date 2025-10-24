"""Tests for EventReorderingService propose_reordering."""
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Event, EventStatus
from src.timeblock.services.event_reordering_models import Conflict, ConflictType, EventPriority
from src.timeblock.services.event_reordering_service import EventReorderingService


@pytest.fixture
def test_engine():
    """Engine SQLite em memória."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(test_engine):
    """Session fixture."""
    with Session(test_engine) as session:
        yield session


class TestProposeReordering:
    """Tests for propose_reordering."""

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_empty_conflicts(self, mock_context, test_engine):
        """Returns empty proposal for no conflicts."""
        mock_context.return_value.__enter__.return_value = test_engine
        
        proposal = EventReorderingService.propose_reordering([])
        assert len(proposal.conflicts) == 0
        assert len(proposal.proposed_changes) == 0
        assert proposal.estimated_duration_shift == 0

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_critical_events_dont_move(self, mock_context, test_engine, session):
        """CRITICAL priority events are not rescheduled."""
        mock_context.return_value.__enter__.return_value = test_engine
        
        event1 = Event(
            title="Event 1",
            status=EventStatus.IN_PROGRESS,  # CRITICAL
            scheduled_start=datetime(2025, 10, 24, 10, 0),
            scheduled_end=datetime(2025, 10, 24, 11, 0),
        )
        event2 = Event(
            title="Event 2",
            status=EventStatus.PLANNED,  # LOW
            scheduled_start=datetime(2025, 10, 24, 10, 30),
            scheduled_end=datetime(2025, 10, 24, 11, 30),
        )
        session.add_all([event1, event2])
        session.commit()
        session.refresh(event1)
        session.refresh(event2)
        
        conflicts = [
            Conflict(
                triggered_event_id=event1.id,
                triggered_event_type="event",
                conflicting_event_id=event2.id,
                conflicting_event_type="event",
                conflict_type=ConflictType.OVERLAP,
                triggered_start=datetime(2025, 10, 24, 10, 0),
                triggered_end=datetime(2025, 10, 24, 11, 0),
                conflicting_start=datetime(2025, 10, 24, 10, 30),
                conflicting_end=datetime(2025, 10, 24, 11, 30),
            )
        ]
        
        proposal = EventReorderingService.propose_reordering(conflicts)
        
        # Event1 (CRITICAL) não deve ter mudança
        critical_changes = [c for c in proposal.proposed_changes if c.event_id == event1.id]
        assert len(critical_changes) == 0
        
        # Event2 (LOW) deve ser movido para depois do event1
        low_changes = [c for c in proposal.proposed_changes if c.event_id == event2.id]
        assert len(low_changes) == 1
        assert low_changes[0].proposed_start == datetime(2025, 10, 24, 11, 0)

    @patch('src.timeblock.services.event_reordering_service.get_engine_context')
    def test_low_priority_stacks_sequentially(self, mock_context, test_engine, session):
        """Multiple LOW priority events stack after CRITICAL."""
        mock_context.return_value.__enter__.return_value = test_engine
        
        now = datetime(2025, 10, 24, 10, 0)
        event1 = Event(
            title="Critical",
            status=EventStatus.IN_PROGRESS,
            scheduled_start=now,
            scheduled_end=now + timedelta(hours=1),
        )
        event2 = Event(
            title="Low 1",
            status=EventStatus.PLANNED,
            scheduled_start=now + timedelta(hours=2),
            scheduled_end=now + timedelta(hours=3),
        )
        event3 = Event(
            title="Low 2",
            status=EventStatus.PLANNED,
            scheduled_start=now + timedelta(hours=2, minutes=30),
            scheduled_end=now + timedelta(hours=3, minutes=30),
        )
        session.add_all([event1, event2, event3])
        session.commit()
        for e in [event1, event2, event3]:
            session.refresh(e)
        
        conflicts = [
            Conflict(
                triggered_event_id=event1.id,
                triggered_event_type="event",
                conflicting_event_id=event2.id,
                conflicting_event_type="event",
                conflict_type=ConflictType.OVERLAP,
                triggered_start=now,
                triggered_end=now + timedelta(hours=1),
                conflicting_start=now + timedelta(hours=2),
                conflicting_end=now + timedelta(hours=3),
            ),
            Conflict(
                triggered_event_id=event2.id,
                triggered_event_type="event",
                conflicting_event_id=event3.id,
                conflicting_event_type="event",
                conflict_type=ConflictType.OVERLAP,
                triggered_start=now + timedelta(hours=2),
                triggered_end=now + timedelta(hours=3),
                conflicting_start=now + timedelta(hours=2, minutes=30),
                conflicting_end=now + timedelta(hours=3, minutes=30),
            )
        ]
        
        proposal = EventReorderingService.propose_reordering(conflicts)
        
        # Event2 deve começar após event1
        event2_change = [c for c in proposal.proposed_changes if c.event_id == event2.id][0]
        assert event2_change.proposed_start == now + timedelta(hours=1)
        
        # Event3 deve começar após event2
        event3_change = [c for c in proposal.proposed_changes if c.event_id == event3.id][0]
        assert event3_change.proposed_start == now + timedelta(hours=2)
