"""Tests for BR-TUI-003: Dashboard helpers e renderização.

Testes unitários para métodos auxiliares do DashboardScreen:
- _format_duration: formatação de duração para agenda (Xm / Xh / XhYY)
- _format_duration_card: formatação para card hábitos (01h30m / 00h30m)
- _find_block_at: localização de blocos em slots de 30min
- _block_style: estilos visuais por status/substatus (color-system.md)
- _status_color, _status_bg, _status_icon: mapeamento semântico
- _render_ascii_time: timer em ASCII art
- Mock data: carregamento sem erros
"""

import pytest

from timeblock.tui.colors import (
    BG_ACCENT,
    BG_MUTED,
    BG_SUCCESS,
    BG_WARNING,
    C_ABOVE,
    C_ACCENT,
    C_BELOW,
    C_ERROR,
    C_MUTED,
    C_OVERLIMIT,
    C_PASSIVE,
    C_SUBTEXT0,
    C_SUBTEXT1,
    C_SUCCESS,
    C_WARNING,
    fill_char,
    is_bold_status,
    status_bg,
    status_color,
    status_icon,
    task_proximity_color,
)
from timeblock.tui.formatters import (
    block_style,
    format_duration,
    format_duration_card,
    render_ascii_time,
    spaced_title,
)
from timeblock.tui.mock_data import MOCK_INSTANCES, MOCK_TASKS, MOCK_TIMER
from timeblock.tui.widgets.agenda_panel import AgendaPanel


class TestBRTUI003FormatDuration:
    """BR-TUI-003: Duração formatada para agenda (Xm < 60, Xh ou XhYY >= 60)."""

    def test_br_tui_003_format_duration_none_returns_empty(self):
        """None retorna string vazia."""
        assert format_duration(None) == ""

    def test_br_tui_003_format_duration_zero_returns_empty(self):
        """Zero retorna string vazia."""
        assert format_duration(0) == ""

    def test_br_tui_003_format_duration_under_60_shows_min(self):
        """Duração < 60 exibe como Xm."""
        assert format_duration(30) == "30m"
        assert format_duration(45) == "45m"
        assert format_duration(1) == "1m"
        assert format_duration(59) == "59m"

    def test_br_tui_003_format_duration_exact_hour_shows_h(self):
        """Duração em horas exatas exibe como Xh."""
        assert format_duration(60) == "1h"
        assert format_duration(120) == "2h"
        assert format_duration(180) == "3h"

    def test_br_tui_003_format_duration_hour_plus_minutes_shows_hyy(self):
        """Duração com horas e minutos exibe como XhYY."""
        assert format_duration(90) == "1h30"
        assert format_duration(115) == "1h55"
        assert format_duration(145) == "2h25"
        assert format_duration(61) == "1h01"


class TestBRTUI003FormatDurationCard:
    """BR-TUI-003: Duração formatada para card hábitos (01h30m zero-padded)."""

    def test_br_tui_003_format_duration_card_none_returns_empty(self):
        """None retorna string vazia."""
        assert format_duration_card(None) == ""

    def test_br_tui_003_format_duration_card_zero_returns_empty(self):
        """Zero retorna string vazia."""
        assert format_duration_card(0) == ""

    def test_br_tui_003_format_duration_card_under_60_zero_padded(self):
        """Duração < 60 exibe como 00hXXm."""
        assert format_duration_card(30) == "00h30m"
        assert format_duration_card(45) == "00h45m"
        assert format_duration_card(5) == "00h05m"

    def test_br_tui_003_format_duration_card_exact_hour(self):
        """Duração em horas exatas exibe como XXh00m."""
        assert format_duration_card(60) == "01h00m"
        assert format_duration_card(120) == "02h00m"

    def test_br_tui_003_format_duration_card_hour_plus_minutes(self):
        """Duração com horas e minutos exibe como XXhYYm."""
        assert format_duration_card(90) == "01h30m"
        assert format_duration_card(75) == "01h15m"
        assert format_duration_card(145) == "02h25m"


