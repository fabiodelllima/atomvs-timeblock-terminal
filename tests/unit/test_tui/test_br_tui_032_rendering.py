"""Testes unitários de renderização da agenda (BR-TUI-032).

Testa funções puras extraídas via Humble Object pattern.
Cada teste valida uma regra específica de BR-TUI-032
usando instâncias mock sem dependência de Textual.

Referências:
    - BR-TUI-032: Renderização de Blocos de Tempo na Agenda
    - HUMBLE; FARLEY, 2010, p. 179 (Humble Object Pattern)
"""

from datetime import datetime

import pytest

from timeblock.tui.widgets.agenda_renderer import (
    build_agenda_content,
    compute_agenda_range,
)

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def now() -> datetime:
    """Hora fixa para testes — 12:00, longe dos blocos de teste."""
    return datetime(2026, 3, 23, 12, 0, 0)


@pytest.fixture
def block_10_11() -> dict:
    """Bloco pendente de 10:00 a 11:00 (60min)."""
    return {
        "name": "Leitura",
        "start_minutes": 600,
        "end_minutes": 660,
        "status": "pending",
        "substatus": None,
    }


@pytest.fixture
def block_11_12() -> dict:
    """Bloco done de 11:00 a 12:00 (60min) — consecutivo ao anterior."""
    return {
        "name": "Treino",
        "start_minutes": 660,
        "end_minutes": 720,
        "status": "done",
        "substatus": "FULL",
    }


@pytest.fixture
def three_overlapping() -> list[dict]:
    """3 blocos sobrepostos para teste de multi-coluna."""
    return [
        {
            "name": "Leitura",
            "start_minutes": 600,
            "end_minutes": 690,
            "status": "pending",
            "substatus": None,
        },
        {
            "name": "Treino",
            "start_minutes": 630,
            "end_minutes": 780,
            "status": "done",
            "substatus": "FULL",
        },
        {
            "name": "Meditação",
            "start_minutes": 660,
            "end_minutes": 750,
            "status": "running",
            "substatus": None,
        },
    ]


def _line_index(line_number: int, instances: list[dict]) -> int:
    """Converte número de linha de 15min para índice em blocks_out."""
    range_start, _ = compute_agenda_range(instances)
    line_start = range_start * 2
    return line_number - line_start


# ============================================================
# Testes BR-TUI-032
# ============================================================


