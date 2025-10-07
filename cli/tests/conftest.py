"""Global pytest configuration."""

import pytest


@pytest.fixture(autouse=True)
def isolate_tests(tmp_path, monkeypatch):
    """Isolate each test using temporary database.

    This fixture runs automatically before each test,
    ensuring tests don't interfere with each other.
    """
    # Create path for temporary database
    db_path = tmp_path / "test_timeblock.db"

    # Override environment variable
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
