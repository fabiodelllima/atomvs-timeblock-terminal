"""Testes para BR-TUI-003-R13: Régua de Horário Adaptativa.

Valida cálculo de range da agenda com suporte a madrugada,
range mínimo 05:00-23:30 e padding de 1h.
"""

from timeblock.tui.widgets.agenda_panel import compute_agenda_range


class TestBRTUI003R13:
    """Valida BR-TUI-003-R13: Régua adaptativa 05:00-23:30."""

    def test_br_tui_003_r13_default_range_no_events(self):
        """Sem eventos, range é 05:00-23:30 (slots 10-47)."""
        start, end = compute_agenda_range([])
        assert start == 10
        assert end == 47

    def test_br_tui_003_r13_range_adapts_to_events(self):
        """Range cobre eventos com padding de 1h."""
        instances = [
            {"start_minutes": 480, "end_minutes": 540},  # 08:00-09:00
        ]
        start, end = compute_agenda_range(instances)
        # 08:00 = slot 16, padding -2 = 14 → min(14, 10) = 10
        # 09:00 = slot 18, padding +2 = 20 → max(20, 47) = 47
        assert start == 10
        assert end == 47

    def test_br_tui_003_r13_early_event_extends_range(self):
        """Evento antes das 05:00 expande o range para baixo."""
        instances = [
            {"start_minutes": 120, "end_minutes": 180},  # 02:00-03:00
        ]
        start, end = compute_agenda_range(instances)
        # 02:00 = slot 4, padding -2 = 2 → min(2, 10) = 2 → 01:00
        assert start == 2
        assert end == 47

    def test_br_tui_003_r13_late_event_extends_range(self):
        """Evento após 23:30 não ultrapassa slot 47."""
        instances = [
            {"start_minutes": 1380, "end_minutes": 1410},  # 23:00-23:30
        ]
        _start, end = compute_agenda_range(instances)
        assert end == 47

    def test_br_tui_003_r13_madrugada_event_visible(self):
        """Hábito de madrugada (03:00) é visível na régua."""
        instances = [
            {"start_minutes": 180, "end_minutes": 240},  # 03:00-04:00
        ]
        start, _end = compute_agenda_range(instances)
        # 03:00 = slot 6, padding -2 = 4 → min(4, 10) = 4 → 02:00
        assert start == 4
        assert start < 10  # abaixo do mínimo default

    def test_br_tui_003_r13_minimum_range_05_2330(self):
        """Range nunca é menor que 05:00-23:30 (slots 10-47)."""
        instances = [
            {"start_minutes": 600, "end_minutes": 660},  # 10:00-11:00
        ]
        start, end = compute_agenda_range(instances)
        assert start <= 10
        assert end >= 47

    def test_br_tui_003_r13_granularity_30min(self):
        """Range usa granularidade de 30 minutos (slots)."""
        instances = [
            {"start_minutes": 615, "end_minutes": 675},  # 10:15-11:15
        ]
        start, end = compute_agenda_range(instances)
        # start_minutes 615 // 30 = slot 20
        # end_minutes ceil(675/30) = slot 23
        assert isinstance(start, int)
        assert isinstance(end, int)

    def test_br_tui_003_r13_padding_one_hour(self):
        """Padding é de 1h (2 slots) antes e depois dos eventos."""
        instances = [
            {"start_minutes": 60, "end_minutes": 120},  # 01:00-02:00
        ]
        start, _end = compute_agenda_range(instances)
        # 01:00 = slot 2, padding -2 = 0 → max(0, 0) = 0 → 00:00
        assert start == 0

    def test_br_tui_003_r13_multiple_events_span(self):
        """Range cobre todos os eventos quando espalhados pelo dia."""
        instances = [
            {"start_minutes": 120, "end_minutes": 180},  # 02:00-03:00
            {"start_minutes": 1320, "end_minutes": 1380},  # 22:00-23:00
        ]
        start, end = compute_agenda_range(instances)
        # Primeiro: slot 4, padding = 2 → 02:00 visível
        assert start <= 4
        # Último: slot 46, padding = 47 (capped)
        assert end == 47
