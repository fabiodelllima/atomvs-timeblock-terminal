"""Testes unitários para date_parser (BR-CLI-002)."""

from datetime import date

from pytest import raises

from timeblock.utils.date_parser import parse_date_input


class TestDateParser:
    """Testes unitários para parse_date_input."""

    # Formatos aceitos
    def test_accepts_iso_8601(self):
        """Aceita formato ISO 8601."""
        assert parse_date_input("2025-06-15") == date(2025, 6, 15)

    def test_accepts_day_first_dash(self):
        """Aceita formato DD-MM-YYYY."""
        assert parse_date_input("15-06-2025") == date(2025, 6, 15)

    def test_accepts_day_first_slash(self):
        """Aceita formato DD/MM/YYYY."""
        assert parse_date_input("15/06/2025") == date(2025, 6, 15)

    def test_accepts_date_object(self):
        """Aceita objeto date."""
        input_date = date(2025, 6, 15)
        assert parse_date_input(input_date) == date(2025, 6, 15)

    # Validação de range (delega para validate_date)
    def test_rejects_before_minimum(self):
        """Rejeita data antes de 2025-01-01."""
        with raises(ValueError, match="Date cannot be before 2025-01-01"):
            parse_date_input("2024-12-31")

    def test_accepts_at_minimum(self):
        """Aceita data mínima exata."""
        assert parse_date_input("2025-01-01") == date(2025, 1, 1)

    def test_accepts_far_future(self):
        """Aceita data distante no futuro."""
        assert parse_date_input("2100-12-31") == date(2100, 12, 31)

    # Validação de calendário
    def test_rejects_invalid_month(self):
        """Rejeita mês inválido."""
        with raises(ValueError, match="Invalid date"):
            parse_date_input("2025-13-01")

    def test_rejects_invalid_day(self):
        """Rejeita dia inválido."""
        with raises(ValueError, match="Invalid date"):
            parse_date_input("30/02/2025")

    def test_accepts_leap_day(self):
        """Aceita dia bissexto válido."""
        assert parse_date_input("29/02/2028") == date(2028, 2, 29)

    def test_rejects_leap_day_non_leap_year(self):
        """Rejeita 29/02 em ano não-bissexto."""
        with raises(ValueError, match="Invalid date"):
            parse_date_input("29/02/2025")

    # Edge cases
    def test_strips_whitespace(self):
        """Remove espaços em branco."""
        assert parse_date_input("  2025-06-15  ") == date(2025, 6, 15)

    def test_rejects_empty_string(self):
        """Rejeita string vazia."""
        with raises(ValueError, match="Date cannot be empty"):
            parse_date_input("")

    def test_rejects_whitespace_only(self):
        """Rejeita string apenas com espaços."""
        with raises(ValueError, match="Date cannot be empty"):
            parse_date_input("   ")

    def test_rejects_none(self):
        """Rejeita None."""
        with raises(ValueError, match="Date must be in ISO 8601 format"):
            parse_date_input(None)  # type: ignore

    def test_rejects_integer(self):
        """Rejeita inteiro."""
        with raises(ValueError, match="Date must be in ISO 8601 format"):
            parse_date_input(20250615)  # type: ignore

    def test_rejects_invalid_format(self):
        """Rejeita formato não suportado."""
        with raises(ValueError, match="Date must be in ISO 8601 format"):
            parse_date_input("Jun 15, 2025")
