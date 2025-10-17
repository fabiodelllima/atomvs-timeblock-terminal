"""Fixtures específicas para integration tests."""

import pytest
from sqlmodel import SQLModel, create_engine


@pytest.fixture
def isolated_db(monkeypatch, tmp_path):
    """Create isolated test database for each test."""
    test_db_path = tmp_path / "test_integration.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(test_db_path))
    
    # Create engine and tables
    db_url = f"sqlite:///{test_db_path}"
    engine = create_engine(db_url, echo=False)
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    engine.dispose()


@pytest.fixture
def runner():
    """CLI test runner."""
    from typer.testing import CliRunner
    return CliRunner()
