"""Testes para open_skip_modal e SKIP_REASON_OPTIONS (BR-TUI-024, DT-039).

Validates:
    - BR-TUI-024: Modal de skip com Select de SkipReason e nota opcional
    - DT-039: open_skip_modal implementation
"""

from timeblock.models.enums import SkipReason
from timeblock.tui.screens.dashboard.crud_habits import SKIP_REASON_OPTIONS


class TestBRTui024SkipReasonOptions:
    """BR-TUI-024: SKIP_REASON_OPTIONS tem 8 opções válidas."""

    def test_br_tui_024_options_has_all_reasons(self) -> None:
        """SKIP_REASON_OPTIONS contém exatamente 8 opções válidas."""
        assert len(SKIP_REASON_OPTIONS) == 8

        # Each key should be a valid SkipReason member name
        for key, _label in SKIP_REASON_OPTIONS:
            # Access by name should not raise
            _ = SkipReason[key]

    def test_br_tui_024_enum_access_patterns(self) -> None:
        """SkipReason suporta acesso por NAME e VALUE."""
        # Access by NAME (used in SKIP_REASON_OPTIONS)
        health_by_name = SkipReason["HEALTH"]
        assert health_by_name == SkipReason.HEALTH

        # Access by VALUE (Portuguese string)
        health_by_value = SkipReason("saude")
        assert health_by_value == SkipReason.HEALTH

        # Both should be the same enum member
        assert health_by_name is health_by_value
