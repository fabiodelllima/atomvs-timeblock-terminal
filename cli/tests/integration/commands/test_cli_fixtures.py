"""Valida fixtures de CLI."""
import pytest


def test_cli_runner_available(cli_runner):
    """Testa que CLI runner está disponível."""
    assert cli_runner is not None
    assert hasattr(cli_runner, 'invoke')
