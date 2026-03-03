"""Testes para BR-DATA-001: Backup Automático do Banco de Dados."""

from pathlib import Path
from unittest.mock import patch

from timeblock.services.backup_service import (
    MAX_BACKUPS,
    _cleanup_old_backups,
    create_backup,
    get_backup_dir,
    list_backups,
    restore_backup,
)


class TestBRData001BackupAutomatico:
    """BR-DATA-001: Backup automático do SQLite."""

    def test_br_data_001_backup_created_with_timestamp(self, tmp_path: Path) -> None:
        """Backup criado com timestamp no nome."""
        db_file = tmp_path / "timeblock.db"
        db_file.write_text("test data")
        with patch("timeblock.services.backup_service.get_db_path", return_value=str(db_file)):
            with patch(
                "timeblock.services.backup_service.get_backup_dir",
                return_value=tmp_path / "backups",
            ):
                result = create_backup(label="startup")
        assert result is not None
        assert "timeblock-" in result.name
        assert "-startup.db" in result.name

    def test_br_data_001_label_in_filename(self, tmp_path: Path) -> None:
        """Label aparece no nome do arquivo."""
        db_file = tmp_path / "timeblock.db"
        db_file.write_text("test data")
        with patch("timeblock.services.backup_service.get_db_path", return_value=str(db_file)):
            with patch(
                "timeblock.services.backup_service.get_backup_dir",
                return_value=tmp_path / "backups",
            ):
                result = create_backup(label="shutdown")
        assert result is not None
        assert "-shutdown.db" in result.name

    def test_br_data_001_rotation_removes_old(self, tmp_path: Path) -> None:
        """Rotação remove backups excedentes."""
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        for i in range(MAX_BACKUPS + 3):
            (backup_dir / f"timeblock-2026010{i:02d}-120000.db").write_text(f"backup {i}")
        _cleanup_old_backups(backup_dir)
        remaining = list(backup_dir.glob("timeblock-*.db"))
        assert len(remaining) == MAX_BACKUPS

    def test_br_data_001_missing_db_returns_none(self, tmp_path: Path) -> None:
        """Banco inexistente retorna None sem erro."""
        with patch(
            "timeblock.services.backup_service.get_db_path",
            return_value=str(tmp_path / "missing.db"),
        ):
            result = create_backup()
        assert result is None

    def test_br_data_001_restore_creates_pre_restore(self, tmp_path: Path) -> None:
        """Restore cria pre-restore antes de sobrescrever."""
        db_file = tmp_path / "timeblock.db"
        db_file.write_text("current data")
        backup_file = tmp_path / "backup.db"
        backup_file.write_text("old data")
        backup_dir = tmp_path / "backups"
        with patch("timeblock.services.backup_service.get_db_path", return_value=str(db_file)):
            with patch("timeblock.services.backup_service.get_backup_dir", return_value=backup_dir):
                result = restore_backup(backup_file)
        assert result is True
        pre_restores = list(backup_dir.glob("*pre-restore*"))
        assert len(pre_restores) == 1

    def test_br_data_001_list_backups_ordered(self, tmp_path: Path) -> None:
        """list_backups retorna ordenado por data (mais recente primeiro)."""
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        import time

        for name in ["timeblock-20260101-100000.db", "timeblock-20260102-100000.db"]:
            (backup_dir / name).write_text("data")
            time.sleep(0.05)
        with patch("timeblock.services.backup_service.get_backup_dir", return_value=backup_dir):
            backups = list_backups()
        assert "20260102" in backups[0].name

    def test_br_data_001_backup_dir_created(self, tmp_path: Path) -> None:
        """Diretório de backups criado automaticamente."""
        db_file = tmp_path / "data" / "timeblock.db"
        db_file.parent.mkdir()
        db_file.write_text("test")
        with patch("timeblock.services.backup_service.get_db_path", return_value=str(db_file)):
            backup_dir = get_backup_dir()
        assert backup_dir.exists()
        assert backup_dir.name == "backups"

    def test_br_data_001_max_backups_respected(self, tmp_path: Path) -> None:
        """MAX_BACKUPS é respeitado após múltiplos backups."""
        db_file = tmp_path / "timeblock.db"
        db_file.write_text("test data")
        backup_dir = tmp_path / "backups"
        with patch("timeblock.services.backup_service.get_db_path", return_value=str(db_file)):
            with patch("timeblock.services.backup_service.get_backup_dir", return_value=backup_dir):
                for i in range(MAX_BACKUPS + 5):
                    create_backup(label=f"test{i}")
        remaining = list(backup_dir.glob("timeblock-*.db"))
        assert len(remaining) <= MAX_BACKUPS
