"""Testes unitários para timer/display.py.

Testa helpers internos de formatação.
"""

from timeblock.commands.timer.display import format_duration


class TestFormatDuration:
    """Testes para format_duration."""

    def test_zero_seconds(self):
        """Zero segundos."""
        assert format_duration(0) == (0, 0, 0)

    def test_seconds_only(self):
        """Apenas segundos."""
        assert format_duration(45) == (0, 0, 45)

    def test_minutes_and_seconds(self):
        """Minutos e segundos."""
        assert format_duration(125) == (0, 2, 5)

    def test_hours_minutes_seconds(self):
        """Horas, minutos e segundos."""
        assert format_duration(3665) == (1, 1, 5)

    def test_exact_hour(self):
        """Hora exata."""
        assert format_duration(3600) == (1, 0, 0)

    def test_large_duration(self):
        """Duração grande (8h30m15s)."""
        assert format_duration(30615) == (8, 30, 15)
