"""Integration tests for add command - error scenarios."""

import pytest
from src.timeblock.main import app
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


class TestAddErrors:
    """Test error handling scenarios."""

    def test_add_invalid_time_format(self, isolated_db, runner):
        """Should reject invalid time format."""
        result = runner.invoke(
            app,
            ["add", "Meeting", "-s", "9am", "-e", "10am"],
        )
        assert result.exit_code == 1
        assert "Invalid time format" in result.stdout

    def test_add_start_after_end(self, isolated_db, runner):
        """Should reject when start time is after end time."""
        result = runner.invoke(
            app,
            ["add", "Meeting", "-s", "15:00", "-e", "14:00"],
        )
        assert result.exit_code == 1
        assert "End time must be after start time" in result.stdout

    def test_add_invalid_hex_color_format(self, isolated_db, runner):
        """Should reject invalid hex color format."""
        result = runner.invoke(
            app,
            [
                "add",
                "Meeting",
                "-s",
                "10:00",
                "-e",
                "11:00",
                "--color",
                "blue",
            ],
        )
        assert result.exit_code == 1
        assert "Invalid color format" in result.stdout

    def test_add_invalid_hex_color_length(self, isolated_db, runner):
        """Should reject hex color with wrong length."""
        result = runner.invoke(
            app,
            [
                "add",
                "Meeting",
                "-s",
                "10:00",
                "-e",
                "11:00",
                "--color",
                "#12345",
            ],
        )
        assert result.exit_code == 1
        assert "Invalid color format" in result.stdout