class TestBRTUI032:
    """Valida regras de renderização de blocos de tempo."""

    def test_br_tui_032_block_first_line_title_icon(
        self,
        block_10_11: dict,
        now: datetime,
    ):
        """BR-TUI-032-R4: Primeira linha tem ícone + título em C_TEXT, sem accent bar."""
        instances = [block_10_11]
        _, blocks, _ = build_agenda_content(instances, now=now)

        # 10:00 = 600min / 15 = line 40
        idx = _line_index(40, instances)
        first_line = blocks[idx]

        # NÃO deve conter accent bar ▌ (removida na v1.7.2)
        assert "\u258c" not in first_line, "Accent bar deveria ter sido removida"
        # Deve conter o nome do hábito
        assert "Leitura" in first_line, "Nome ausente na linha de título"
        # Deve conter o ícone de pending (○)
        assert "\u25cb" in first_line, "Ícone de pending ausente"
        # Deve conter C_TEXT (branco) para o título
        assert "#CDD6F4" in first_line, "C_TEXT ausente — título deveria ser branco"
        # NÃO deve conter fill chars (░)
        assert "\u2591" not in first_line, "Fill char presente na linha de título"

    def test_br_tui_032_block_body_accent_bar_color(
        self,
        block_10_11: dict,
        now: datetime,
    ):
        """BR-TUI-032-R5: Linhas de corpo têm · dim + fill na cor do status."""
        instances = [block_10_11]
        _, blocks, _ = build_agenda_content(instances, now=now)

        # 10:15 = line 41, 10:30 = line 42, 10:45 = line 43
        for line_num in [41, 42, 43]:
            idx = _line_index(line_num, instances)
            body_line = blocks[idx]

            # Sem accent bar (removida v1.7.2)
            assert "\u258c" not in body_line, f"Accent bar na linha {line_num}"
            # Prefixo · em dim
            assert "[dim]\u00b7[/dim]" in body_line, (
                f"Prefixo \u00b7 dim ausente na linha {line_num}"
            )
            # Fill char presente
            assert "\u2591" in body_line, f"Fill char ausente na linha {line_num}"
            # Cor de pending (#89B4FA) deve estar no markup
            assert "#89B4FA" in body_line, f"Cor de pending ausente na linha {line_num}"

    def test_br_tui_032_no_horizontal_lines_through_blocks(
        self,
        block_10_11: dict,
        now: datetime,
    ):
        """BR-TUI-032-R8: Nenhuma linha horizontal atravessa um bloco."""
        instances = [block_10_11]
        _, blocks, _ = build_agenda_content(instances, now=now)

        # Verificar linhas do bloco (10:00 a 11:00 = lines 40-44)
        for line_num in range(40, 45):
            idx = _line_index(line_num, instances)
            line = blocks[idx]
            assert "\u2500\u253c\u2500" not in line, f"─┼─ encontrado na linha {line_num}"
            assert "\u2500\u252c\u2500" not in line, f"─┬─ encontrado na linha {line_num}"
            # ─── dentro de bloco (3+ hífens consecutivos)
            assert "\u2500\u2500\u2500" not in line, f"─── encontrado na linha {line_num}"

    def test_br_tui_032_end_time_line_has_color(
        self,
        block_10_11: dict,
        now: datetime,
    ):
        """BR-TUI-032-R9: Linha do horário de término ainda exibe fill."""
        instances = [block_10_11]
        _, blocks, _ = build_agenda_content(instances, now=now)

        # 11:00 = 660min / 15 = line 44 (R9: end line com fill)
        idx = _line_index(44, instances)
        end_line = blocks[idx]

        # Sem accent bar (removida v1.7.2)
        assert "\u258c" not in end_line, "Accent bar deveria ter sido removida"
        # Prefixo · em dim (mesmo formato do corpo)
        assert "[dim]\u00b7[/dim]" in end_line, "Prefixo \u00b7 dim ausente na end line"
        # Fill char presente (R9: ainda exibe cor)
        assert "\u2591" in end_line, "Fill char ausente na end line (R9)"
        # Cor presente
        assert "#89B4FA" in end_line, "Cor ausente na end line"

    def test_br_tui_032_consecutive_blocks_no_gap(
        self,
        block_10_11: dict,
        block_11_12: dict,
        now: datetime,
    ):
        """BR-TUI-032-R11: Bloco consecutivo substitui corpo do anterior."""
        instances = [block_10_11, block_11_12]
        _, blocks, _ = build_agenda_content(instances, now=now)

        # 11:00 = line 44 — deve ter TÍTULO do segundo bloco, não corpo do primeiro
        idx = _line_index(44, instances)
        transition_line = blocks[idx]

        # Título do segundo bloco
        assert "Treino" in transition_line, (
            "Título do bloco consecutivo ausente na linha de transição"
        )
        # NÃO deve ter fill do primeiro bloco (cor pending #89B4FA com ░)
        # Pode ter accent bar do novo bloco (cor done #A6E3A1)
        assert "#A6E3A1" in transition_line, "Cor do bloco done ausente — deveria ser o novo bloco"

    def test_br_tui_032_minimum_column_width_18(
        self,
        three_overlapping: list[dict],
        now: datetime,
    ):
        """BR-TUI-032-R12: Largura mínima por coluna é 18 caracteres."""
        _, _blocks, content_width = build_agenda_content(
            three_overlapping,
            now=now,
        )

        # 3 colunas * 18 + 2 gaps + 1 = 57 mínimo
        assert content_width >= 3 * 18 + 2, (
            f"Largura total {content_width} insuficiente para 3 colunas de 18"
        )

    def test_br_tui_032_empty_area_is_empty(self, block_10_11: dict, now: datetime):
        """BR-TUI-032-R16: Áreas sem bloco são string vazia."""
        instances = [block_10_11]
        _, blocks, _ = build_agenda_content(instances, now=now)

        # 09:00 = line 36 — antes do bloco, deve ser vazio
        idx = _line_index(36, instances)
        empty_line = blocks[idx]

        assert empty_line == "", f"Área vazia não é string vazia: {empty_line!r}"

    def test_br_tui_032_granularity_15min(self, block_10_11: dict, now: datetime):
        """BR-TUI-032-R1/R2: Exatamente 4 linhas entre 10:00 e 11:00."""
        instances = [block_10_11]
        hours, _, _ = build_agenda_content(instances, now=now)

        # Encontrar índices das labels 10:00 e 11:00
        idx_10 = None
        idx_11 = None
        for i, h in enumerate(hours):
            if "10:00" in h:
                idx_10 = i
            elif "11:00" in h:
                idx_11 = i

        assert idx_10 is not None, "Label 10:00 não encontrado"
        assert idx_11 is not None, "Label 11:00 não encontrado"
        # 10:00, 10:15, 10:30, 10:45 = 4 linhas até 11:00
        assert idx_11 - idx_10 == 4, (
            f"Esperado 4 linhas entre 10:00 e 11:00, encontrado {idx_11 - idx_10}"
        )
