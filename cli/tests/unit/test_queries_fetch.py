"""Tests for fetch_events functions."""

from datetime import UTC, timedelta

from sqlmodel import Session

from src.timeblock.database import create_db_and_tables, get_engine
from src.timeblock.utils.queries import (
    build_events_query,
    fetch_events,
    fetch_events_in_range,
)


class TestFetchEvents:
    """Tests for fetch_events function."""

    def test_fetch_all_events(self, test_db, sample_events):
        """Should fetch all events when no filters."""
        with Session(test_db) as session:
            query = build_events_query()
            results = fetch_events(session, query)
            assert len(results) == 5

    def test_fetch_empty_database(self, test_db):
        """Should return empty list when database is empty."""
        create_db_and_tables()
        # test_db já cria engine e tabelas
        engine = get_engine()
        with Session(engine) as session:
            query = build_events_query()
            results = fetch_events(session, query)
            assert len(results) == 0


class TestFetchEventsInRange:
    """Tests for fetch_events_in_range convenience function."""

    def test_fetch_with_start(self, test_db, sample_events, now_time):
        """Should fetch events from start date."""
        with Session(test_db) as session:
            results = fetch_events_in_range(session, start=now_time)

            assert len(results) == 3
            assert all(
                e.scheduled_start.replace(tzinfo=UTC) >= now_time for e in results
            )

    def test_fetch_with_end(self, test_db, sample_events, now_time):
        """Should fetch events up to end date."""
        with Session(test_db) as session:
            results = fetch_events_in_range(session, end=now_time)

            assert len(results) == 3
            assert all(
                e.scheduled_start.replace(tzinfo=UTC) <= now_time for e in results
            )

    def test_fetch_with_range(self, test_db, sample_events, now_time):
        """Should fetch events within date range."""
        with Session(test_db) as session:
            start = now_time - timedelta(days=1)
            end = now_time + timedelta(days=1)
            results = fetch_events_in_range(session, start=start, end=end)

            assert len(results) == 3

    def test_fetch_with_ascending(self, test_db, sample_events):
        """Should respect ascending parameter."""
        with Session(test_db) as session:
            results = fetch_events_in_range(session, ascending=True)

            assert len(results) == 5
            assert results[0].title == "Event 1"
            assert results[-1].title == "Event 5"

    def test_fetch_empty_range(self, test_db, sample_events, now_time):
        """Should return empty list when no events in range."""
        with Session(test_db) as session:
            start = now_time + timedelta(days=100)
            end = now_time + timedelta(days=200)
            results = fetch_events_in_range(session, start=start, end=end)

            assert len(results) == 0

    def test_fetch_no_filters(self, test_db, sample_events):
        """Should fetch all events when no filters provided."""
        with Session(test_db) as session:
            results = fetch_events_in_range(session)
            assert len(results) == 5
