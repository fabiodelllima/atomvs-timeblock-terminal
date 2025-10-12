"""Tests for time range validation."""

from datetime import datetime, timedelta, timezone

import pytest

from src.timeblock.utils.validators import validate_time_range


class TestValidateTimeRange:
    """Test validate_time_range function."""

    def test_valid_range(self):
        """Should accept valid time range."""
        start = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        validate_time_range(start, end)  # Should not raise

    def test_valid_range_small_gap(self):
        """Should accept range with 1 minute gap."""
        start = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 9, 1, tzinfo=timezone.utc)
        validate_time_range(start, end)  # Should not raise

    def test_same_time_valid_crossing_midnight(self):
        """Same time treated as crossing midnight (valid)."""
        time = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        validate_time_range(time, time)  # Should not raise (crossing midnight)

    def test_end_before_start_valid_crossing_midnight(self):
        """End before start treated as crossing midnight (valid)."""
        start = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        validate_time_range(start, end)  # Should not raise (crossing midnight)

    def test_end_one_second_before_valid(self):
        """End 1 second before start treated as crossing midnight (valid)."""
        start = datetime(2025, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
        end = start - timedelta(seconds=1)
        validate_time_range(start, end)  # Should not raise (crossing midnight)