class TestBRTUI003FindBlockAt:
    """BR-TUI-003: Localização de blocos em slots de 30min."""

    def setup_method(self):
        """Instâncias mock para testes."""
        self.instances = [
            {"name": "Meditação", "start_hour": 6, "end_hour": 7},
            {"name": "Deep Work", "start_hour": 9, "end_hour": 11},
            {"name": "Almoço", "start_hour": 12, "end_hour": 13},
        ]

    def test_br_tui_003_find_block_at_start(self):
        """Encontra bloco no slot de início."""
        block = AgendaPanel.find_block_at(self.instances, 6, 0)
        assert block is not None
        assert block["name"] == "Meditação"

    def test_br_tui_003_find_block_at_middle(self):
        """Encontra bloco no meio (slot intermediário)."""
        block = AgendaPanel.find_block_at(self.instances, 6, 30)
        assert block is not None
        assert block["name"] == "Meditação"

    def test_br_tui_003_find_block_at_multi_hour(self):
        """Encontra bloco de múltiplas horas em qualquer slot."""
        for hour, minute in [(9, 0), (9, 30), (10, 0), (10, 30)]:
            block = AgendaPanel.find_block_at(self.instances, hour, minute)
            assert block is not None, f"Deveria encontrar bloco em {hour}:{minute:02d}"
            assert block["name"] == "Deep Work"

    def test_br_tui_003_find_block_at_end_exclusive(self):
        """Não encontra bloco no horário de fim (exclusivo)."""
        block = AgendaPanel.find_block_at(self.instances, 7, 0)
        assert block is None

    def test_br_tui_003_find_block_at_empty_slot(self):
        """Retorna None em slot sem bloco."""
        block = AgendaPanel.find_block_at(self.instances, 8, 0)
        assert block is None

    def test_br_tui_003_find_block_at_empty_list(self):
        """Retorna None com lista vazia."""
        block = AgendaPanel.find_block_at([], 6, 0)
        assert block is None

    def test_br_tui_003_find_block_default_minute(self):
        """Minuto padrão é 0 quando não especificado."""
        block = AgendaPanel.find_block_at(self.instances, 12)
        assert block is not None
        assert block["name"] == "Almoço"


class TestBRTUI003StatusColor:
    """BR-TUI-003/color-system.md: Mapeamento status → cor semântica."""

    @pytest.mark.parametrize(
        "status,substatus,expected_color",
        [
            ("done", None, C_SUCCESS),
            ("done", "full", C_SUCCESS),
            ("done", "partial", C_BELOW),
            ("done", "overdone", C_ABOVE),
            ("done", "excessive", C_OVERLIMIT),
            ("not_done", None, C_ERROR),
            ("not_done", "justified", C_WARNING),
            ("not_done", "unjustified", C_ERROR),
            ("not_done", "ignored", C_PASSIVE),
            ("running", None, C_ACCENT),
            ("paused", None, C_WARNING),
            ("pending", None, C_MUTED),
        ],
    )
    def test_br_tui_003_status_color_mapping(self, status, substatus, expected_color):
        """Cada status/substatus mapeia para cor color-system.md correta."""
        assert status_color(status, substatus) == expected_color


class TestBRTUI003StatusBg:
    """BR-TUI-003/color-system.md: Background colors a 15% opacity."""

    @pytest.mark.parametrize(
        "status,substatus,expected_bg",
        [
            ("done", None, BG_SUCCESS),
            ("running", None, BG_ACCENT),
            ("paused", None, BG_WARNING),
            ("pending", None, BG_MUTED),
        ],
    )
    def test_br_tui_003_status_bg_mapping(self, status, substatus, expected_bg):
        """Cada status tem background a 15% correto."""
        assert status_bg(status, substatus) == expected_bg


class TestBRTUI003StatusIcon:
    """BR-TUI-003/color-system.md: Mapeamento status → ícone."""

    @pytest.mark.parametrize(
        "status,substatus,expected_icon",
        [
            ("done", None, "✓"),
            ("done", "full", "✓"),
            ("done", "partial", "✓~"),
            ("done", "overdone", "✓+"),
            ("done", "excessive", "✓!"),
            ("not_done", "justified", "!"),
            ("not_done", "unjustified", "✗!"),
            ("not_done", "ignored", "✗?"),
            ("running", None, "▶"),
            ("paused", None, "⏸"),
            ("pending", None, "·"),
        ],
    )
    def test_br_tui_003_status_icon_mapping(self, status, substatus, expected_icon):
        """Cada status/substatus tem ícone color-system.md correto."""
        assert status_icon(status, substatus) == expected_icon


