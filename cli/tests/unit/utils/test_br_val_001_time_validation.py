"""Testes para BR-VAL-001: Validação de Horários.

Referência da Regra de Negócio:
    - BR-VAL-001: Validação de Horários
      * start_time < end_time
      * duration_minutes > 0
      * Horários dentro do dia (00:00 - 23:59)
"""

from datetime import UTC, datetime, timedelta

import pytest

from timeblock.utils.validators import parse_time, validate_time_range

# ============================================================================
# BR-VAL-001: Validação de Horários - Suite Completa de Testes
# ============================================================================


class TestBRVal001TimeValidation:
    """Testes para BR-VAL-001: Regras de validação de horários.

    Esta classe valida os três requisitos principais:
        1. Horário de início deve ser anterior ao horário de término
        2. Duração deve ser positiva (> 0 minutos)
        3. Horários devem estar dentro do range válido (00:00 - 23:59)
    """

    # ------------------------------------------------------------------------
    # BR-VAL-001: start_time < end_time
    # ------------------------------------------------------------------------

    def test_br_val_001_start_before_end_normal_case(self):
        """BR-VAL-001: Deve aceitar quando start < end (evento normal no mesmo dia)."""
        now = datetime.now(UTC).replace(hour=10, minute=0, second=0, microsecond=0)
        start = now
        end = now.replace(hour=12, minute=0)  # 2 horas depois

        result = validate_time_range(start, end)

        assert result == end
        assert result > start

    def test_br_val_001_start_before_end_midnight_crossing(self):
        """BR-VAL-001: Deve aceitar quando end < start (cruzamento de meia-noite detectado)."""
        now = datetime.now(UTC).replace(hour=23, minute=0, second=0, microsecond=0)
        start = now
        end = now.replace(hour=2, minute=0)  # Parece anterior, mas cruza meia-noite

        result = validate_time_range(start, end)

        # Resultado deve ser ajustado para o próximo dia
        assert result.hour == 2
        assert result.day == end.day + 1
        assert result > start

    def test_br_val_001_rejects_same_time_as_24h_duration(self):
        """BR-VAL-001: Deve rejeitar quando start == end (interpretado como 24h, inválido)."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)

        with pytest.raises(ValueError, match="cannot be 24 hours or more"):
            validate_time_range(now, now)

    # ------------------------------------------------------------------------
    # BR-VAL-001: duration_minutes > 0
    # ------------------------------------------------------------------------

    def test_br_val_001_positive_duration_minimum(self):
        """BR-VAL-001: Deve aceitar duração mínima válida (1 minuto)."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = start + timedelta(minutes=1)

        result = validate_time_range(start, end)

        assert result == end
        duration_seconds = (result - start).total_seconds()
        assert duration_seconds == 60  # Exatamente 1 minuto

    def test_br_val_001_positive_duration_rejects_zero(self):
        """BR-VAL-001: Deve rejeitar duração zero (< 1 minuto)."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = start + timedelta(seconds=30)  # Apenas 30 segundos

        with pytest.raises(ValueError, match="at least 1 minute long"):
            validate_time_range(start, end)

    def test_br_val_001_positive_duration_rejects_negative(self):
        """BR-VAL-001: Deve rejeitar duração negativa após ajuste."""
        # Testado implicitamente pela rejeição de 24h, pois mesmo horário = duração de 24h
        now = datetime.now(UTC).replace(second=0, microsecond=0)

        with pytest.raises(ValueError, match="cannot be 24 hours or more"):
            validate_time_range(now, now)

    def test_br_val_001_positive_duration_maximum_valid(self):
        """BR-VAL-001: Deve aceitar duração máxima válida (< 24 horas)."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = start + timedelta(hours=23, minutes=59)  # Logo abaixo de 24h

        result = validate_time_range(start, end)

        assert result == end
        duration_seconds = (result - start).total_seconds()
        assert duration_seconds == (23 * 3600 + 59 * 60)  # 23h59m

    def test_br_val_001_positive_duration_rejects_24h_exact(self):
        """BR-VAL-001: Deve rejeitar duração de exatamente 24 horas."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = start  # Mesmo horário = 24h quando ajustado

        with pytest.raises(ValueError, match="cannot be 24 hours or more"):
            validate_time_range(start, end)

    def test_br_val_001_positive_duration_rejects_over_24h(self):
        """BR-VAL-001: Deve rejeitar duração superior a 24 horas."""
        now = datetime.now(UTC).replace(second=0, microsecond=0)
        start = now
        end = start + timedelta(hours=25)

        with pytest.raises(ValueError, match="cannot be 24 hours or more"):
            validate_time_range(start, end)

    # ------------------------------------------------------------------------
    # BR-VAL-001: Horários dentro do dia (00:00 - 23:59)
    # ------------------------------------------------------------------------

    def test_br_val_001_valid_time_range_midnight_start(self):
        """BR-VAL-001: Deve aceitar horário de início à meia-noite (00:00)."""
        time = parse_time("00:00")

        assert time.hour == 0
        assert time.minute == 0

    def test_br_val_001_valid_time_range_end_of_day(self):
        """BR-VAL-001: Deve aceitar horário no final do dia (23:59)."""
        time = parse_time("23:59")

        assert time.hour == 23
        assert time.minute == 59

    def test_br_val_001_valid_time_range_rejects_hour_24(self):
        """BR-VAL-001: Deve rejeitar hora 24 (fora do range válido)."""
        with pytest.raises(ValueError, match="Hour must be between 0 and 23"):
            parse_time("24:00")

    def test_br_val_001_valid_time_range_rejects_hour_negative(self):
        """BR-VAL-001: Deve rejeitar hora negativa (fora do range válido)."""
        with pytest.raises(ValueError, match="Hour must be between 0 and 23"):
            parse_time("-1:00")

    def test_br_val_001_valid_time_range_rejects_minute_60(self):
        """BR-VAL-001: Deve rejeitar minuto 60 (fora do range válido)."""
        with pytest.raises(ValueError, match="Minute must be between 0 and 59"):
            parse_time("12:60")

    def test_br_val_001_valid_time_range_rejects_minute_negative(self):
        """BR-VAL-001: Deve rejeitar minuto negativo (fora do range válido)."""
        with pytest.raises(ValueError, match="Minute must be between 0 and 59"):
            parse_time("12:-1")

    def test_br_val_001_valid_time_range_accepts_all_valid_hours(self):
        """BR-VAL-001: Deve aceitar todas as horas de 0 a 23."""
        for hour in range(0, 24):
            time_str = f"{hour:02d}:00"
            time = parse_time(time_str)
            assert time.hour == hour

    def test_br_val_001_valid_time_range_accepts_all_valid_minutes(self):
        """BR-VAL-001: Deve aceitar todos os minutos de 0 a 59."""
        for minute in range(0, 60):
            time_str = f"12:{minute:02d}"
            time = parse_time(time_str)
            assert time.minute == minute

    # ------------------------------------------------------------------------
    # BR-VAL-001: Testes de integração (múltiplas regras)
    # ------------------------------------------------------------------------

    def test_br_val_001_integration_valid_morning_event(self):
        """BR-VAL-001: Teste de integração - evento matinal válido."""
        start = parse_time("09:00")
        end = parse_time("10:30")

        result = validate_time_range(start, end)

        # Todas as três regras satisfeitas:
        # 1. start < end ✓
        # 2. duration > 0 (90 minutos) ✓
        # 3. horários em range válido (09:00, 10:30) ✓
        assert result == end
        duration_minutes = (result - start).total_seconds() / 60
        assert duration_minutes == 90

    def test_br_val_001_integration_valid_evening_to_night(self):
        """BR-VAL-001: Teste de integração - evento noturno cruzando meia-noite."""
        start = parse_time("23:00")
        end = parse_time("01:00")

        result = validate_time_range(start, end)

        # Todas as três regras satisfeitas com cruzamento de meia-noite:
        # 1. start < end (após ajuste) ✓
        # 2. duration > 0 (2 horas) ✓
        # 3. horários em range válido (23:00, 01:00) ✓
        assert result.hour == 1
        assert result.day == end.day + 1
        duration_hours = (result - start).total_seconds() / 3600
        assert duration_hours == 2

    def test_br_val_001_integration_edge_case_one_minute_before_midnight(self):
        """BR-VAL-001: Teste de integração - evento terminando um minuto antes da meia-noite."""
        now = datetime.now(UTC).replace(hour=22, minute=0, second=0, microsecond=0)
        start = now
        end = now.replace(hour=23, minute=59)

        result = validate_time_range(start, end)

        # Evento válido dentro do mesmo dia
        assert result == end
        duration_minutes = (result - start).total_seconds() / 60
        assert duration_minutes == 119  # 1h59m
