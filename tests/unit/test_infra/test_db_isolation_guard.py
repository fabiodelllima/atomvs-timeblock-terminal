"""Teste-guarda de isolamento de banco (BR-TEST-003 / DT-078).

Garante que nenhum teste resolva o path do banco para o arquivo de
produção XDG. Falha de forma determinística se a guarda global de
isolamento (fixture autouse no conftest raiz) não estiver ativa.

Referências:
    - BR-TEST-003: Isolamento Absoluto do Banco de Produção
    - DT-078: Testes de integração sem guarda global de banco isolado
    - ADR-026: Test Database Isolation Strategy
"""

import os
from pathlib import Path

from timeblock.database.engine import get_db_path


class TestBRTest003DatabaseIsolation:
    """Valida que a suíte nunca toca o banco de produção XDG."""

    def _production_db_path(self) -> str:
        """Replica a resolução XDG de produção de get_db_path()."""
        xdg = os.getenv("XDG_DATA_HOME")
        base = Path(xdg) if xdg else Path.home() / ".local" / "share"
        return str(base / "atomvs" / "atomvs.db")

    def test_br_test_003_db_path_never_resolves_to_production(self):
        """get_db_path() não pode retornar o banco XDG de produção."""
        resolved = get_db_path()
        production = self._production_db_path()
        assert resolved != production, (
            f"get_db_path() resolveu para o banco de produção ({resolved}). "
            "A guarda global de isolamento (BR-TEST-003) não está ativa."
        )

    def test_br_test_003_env_var_is_set_during_suite(self):
        """TIMEBLOCK_DB_PATH deve estar definido durante a suíte."""
        value = os.getenv("TIMEBLOCK_DB_PATH")
        assert value is not None, (
            "TIMEBLOCK_DB_PATH não está definido durante a suíte. "
            "A guarda global de isolamento (BR-TEST-003) não está ativa."
        )