class TestBRTUI003BoldStatus:
    """BR-TUI-003/color-system.md: Bold exclusivo em running e paused."""

    @pytest.mark.parametrize(
        "status,expected_bold",
        [
            ("done", False),
            ("not_done", False),
            ("running", True),
            ("paused", True),
            ("pending", False),
        ],
    )
    def test_br_tui_003_bold_only_running_paused(self, status, expected_bold):
        """Bold é exclusivo de running e paused."""
        assert is_bold_status(status) == expected_bold


class TestBRTUI003FillChar:
    """BR-TUI-003/color-system.md: Caractere de preenchimento por status."""

    @pytest.mark.parametrize(
        "status,expected_char",
        [
            ("done", "░"),
            ("not_done", "┄"),
            ("running", "▓"),
            ("paused", "▒"),
            ("pending", "░"),
        ],
    )
    def test_br_tui_003_fill_char_by_status(self, status, expected_char):
        """Cada status usa caractere de preenchimento apropriado."""
        assert fill_char(status) == expected_char


class TestBRTUI003BlockStyle:
    """BR-TUI-003: _block_style compat (fill + indicator)."""

    @pytest.mark.parametrize(
        "status,substatus,expected_indicator",
        [
            ("done", None, "✓ done"),
            ("done", "partial", "✓~ partial"),
            ("done", "overdone", "✓+ overdone"),
            ("done", "excessive", "✓! excessive"),
            ("not_done", "justified", "! justified"),
            ("not_done", "unjustified", "✗! unjustified"),
            ("not_done", "ignored", "✗? ignored"),
            ("running", None, "▶ running"),
            ("paused", None, "⏸ paused"),
            ("pending", None, "· pending"),
        ],
    )
    def test_br_tui_003_block_style_indicators(self, status, substatus, expected_indicator):
        """Cada status/substatus tem indicador visual correto."""
        _fill, indicator = block_style(status, substatus)
        assert expected_indicator in indicator

    @pytest.mark.parametrize(
        "status,substatus,expected_color",
        [
            ("done", None, C_SUCCESS),
            ("done", "partial", C_BELOW),
            ("done", "overdone", C_ABOVE),
            ("done", "excessive", C_OVERLIMIT),
            ("not_done", "unjustified", C_ERROR),
            ("not_done", "ignored", C_PASSIVE),
            ("running", None, C_ACCENT),
            ("paused", None, C_WARNING),
            ("pending", None, C_MUTED),
        ],
    )
    def test_br_tui_003_block_style_colors(self, status, substatus, expected_color):
        """Cada status/substatus usa cor color-system.md no fill."""
        fill, _indicator = block_style(status, substatus)
        assert expected_color in fill

    def test_br_tui_003_block_style_has_background(self):
        """Fill contém 'on' para background color."""
        fill, _ = block_style("done")
        assert " on " in fill

    def test_br_tui_003_block_style_bold_in_running(self):
        """Running indicator contém bold."""
        _fill, indicator = block_style("running")
        assert "bold" in indicator

    def test_br_tui_003_block_style_bold_in_paused(self):
        """Paused indicator contém bold."""
        _fill, indicator = block_style("paused")
        assert "bold" in indicator

    def test_br_tui_003_block_style_no_bold_in_done(self):
        """Done indicator não contém bold."""
        _fill, indicator = block_style("done")
        assert "bold" not in indicator


class TestBRTUI003TaskProximityColor:
    """BR-TUI-003/color-system.md: Heat de proximidade para tasks."""

    @pytest.mark.parametrize(
        "days,expected_color",
        [
            (0, C_WARNING),
            (1, C_OVERLIMIT),
            (2, C_ABOVE),
            (3, C_ABOVE),
            (4, C_BELOW),
            (7, C_BELOW),
            (8, C_SUBTEXT1),
            (14, C_SUBTEXT1),
            (15, C_SUBTEXT0),
            (29, C_MUTED),
            (61, C_MUTED),
            (None, C_MUTED),
        ],
    )
    def test_br_tui_003task_proximity_color(self, days, expected_color):
        """Proximidade mapeia para cor correta no heat de 7 faixas."""
        assert task_proximity_color(days) == expected_color


