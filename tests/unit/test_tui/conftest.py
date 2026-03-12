"""Fixtures específicas para testes da TUI.

Isola a suíte da TUI do banco de dados real do desenvolvedor,
garantindo que testes rodem com estado limpo independente do
ambiente local.

Referências:
    - BR-TEST-001: Isolamento de testes
    - ADR-033: Session-scoped fixtures
"""

import os

import pytest


@pytest.fixture(autouse=True, scope="session")
def _isolate_tui_database():
    """Força banco em memória para todos os testes TUI.

    Sem este isolamento, testes que verificam estado vazio
    (e.g. e/x sem rotina ativa) falham quando o banco local
    do desenvolvedor contém dados pré-existentes.
    """
    original = os.environ.get("TIMEBLOCK_DB_PATH")
    os.environ["TIMEBLOCK_DB_PATH"] = ":memory:"
    yield
    if original is None:
        os.environ.pop("TIMEBLOCK_DB_PATH", None)
    else:
        os.environ["TIMEBLOCK_DB_PATH"] = original
