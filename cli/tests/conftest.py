"""Global pytest configuration."""

import os
from pathlib import Path

import pytest
from src.timeblock.database import create_db_and_tables


@pytest.fixture(scope="session", autouse=True)
def backup_real_db():
    """Backup real database before tests, restore after."""
    real_db = Path("data/timeblock.db")
    backup = Path("data/timeblock.db.backup")
    # Backup if exists
    if real_db.exists():
        real_db.rename(backup)
    yield
    # Restore
    if backup.exists():
        if real_db.exists():
            real_db.unlink()
        backup.rename(real_db)


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create temporary test database with tables."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    create_db_and_tables()
    yield db_path
