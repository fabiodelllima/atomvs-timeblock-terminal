"""Configuração global do pytest."""

import pytest


@pytest.fixture(autouse=True)
def isolate_tests(tmp_path, monkeypatch):
    """Isola cada teste usando banco de dados temporário.

    Esta fixture roda automaticamente antes de cada teste,
    garantindo que os testes não interferem uns nos outros.
    """
    # Criar caminho para banco temporário
    db_path = tmp_path / "test_timeblock.db"

    # Sobrescrever variável de ambiente
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