class TestBRTUI003AsciiTimer:
    """BR-TUI-003: Renderização de timer em ASCII art."""

    def test_br_tui_003_ascii_time_returns_3_lines(self):
        """ASCII art sempre retorna exatamente 3 linhas."""
        result = render_ascii_time("47:23")
        assert len(result) == 3

    def test_br_tui_003_ascii_time_contains_digits(self):
        """Cada linha contém caracteres de bloco."""
        result = render_ascii_time("00:00")
        for line in result:
            assert len(line) > 0

    def test_br_tui_003_ascii_time_colon_in_middle(self):
        """Linha do meio contém separador de dois pontos."""
        result = render_ascii_time("12:34")
        assert "·" in result[1]


class TestBRTUI003MockData:
    """BR-TUI-003: Mock data carrega sem erros e exercita todos os status."""

    def test_br_tui_003_mock_instances_structure(self):
        """Mock instances têm campos obrigatórios."""
        required_keys = {
            "name",
            "start_hour",
            "end_hour",
            "status",
            "substatus",
            "actual_minutes",
        }
        for inst in MOCK_INSTANCES:
            assert required_keys.issubset(inst.keys()), f"Campos faltando em {inst['name']}"

    def test_br_tui_003_mock_instances_valid_hours(self):
        """Horários dos mocks são válidos (0-23, start < end)."""
        for inst in MOCK_INSTANCES:
            assert 0 <= inst["start_hour"] < 24
            assert 0 < inst["end_hour"] <= 24
            assert inst["start_hour"] < inst["end_hour"]

    def test_br_tui_003_mock_instances_valid_status(self):
        """Status dos mocks são valores válidos."""
        valid = {"done", "not_done", "pending", "running", "paused"}
        for inst in MOCK_INSTANCES:
            assert inst["status"] in valid, f"Status inválido: {inst['status']}"

    def test_br_tui_003_mock_instances_no_overlap(self):
        """Mock instances não têm sobreposição (BR-REORDER-001)."""
        sorted_inst = sorted(MOCK_INSTANCES, key=lambda x: x["start_hour"])
        for i in range(len(sorted_inst) - 1):
            assert sorted_inst[i]["end_hour"] <= sorted_inst[i + 1]["start_hour"], (
                f"Sobreposição: {sorted_inst[i]['name']} e {sorted_inst[i + 1]['name']}"
            )

    def test_br_tui_003_mock_instances_covers_all_main_status(self):
        """Mock data exercita todos os status principais."""
        statuses = {inst["status"] for inst in MOCK_INSTANCES}
        assert statuses == {"done", "not_done", "pending", "running", "paused"}

    def test_br_tui_003_mock_instances_covers_done_substatus(self):
        """Mock data exercita substatus DONE (full, partial, overdone, excessive)."""
        done_subs = {inst.get("substatus") for inst in MOCK_INSTANCES if inst["status"] == "done"}
        assert done_subs == {"full", "partial", "overdone", "excessive"}

    def test_br_tui_003_mock_instances_covers_not_done_substatus(self):
        """Mock data exercita substatus NOT_DONE (unjustified, ignored)."""
        nd_subs = {inst.get("substatus") for inst in MOCK_INSTANCES if inst["status"] == "not_done"}
        assert {"unjustified", "ignored"}.issubset(nd_subs)

    def test_br_tui_003_mock_tasks_covers_all_status(self):
        """Mock tasks exercita todos os status."""
        statuses = {t["status"] for t in MOCK_TASKS}
        assert statuses == {"pending", "completed", "cancelled", "overdue"}

    def test_br_tui_003_mock_tasks_not_empty(self):
        """Lista de tasks mock não é vazia."""
        assert len(MOCK_TASKS) > 0

    def test_br_tui_003_mock_timer_structure(self):
        """Timer mock tem campos obrigatórios."""
        assert "elapsed" in MOCK_TIMER
        assert "name" in MOCK_TIMER
        assert "status" in MOCK_TIMER


class TestBRTUI003SpacedTitle:
    """BR-TUI-003: Formatação de títulos com space-between."""

    def test_br_tui_003_spaced_title_basic(self):
        """Título básico com separador de traços."""
        result = spaced_title("Hábitos", "4/8 50%")
        assert "Hábitos" in result
        assert "4/8 50%" in result
        assert "─" in result

    def test_br_tui_003_spaced_title_minimum_gap(self):
        """Título com textos longos mantém gap mínimo de 2."""
        result = spaced_title("A" * 40, "B" * 40, width=48)
        assert "A" * 40 in result and "B" * 40 in result
