"""Tests for build_events_query function."""

import pytest
from datetime import timedelta
from sqlmodel import Session

from src.timeblock.utils.queries import build_events_query
from .test_queries_fixtures import in_memory_db, now_time, sample_events


class TestBuildEventsQuery:
    """Tests for build_events_query function."""

    def test_query_default_descending(self, in_memory_db, sample_events):
        """Should order by scheduled_start descending by default."""
        with Session(in_memory_db) as session:
            query = build_events_query(ascending=False)
            results = list(session.exec(query))

            assert len(results) == 5
            assert results[0].title == "Event 5"
            assert results[-1].title == "Event 1"

    def test_query_ascending(self, in_memory_db, sample_events):
        """Should order by scheduled_start ascending when requested."""
        with Session(in_memory_db) as session:
            query = build_events_query(ascending=True)
            results = list(session.exec(query))

            assert len(results) == 5
            assert results[0].title == "Event 1"
            assert results[-1].title == "Event 5"

    def test_query_with_start_date(self, in_memory_db, sample_events, now_time):
        """Should filter events from start date."""
        with Session(in_memory_db) as session:
            query = build_events_query(start=now_time, ascending=True)
            results = list(session.exec(query))

            assert len(results) == 3
            assert results[0].title == "Event 3"
            assert results[1].title == "Event 4"
            assert results[2].title == "Event 5"

    def test_query_with_end_date(self, in_memory_db, sample_events, now_time):
        """Should filter events up to end date."""
        with Session(in_memory_db) as session:
            query = build_events_query(end=now_time, ascending=True)
            results = list(session.exec(query))

            assert len(results) == 3
            assert results[0].title == "Event 1"
            assert results[1].title == "Event 2"
            assert results[2].title == "Event 3"

    def test_query_with_date_range(self, in_memory_db, sample_events, now_time):
        """Should filter events within date range."""
        with Session(in_memory_db) as session:
            start = now_time - timedelta(days=1)
            end = now_time + timedelta(days=1)
            query = build_events_query(start=start, end=end, ascending=True)
            results = list(session.exec(query))

            assert len(results) == 3
            assert results[0].title == "Event 2"
            assert results[1].title == "Event 3"
            assert results[2].title == "Event 4"

    def test_query_no_results(self, in_memory_db, sample_events, now_time):
        """Should return empty list when no events match."""
        with Session(in_memory_db) as session:
            start = now_time - timedelta(days=365)
            end = now_time - timedelta(days=300)
            query = build_events_query(start=start, end=end)
            results = list(session.exec(query))

            assert len(results) == 0
