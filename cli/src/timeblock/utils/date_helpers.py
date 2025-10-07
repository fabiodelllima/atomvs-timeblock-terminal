"""Date and time manipulation utilities."""

import calendar
from datetime import datetime, timedelta, timezone
from typing import Optional


def get_week_bounds(week_offset: int = 0) -> tuple[datetime, datetime]:
    """Get start (Monday) and end (Sunday) of a week.

    Args:
        week_offset: 0 = current week, 1 = next week, -1 = last week, etc.

    Returns:
        Tuple of (start_datetime, end_datetime) in UTC
    """
    now = datetime.now(timezone.utc)

    # Find Monday of current week (weekday: 0=Monday, 6=Sunday)
    days_since_monday = now.weekday()
    current_week_monday = (now - timedelta(days=days_since_monday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Calculate target week
    target_week_monday = current_week_monday + timedelta(weeks=week_offset)
    target_week_sunday = target_week_monday + timedelta(
        days=6, hours=23, minutes=59, seconds=59
    )

    return target_week_monday, target_week_sunday


def get_month_bounds(
    month: int, year: Optional[int] = None
) -> tuple[datetime, datetime]:
    """Get start and end of a specific month.

    Args:
        month: Month number (1-12) or offset (+1, -1, etc)
        year: Year (defaults to current year)

    Returns:
        Tuple of (start_datetime, end_datetime) in UTC
    """
    now = datetime.now(timezone.utc)

    if year is None:
        year = now.year

    # Validate month
    if month < 1 or month > 12:
        raise ValueError(f"Month must be between 1 and 12, got {month}")

    # First day of month
    month_start = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)

    # Last day of month
    last_day = calendar.monthrange(year, month)[1]
    month_end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

    return month_start, month_end


def add_months(source_date: datetime, months: int) -> datetime:
    """Add months to a datetime, handling year wraparound correctly.

    Args:
        source_date: Starting datetime
        months: Number of months to add (can be negative)

    Returns:
        New datetime with months added
    """
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return source_date.replace(year=year, month=month, day=day)


def get_day_bounds(day_offset: int = 0) -> tuple[datetime, datetime]:
    """Get start and end of a specific day.

    Args:
        day_offset: 0 = today, 1 = tomorrow, -1 = yesterday, etc.

    Returns:
        Tuple of (start_datetime, end_datetime) in UTC
    """
    now = datetime.now(timezone.utc)
    target_day = (now + timedelta(days=day_offset)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    day_end = target_day.replace(hour=23, minute=59, second=59)

    return target_day, day_end


def parse_offset(value: str) -> int:
    """Parse offset string like '+1', '-2', '5' to integer.

    Args:
        value: String value (e.g., '+1', '-2', '5')

    Returns:
        Integer offset
    """
    # Remove leading '+' if present
    if value.startswith("+"):
        value = value[1:]
    return int(value)
