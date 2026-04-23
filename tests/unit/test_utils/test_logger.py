"""Testes para módulo de logging estruturado (DT-022).

Referências:
    - DT-022: Logging estruturado
    - ADR-019: Test Naming Convention
"""

import json
import logging
import os
import tempfile
from pathlib import Path

import pytest

from timeblock.utils.logger import (
    _reset_for_testing,
    configure_logging,
    disable_logging,
    enable_logging,
    get_logger,
)


@pytest.fixture(autouse=True)
def _reset_logging():
    """Reseta estado do logging entre cada teste."""
    _reset_for_testing()
    yield
    _reset_for_testing()
    enable_logging()


class TestConfigureLogging:
    """Testa configure_logging() com diferentes parâmetros."""

    def test_configure_console_only(self):
        """Console habilitado, arquivo desabilitado."""
        configure_logging(console=True, log_file=False)
        root = logging.getLogger("timeblock")
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0], logging.StreamHandler)

    def test_configure_file_only(self):
        """Arquivo habilitado, console desabilitado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(log_path)
            try:
                configure_logging(console=False, log_file=True)
                root = logging.getLogger("timeblock")
                assert len(root.handlers) == 1
                assert log_path.parent.exists()
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)

    def test_configure_dual(self):
        """Console e arquivo habilitados simultaneamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(log_path)
            try:
                configure_logging(console=True, log_file=True)
                root = logging.getLogger("timeblock")
                assert len(root.handlers) == 2
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)

    def test_configure_idempotent(self):
        """Segunda chamada não altera configuração."""
        configure_logging(console=True, log_file=False)
        root = logging.getLogger("timeblock")
        handler_count = len(root.handlers)
        configure_logging(console=True, log_file=True)
        assert len(root.handlers) == handler_count

    def test_configure_level_from_env(self):
        """Nível lido de ATOMVS_LOG_LEVEL."""
        os.environ["ATOMVS_LOG_LEVEL"] = "DEBUG"
        try:
            configure_logging(log_file=False)
            root = logging.getLogger("timeblock")
            assert root.level == logging.DEBUG
        finally:
            os.environ.pop("ATOMVS_LOG_LEVEL", None)

    def test_configure_level_parameter(self):
        """Parâmetro level tem prioridade sobre default."""
        configure_logging(level="WARNING", log_file=False)
        root = logging.getLogger("timeblock")
        assert root.level == logging.WARNING


class TestGetLogger:
    """Testa get_logger() e namespace hierárquico."""

    def test_get_logger_returns_child(self):
        """Logger retornado é filho do namespace timeblock."""
        logger = get_logger("timeblock.services.timer")
        assert logger.name == "timeblock.services.timer"

    def test_get_logger_auto_configures(self):
        """get_logger sem configure_logging prévio configura defaults."""
        logger = get_logger("timeblock.test.auto")
        assert logger is not None
        root = logging.getLogger("timeblock")
        assert len(root.handlers) > 0

    def test_get_logger_inherits_level(self):
        """Logger filho herda nível do root timeblock."""
        configure_logging(level="DEBUG", log_file=False)
        logger = get_logger("timeblock.services.test")
        assert logger.getEffectiveLevel() == logging.DEBUG


class TestJsonFormat:
    """Testa formato JSON Lines no arquivo."""

    def test_json_lines_format(self):
        """Cada linha do arquivo é JSON válido."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(log_path)
            try:
                configure_logging(console=False, log_file=True)
                logger = get_logger("timeblock.test.json")
                logger.info("Mensagem de teste")

                for handler in logging.getLogger("timeblock").handlers:
                    handler.flush()

                content = log_path.read_text().strip()
                record = json.loads(content)
                assert record["message"] == "Mensagem de teste"
                assert record["levelname"] == "INFO"
                assert "asctime" in record
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)

    def test_json_extra_fields(self):
        """Campos extra são incluídos no JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(log_path)
            try:
                configure_logging(console=False, log_file=True)
                logger = get_logger("timeblock.test.extra")
                logger.info("Operação", extra={"habit_id": 42})

                for handler in logging.getLogger("timeblock").handlers:
                    handler.flush()

                content = log_path.read_text().strip()
                record = json.loads(content)
                assert record["habit_id"] == 42
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)


