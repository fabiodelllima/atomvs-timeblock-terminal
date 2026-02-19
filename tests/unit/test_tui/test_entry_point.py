"""Tests for BR-TUI-001: Entry Point Detection."""

import sys
from unittest.mock import patch


class TestBRTUI001EntryPointDetection:
    """BR-TUI-001: timeblock sem argumentos abre TUI, com argumentos executa CLI."""

    def test_br_tui_001_no_args_launches_tui(self):
        """Sem argumentos, deve tentar importar e executar TimeBlockApp."""
        with (
            patch.object(sys, "argv", ["timeblock"]),
            patch("timeblock.main.launch_tui", return_value=True) as mock_tui,
        ):
            from timeblock.main import main

            main()
            mock_tui.assert_called_once()

    def test_br_tui_001_with_args_runs_cli(self):
        """Com argumentos, deve executar CLI normalmente."""
        with (
            patch.object(sys, "argv", ["timeblock", "routine", "list"]),
            patch("timeblock.main.app") as mock_app,
        ):
            from timeblock.main import main

            main()
            mock_app.assert_called_once()

    def test_br_tui_001_tui_import_error_shows_warning(self, capsys):
        """Se textual não instalado, exibe warning e instrução de instalação."""
        with (
            patch.object(sys, "argv", ["timeblock"]),
            patch(
                "timeblock.main.launch_tui",
                side_effect=ImportError("No module named 'textual'"),
            ),
        ):
            from timeblock.main import main

            main()
            captured = capsys.readouterr()
            assert "[WARN]" in captured.out
            assert "textual" in captured.out

    def test_br_tui_001_help_flag_runs_cli(self):
        """--help é argumento, deve executar CLI."""
        with (
            patch.object(sys, "argv", ["timeblock", "--help"]),
            patch("timeblock.main.app") as mock_app,
        ):
            from timeblock.main import main

            main()
            mock_app.assert_called_once()
