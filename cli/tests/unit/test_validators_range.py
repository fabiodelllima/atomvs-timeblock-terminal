"""Tests for time range validation."""

import pytest
from datetime import datetime, timezone, timedelta

from src.timeblock.utils.validators import validate_time_range


class TestValidateTimeRange:
    """Tests for validate_time_range function."""

    def test_valid_range(self):
        """Should accept valid time range."""
        start = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        # Should not raise
        validate_time_range(start, end)

    def test_valid_range_small_gap(self):
        """Should accept range with small gap."""
        start = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        end = start + timedelta(minutes=1)
        # Should not raise
        validate_time_range(start, end)

    def test_invalid_same_time(self):
        """Should raise ValueError when start == end."""
        time = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match="End time must be after start time"):
            validate_time_range(time, time)

    def test_invalid_end_before_start(self):
        """Should raise ValueError when end < start."""
        start = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match="End time must be after start time"):
            validate_time_range(start, end)

    def test_invalid_end_one_second_before(self):
        """Should raise ValueError even for 1 second difference."""
        start = datetime(2025, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 8, 59, 59, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match="End time must be after start time"):
            validate_time_range(start, end)
