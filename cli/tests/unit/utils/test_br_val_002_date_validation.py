"""Testes para BR-VAL-002: Validação de Datas.

Referência da Regra de Negócio:
    - BR-VAL-002: Validação de Datas
      * Data não anterior a 2025-01-01
      * Sem limite de data futura
      * Formato ISO 8601 (YYYY-MM-DD)
"""

from datetime import date

import pytest

from timeblock.utils.validators import validate_date

# ============================================================================
# BR-VAL-002: Date Validation - Suite Completa de Testes
# ============================================================================


class TestBRVal002DateValidation:
    """Testes para BR-VAL-002: Regras de validação de datas.

    Esta classe valida os três requisitos principais:
        1. Data não pode ser anterior a 2025-01-01 (limite mínimo)
        2. Sem limite para datas futuras (planejamento de longo prazo)
        3. Formato ISO 8601 obrigatório (YYYY-MM-DD)
    """

    # ------------------------------------------------------------------------
    # BR-VAL-002: Data não anterior a 2025-01-01
    # ------------------------------------------------------------------------

    def test_br_val_002_accepts_minimum_date(self):
        """BR-VAL-002: Deve aceitar a data mínima exata (2025-01-01)."""
        result = validate_date("2025-01-01")

        assert result == date(2025, 1, 1)

    def test_br_val_002_accepts_date_object_at_minimum(self):
        """BR-VAL-002: Deve aceitar objeto date na data mínima."""
        input_date = date(2025, 1, 1)

        result = validate_date(input_date)

        assert result == date(2025, 1, 1)

    def test_br_val_002_accepts_date_after_minimum(self):
        """BR-VAL-002: Deve aceitar data após o mínimo."""
        result = validate_date("2025-01-02")

        assert result == date(2025, 1, 2)

    def test_br_val_002_accepts_date_well_after_minimum(self):
        """BR-VAL-002: Deve aceitar data bem após o mínimo."""
        result = validate_date("2025-06-15")

        assert result == date(2025, 6, 15)

    def test_br_val_002_rejects_date_one_day_before_minimum(self):
        """BR-VAL-002: Deve rejeitar data um dia antes do mínimo."""
        with pytest.raises(ValueError, match="Date cannot be before 2025-01-01"):
            validate_date("2024-12-31")

    def test_br_val_002_rejects_date_before_minimum(self):
        """BR-VAL-002: Deve rejeitar data anterior ao mínimo."""
        with pytest.raises(ValueError, match="Date cannot be before 2025-01-01"):
            validate_date("2024-01-01")

    def test_br_val_002_rejects_date_far_before_minimum(self):
        """BR-VAL-002: Deve rejeitar data muito anterior ao mínimo."""
        with pytest.raises(ValueError, match="Date cannot be before 2025-01-01"):
            validate_date("2020-01-01")

    def test_br_val_002_rejects_date_object_before_minimum(self):
        """BR-VAL-002: Deve rejeitar objeto date anterior ao mínimo."""
        input_date = date(2024, 12, 31)

        with pytest.raises(ValueError, match="Date cannot be before 2025-01-01"):
            validate_date(input_date)

    # ------------------------------------------------------------------------
    # BR-VAL-002: Sem limite de data futura
    # ------------------------------------------------------------------------

    def test_br_val_002_accepts_near_future_date(self):
        """BR-VAL-002: Deve aceitar data no futuro próximo."""
        result = validate_date("2026-12-31")

        assert result == date(2026, 12, 31)

    def test_br_val_002_accepts_medium_future_date(self):
        """BR-VAL-002: Deve aceitar data no futuro médio."""
        result = validate_date("2030-06-15")

        assert result == date(2030, 6, 15)

    def test_br_val_002_accepts_far_future_date(self):
        """BR-VAL-002: Deve aceitar data no futuro distante."""
        result = validate_date("2050-01-01")

        assert result == date(2050, 1, 1)

    def test_br_val_002_accepts_very_far_future_date(self):
        """BR-VAL-002: Deve aceitar data muito distante no futuro."""
        result = validate_date("2100-12-31")

        assert result == date(2100, 12, 31)

    def test_br_val_002_accepts_future_date_object(self):
        """BR-VAL-002: Deve aceitar objeto date no futuro."""
        input_date = date(2030, 6, 15)

        result = validate_date(input_date)

        assert result == date(2030, 6, 15)

    # ------------------------------------------------------------------------
    # BR-VAL-002: Formato ISO 8601 (YYYY-MM-DD)
    # ------------------------------------------------------------------------

    def test_br_val_002_accepts_valid_iso_format(self):
        """BR-VAL-002: Deve aceitar formato ISO 8601 válido."""
        result = validate_date("2025-03-15")

        assert result == date(2025, 3, 15)

    def test_br_val_002_rejects_brazilian_format(self):
        """BR-VAL-002: Deve rejeitar formato brasileiro (DD/MM/YYYY)."""
        with pytest.raises(ValueError, match="Date must be in ISO 8601 format \\(YYYY-MM-DD\\)"):
            validate_date("15/03/2025")

    def test_br_val_002_rejects_american_format(self):
        """BR-VAL-002: Deve rejeitar formato americano (MM/DD/YYYY)."""
        with pytest.raises(ValueError, match="Date must be in ISO 8601 format \\(YYYY-MM-DD\\)"):
            validate_date("03/15/2025")

    def test_br_val_002_rejects_format_with_dots(self):
        """BR-VAL-002: Deve rejeitar formato com pontos (YYYY.MM.DD)."""
        with pytest.raises(ValueError, match="Date must be in ISO 8601 format \\(YYYY-MM-DD\\)"):
            validate_date("2025.03.15")

    def test_br_val_002_rejects_format_without_separators(self):
        """BR-VAL-002: Deve rejeitar formato sem separadores (YYYYMMDD)."""
        with pytest.raises(ValueError, match="Date must be in ISO 8601 format \\(YYYY-MM-DD\\)"):
            validate_date("20250315")

    def test_br_val_002_rejects_empty_string(self):
        """BR-VAL-002: Deve rejeitar string vazia."""
        with pytest.raises(ValueError, match="Date cannot be empty"):
            validate_date("")

    def test_br_val_002_rejects_whitespace_only(self):
        """BR-VAL-002: Deve rejeitar string apenas com espaços."""
        with pytest.raises(ValueError, match="Date cannot be empty"):
            validate_date("   ")

    def test_br_val_002_rejects_invalid_month(self):
        """BR-VAL-002: Deve rejeitar mês inválido."""
        with pytest.raises(ValueError, match="Invalid date"):
            validate_date("2025-13-01")

    def test_br_val_002_rejects_month_zero(self):
        """BR-VAL-002: Deve rejeitar mês zero."""
        with pytest.raises(ValueError, match="Invalid date"):
            validate_date("2025-00-01")

    def test_br_val_002_rejects_invalid_day(self):
        """BR-VAL-002: Deve rejeitar dia inválido."""
        with pytest.raises(ValueError, match="Invalid date"):
            validate_date("2025-01-32")

    def test_br_val_002_rejects_day_zero(self):
        """BR-VAL-002: Deve rejeitar dia zero."""
        with pytest.raises(ValueError, match="Invalid date"):
            validate_date("2025-01-00")

    def test_br_val_002_rejects_february_30(self):
        """BR-VAL-002: Deve rejeitar 30 de fevereiro."""
        with pytest.raises(ValueError, match="Invalid date"):
            validate_date("2025-02-30")

    def test_br_val_002_rejects_february_29_non_leap_year(self):
        """BR-VAL-002: Deve rejeitar 29 de fevereiro em ano não bissexto."""
        with pytest.raises(ValueError, match="Invalid date"):
            validate_date("2025-02-29")

    def test_br_val_002_accepts_february_29_leap_year(self):
        """BR-VAL-002: Deve aceitar 29 de fevereiro em ano bissexto."""
        result = validate_date("2028-02-29")

        assert result == date(2028, 2, 29)

    def test_br_val_002_rejects_april_31(self):
        """BR-VAL-002: Deve rejeitar 31 de abril (mês com 30 dias)."""
        with pytest.raises(ValueError, match="Invalid date"):
            validate_date("2025-04-31")

    # ------------------------------------------------------------------------
    # BR-VAL-002: Testes de tipo
    # ------------------------------------------------------------------------

    def test_br_val_002_returns_date_object_from_string(self):
        """BR-VAL-002: Deve retornar objeto date quando recebe string."""
        result = validate_date("2025-06-15")

        assert isinstance(result, date)
        assert result == date(2025, 6, 15)

    def test_br_val_002_returns_date_object_from_date(self):
        """BR-VAL-002: Deve retornar objeto date quando recebe date."""
        input_date = date(2025, 6, 15)

        result = validate_date(input_date)

        assert isinstance(result, date)
        assert result == date(2025, 6, 15)

    def test_br_val_002_rejects_none(self):
        """BR-VAL-002: Deve rejeitar None."""
        with pytest.raises(ValueError, match="Date cannot be empty"):
            validate_date(None)  # type: ignore

    def test_br_val_002_rejects_integer(self):
        """BR-VAL-002: Deve rejeitar integer."""
        with pytest.raises(ValueError, match="Date must be in ISO 8601 format \\(YYYY-MM-DD\\)"):
            validate_date(20250615)  # type: ignore

    # ------------------------------------------------------------------------
    # BR-VAL-002: Casos extremos
    # ------------------------------------------------------------------------

    def test_br_val_002_accepts_last_day_of_year(self):
        """BR-VAL-002: Deve aceitar último dia do ano."""
        result = validate_date("2025-12-31")

        assert result == date(2025, 12, 31)

    def test_br_val_002_accepts_first_day_of_year(self):
        """BR-VAL-002: Deve aceitar primeiro dia do ano."""
        result = validate_date("2026-01-01")

        assert result == date(2026, 1, 1)

    def test_br_val_002_accepts_leap_day(self):
        """BR-VAL-002: Deve aceitar dia bissexto válido."""
        result = validate_date("2028-02-29")

        assert result == date(2028, 2, 29)
