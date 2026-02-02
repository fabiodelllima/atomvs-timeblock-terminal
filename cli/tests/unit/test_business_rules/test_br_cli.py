"""Testes para Business Rules de CLI.

Valida BRs:
- BR-CLI-001: Validação de Flags Dependentes
"""

import pytest

from timeblock.commands.habit.atom import _validate_log_mode


class TestBRCli001:
    """Valida BR-CLI-001: Flags dependentes requerem par completo."""

    def test_br_cli_001_start_without_end_raises(self):
        """BR-CLI-001: --start sem --end lança erro."""
        with pytest.raises(ValueError, match="--start requer --end"):
            _validate_log_mode(start="09:00", end=None, duration=None)

    def test_br_cli_001_end_without_start_raises(self):
        """BR-CLI-001: --end sem --start lança erro."""
        with pytest.raises(ValueError, match="--start requer --end"):
            _validate_log_mode(start=None, end="10:00", duration=None)

    def test_br_cli_001_start_end_together_valid(self):
        """BR-CLI-001: --start com --end juntos é válido."""
        # Não deve lançar exceção
        _validate_log_mode(start="09:00", end="10:00", duration=None)

    def test_br_cli_001_start_end_with_duration_raises(self):
        """BR-CLI-001: --start/--end com --duration é inválido."""
        with pytest.raises(ValueError, match="--start/--end com --duration"):
            _validate_log_mode(start="09:00", end="10:00", duration=30)

    def test_br_cli_001_no_flags_raises(self):
        """BR-CLI-001: Nenhuma flag de tempo lança erro."""
        with pytest.raises(ValueError, match=r"--start/--end.*--duration"):
            _validate_log_mode(start=None, end=None, duration=None)

    def test_br_cli_001_duration_only_valid(self):
        """BR-CLI-001: --duration sozinho é válido."""
        _validate_log_mode(start=None, end=None, duration=30)
