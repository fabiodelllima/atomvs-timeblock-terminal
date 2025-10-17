"""Tests for main CLI commands."""

from typer.testing import CliRunner

from src.timeblock.main import app


def test_version_command():
    """Should display version information."""
    runner = CliRunner()
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "TimeBlock v" in result.output
    assert "0.1.0" in result.output