class TestLogRotation:
    """Testa rotação automática de arquivos."""

    def test_rotation_creates_backup(self):
        """Rotação cria backups ao atingir max_bytes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(log_path)
            try:
                configure_logging(
                    console=False,
                    log_file=True,
                    max_bytes=100,
                    backup_count=2,
                )
                logger = get_logger("timeblock.test.rotation")
                for i in range(50):
                    logger.info(f"Mensagem de teste número {i} com texto extra")

                backups = list(Path(tmpdir).glob("test.jsonl.*"))
                assert len(backups) > 0
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)


class TestDisableEnableLogging:
    """Testa desabilitar/habilitar logs globalmente."""

    def test_disable_suppresses_output(self):
        """disable_logging suprime todas as mensagens."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(log_path)
            try:
                configure_logging(console=False, log_file=True)
                logger = get_logger("timeblock.test.disable")
                disable_logging()
                logger.error("Mensagem suprimida")

                for handler in logging.getLogger("timeblock").handlers:
                    handler.flush()

                if log_path.exists():
                    assert log_path.read_text().strip() == ""
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)
                enable_logging()

    def test_enable_restores_output(self):
        """enable_logging restaura mensagens após disable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(log_path)
            try:
                configure_logging(console=False, log_file=True)
                logger = get_logger("timeblock.test.enable")
                disable_logging()
                logger.info("Suprimida")
                enable_logging()
                logger.info("Visível")

                for handler in logging.getLogger("timeblock").handlers:
                    handler.flush()

                content = log_path.read_text()
                assert "Suprimida" not in content
                assert "Visível" in content
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)


class TestXDGPaths:
    """Testa resolução de caminhos XDG."""

    def test_xdg_data_home_respected(self):
        """XDG_DATA_HOME é usado quando definido."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["XDG_DATA_HOME"] = tmpdir
            os.environ.pop("ATOMVS_LOG_FILE", None)
            try:
                configure_logging(console=False, log_file=True)
                expected = Path(tmpdir) / "atomvs" / "logs" / "atomvs.jsonl"
                assert expected.parent.exists()
            finally:
                os.environ.pop("XDG_DATA_HOME", None)

    def test_atomvs_log_file_overrides_xdg(self):
        """ATOMVS_LOG_FILE tem prioridade sobre XDG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = Path(tmpdir) / "custom.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(custom_path)
            os.environ["XDG_DATA_HOME"] = "/should/not/be/used"
            try:
                configure_logging(console=False, log_file=True)
                logger = get_logger("timeblock.test.override")
                logger.info("test")

                for handler in logging.getLogger("timeblock").handlers:
                    handler.flush()

                assert custom_path.exists()
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)
                os.environ.pop("XDG_DATA_HOME", None)


class TestBROBS001NoStderrLeak:
    """Testa BR-OBS-001: TUI nunca emite para stderr via logging.

    Referências:
        - BR-OBS-001 regra 11: "stdout/stderr: NADA durante execução da TUI"
        - BR-OBS-001 regra 12: "Nunca logging para console handler durante TUI"
        - BR-OBS-001 tabela: TUI | Console (stderr) = Desabilitado
        - Issue #48: logs vazam para stderr quebrando layout Textual
    """

    def test_br_obs_001_tui_no_stdout(self):
        """get_logger em tempo de import não deve vazar stderr no modo TUI.

        Cenário do bug #48: módulos do projeto chamam get_logger() em tempo
        de import (padrão `logger = get_logger(__name__)` no topo dos arquivos).
        Essas chamadas ocorrem antes de main() rodar configure_logging(console=False)
        porque main.py importa commands no topo e cada command instancia logger.

        Se get_logger auto-configura com console=True como side-effect, o
        StreamHandler(stderr) persiste quando main() chama configure_logging,
        porque a função é idempotente (retorna cedo se _configured).

        BR-OBS-001 exige zero console handlers durante TUI. Este teste
        garante que a sequência "import precoce → configure TUI" resulta
        em zero StreamHandler (excluindo FileHandler) no logger timeblock.

        A checagem é por tipo de handler, não por stream específico, porque
        BR-OBS-001 regra 12 veta "console handler" de forma abstrata. Também
        evita acoplamento ao pytest capture fd-level, que substitui sys.stderr
        por FileIO durante testes.

        Nota: RotatingFileHandler herda de FileHandler que herda de
        StreamHandler. A exclusão explícita de FileHandler previne falso
        positivo quando log_file=True.
        """
        # Simula chamada em tempo de import (antes do entrypoint configurar)
        _early_logger = get_logger("timeblock.commands.tag")
        assert _early_logger is not None

        # Entrypoint TUI chama configure_logging com console desabilitado
        configure_logging(console=False, log_file=False)

        # BR-OBS-001 regra 11/12: nenhum console handler ativo no modo TUI.
        # RotatingFileHandler herda de StreamHandler via FileHandler; exclusão
        # explícita de FileHandler evita falso positivo em modo dual.
        root = logging.getLogger("timeblock")
        console_handlers = [
            h
            for h in root.handlers
            if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        ]
        assert console_handlers == [], (
            f"BR-OBS-001 violada: console handler ativo no modo TUI. "
            f"Handlers encontrados: {console_handlers}. "
            f"Streams: {[getattr(h, 'stream', None) for h in console_handlers]}"
        )
