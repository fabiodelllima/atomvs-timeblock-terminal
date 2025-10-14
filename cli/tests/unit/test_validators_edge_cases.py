"""Tests for validator edge cases."""

import pytest
from datetime import datetime
from datetime import timezone as tz
from src.timeblock.utils.validators import validate_time_range


def test_validate_duration_less_than_one_minute():
    """Should raise error for events shorter than 1 minute (line 75)."""
    now = datetime.now(tz.utc)
    # 30 seconds duration
    start = now
    end = now.replace(second=30)
    
    with pytest.raises(ValueError, match="at least 1 minute long"):
        validate_time_range(start, end)


def test_validate_normal_case_valid():
    """Should pass for normal valid time range."""
    now = datetime.now(tz.utc)
    start = now
    end = now.replace(hour=now.hour + 1)
    
    # Should not raise
    validate_time_range(start, end)
