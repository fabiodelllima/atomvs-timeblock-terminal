"""Testes da BR-TUI-034 — Hints contextuais no footer global.

Valida o helper _format_hint e o mapa PANEL_KEYBINDINGS do StatusBar
contra as regras documentadas na BR-TUI-034 (br-tui.md).

Estes testes existem para validar a BR contra regressão futura. Não são
auto-referentes ao código: cada um aponta uma cláusula específica da BR
e falha quando a implementação diverge dessa cláusula.

Referências:
    - BR-TUI-034 em docs/reference/business-rules/br-tui.md
    - DT-074 (anti-padrão de testes auto-referentes — evitado aqui)
    - Issues #29, #32, #44 (gatilhos da BR)
"""

import pytest

from timeblock.tui.colors import C_INFO, C_SUBTEXT1
from timeblock.tui.widgets.status_bar import (
    DEFAULT_KEYBINDINGS,
    PANEL_KEYBINDINGS,
    _format_hint,
)


class TestBRTUI034FormatHint:
    """Valida o helper _format_hint contra as regras 3-8 da BR-TUI-034."""

    @pytest.mark.skip(
        reason="Aguarda adaptação de BR-TUI-034 e teste após redesign de hints na v1.7.2 — ref issue #53"
    )
    def test_br_tui_034_format_single_key(self) -> None:
        """Regra 3: hint `[q] sair` parsa para markup com tecla em C_INFO.

        Regra 6: tecla recebe C_INFO. Regra 7: descrição recebe C_SUBTEXT1.
        Regra 8: sem [dim] envolvendo o todo.
        """
        result = _format_hint("[q] sair")
        # Tecla com colchetes literais escapados em C_INFO
        assert f"[{C_INFO}]\\[q\\][/{C_INFO}]" in result
        # Descrição em C_SUBTEXT1
        assert f"[{C_SUBTEXT1}] sair[/{C_SUBTEXT1}]" in result
        # Garantia: sem [dim] envolvendo
        assert "[dim]" not in result

    @pytest.mark.skip(
        reason="Aguarda adaptação de BR-TUI-034 e teste após redesign de hints na v1.7.2 — ref issue #53"
    )
    def test_br_tui_034_format_multiple_keys(self) -> None:
        """Regra 4: múltiplos hints separados por dois espaços produzem N pares.

        Hint com 4 keys deve gerar 4 substrings de C_INFO e 4 de C_SUBTEXT1.
        """
        hint = "[v] done  [s] skip  [t] timer  [u] undo"
        result = _format_hint(hint)
        # Conta ocorrências da abertura de tag C_INFO (uma por tecla)
        assert result.count(f"[{C_INFO}]\\[") == 4
        # Conta ocorrências da abertura de tag C_SUBTEXT1 (uma por descrição)
        assert result.count(f"[{C_SUBTEXT1}]") == 4

    @pytest.mark.skip(
        reason="Aguarda adaptação de BR-TUI-034 e teste após redesign de hints na v1.7.2 — ref issue #53"
    )
    def test_br_tui_034_format_multichar_key(self) -> None:
        """Regra 5: combinações de teclas como [Ctrl+Q] são válidas.

        O parser deve capturar `Ctrl+Q` inteiro entre os colchetes,
        sem interpretar o `+` como separador.
        """
        result = _format_hint("[Ctrl+Q] sair")
        assert f"[{C_INFO}]\\[Ctrl+Q\\][/{C_INFO}]" in result
        assert f"[{C_SUBTEXT1}] sair[/{C_SUBTEXT1}]" in result

    @pytest.mark.skip(
        reason="Aguarda adaptação de BR-TUI-034 e teste após redesign de hints na v1.7.2 — ref issue #53"
    )
    def test_br_tui_034_format_arrow_key(self) -> None:
        """Regra 5: setas Unicode `[↑↓]` são válidas como tecla.

        O parser deve aceitar caracteres não-ASCII dentro dos colchetes.
        """
        result = _format_hint("[↑↓] navegar")
        assert f"[{C_INFO}]\\[↑↓\\][/{C_INFO}]" in result
        assert f"[{C_SUBTEXT1}] navegar[/{C_SUBTEXT1}]" in result

    def test_br_tui_034_format_empty_returns_empty(self) -> None:
        """Helper retorna string vazia para entrada vazia (defensivo)."""
        assert _format_hint("") == ""


class TestBRTUI034PanelKeybindings:
    """Valida o mapa PANEL_KEYBINDINGS contra as regras 9-12 da BR-TUI-034."""

    def test_br_tui_034_panel_keybindings_all_panels_covered(self) -> None:
        """Regra 12: todos os IDs de panel registrados têm entrada no mapa.

        Os 5 panels do dashboard devem estar presentes em PANEL_KEYBINDINGS.
        Adicionar um panel novo sem registrar seu hint quebra este teste.
        """
        expected_panels = {
            "agenda-content",
            "panel-habits",
            "panel-tasks",
            "panel-timer",
            "panel-metrics",
        }
        assert expected_panels.issubset(PANEL_KEYBINDINGS.keys()), (
            f"Panels faltando em PANEL_KEYBINDINGS: {expected_panels - PANEL_KEYBINDINGS.keys()}"
        )

    def test_br_tui_034_default_keybindings_when_unknown_panel(self) -> None:
        """Regra 11: panel_id desconhecido cai no DEFAULT_KEYBINDINGS.

        DEFAULT_KEYBINDINGS deve cobrir ações globais (Tab, ajuda, sair)
        e seguir o mesmo formato `[tecla] descrição` da regra 3.
        """
        # DEFAULT existe e não é vazio
        assert DEFAULT_KEYBINDINGS
        # Segue o formato [tecla] descrição (tem ao menos um par de colchetes)
        assert "[" in DEFAULT_KEYBINDINGS and "]" in DEFAULT_KEYBINDINGS
        # Cobre ação de saída (regra implícita: usuário sempre tem como sair)
        assert "Ctrl+Q" in DEFAULT_KEYBINDINGS or "q" in DEFAULT_KEYBINDINGS.lower()
        # Validação extra: passa pelo helper sem erro
        formatted = _format_hint(DEFAULT_KEYBINDINGS)
        assert formatted  # não-vazio
        assert C_INFO in formatted
        assert C_SUBTEXT1 in formatted
