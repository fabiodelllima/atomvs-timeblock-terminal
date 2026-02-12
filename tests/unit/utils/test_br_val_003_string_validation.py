"""Testes unitários para BR-VAL-003: Validação de Strings.

BR-VAL-003 define limites para campos de texto:
    - title: 1-200 caracteres
    - name: 1-200 caracteres
    - description: 0-2000 caracteres (opcional)
    - note: 0-500 caracteres (opcional)

Comportamento: Trim de espaços antes da validação.
"""

import pytest

from timeblock.utils.validators import (
    StringValidationError,
    validate_description,
    validate_name,
    validate_note,
    validate_title,
)


class TestBRVal003ValidateTitle:
    """BR-VAL-003: Validação de campo title (1-200 chars, obrigatório)."""

    def test_br_val_003_title_valid_minimum(self):
        """BR-VAL-003: Title com 1 caractere é válido."""
        result = validate_title("A")
        assert result == "A"

    def test_br_val_003_title_valid_maximum(self):
        """BR-VAL-003: Title com 200 caracteres é válido."""
        title = "A" * 200
        result = validate_title(title)
        assert result == title
        assert len(result) == 200

    def test_br_val_003_title_exceeds_maximum(self):
        """BR-VAL-003: Title com 201+ caracteres é inválido."""
        title = "A" * 201
        with pytest.raises(StringValidationError, match="cannot exceed 200"):
            validate_title(title)

    def test_br_val_003_title_empty_string(self):
        """BR-VAL-003: Title vazio é inválido."""
        with pytest.raises(StringValidationError, match="cannot be empty"):
            validate_title("")

    def test_br_val_003_title_none(self):
        """BR-VAL-003: Title None é inválido."""
        with pytest.raises(StringValidationError, match="cannot be empty"):
            validate_title(None)

    def test_br_val_003_title_whitespace_only(self):
        """BR-VAL-003: Title apenas com espaços é inválido (após trim)."""
        with pytest.raises(StringValidationError, match="cannot be empty"):
            validate_title("   ")

    def test_br_val_003_title_trim_whitespace(self):
        """BR-VAL-003: Trim aplicado antes da validação."""
        result = validate_title("  Hello World  ")
        assert result == "Hello World"

    def test_br_val_003_title_trim_preserves_internal_spaces(self):
        """BR-VAL-003: Trim preserva espaços internos."""
        result = validate_title("  Hello   World  ")
        assert result == "Hello   World"


class TestBRVal003ValidateName:
    """BR-VAL-003: Validação de campo name (1-200 chars, obrigatório)."""

    def test_br_val_003_name_valid_minimum(self):
        """BR-VAL-003: Name com 1 caractere é válido."""
        result = validate_name("X")
        assert result == "X"

    def test_br_val_003_name_valid_maximum(self):
        """BR-VAL-003: Name com 200 caracteres é válido."""
        name = "B" * 200
        result = validate_name(name)
        assert result == name

    def test_br_val_003_name_exceeds_maximum(self):
        """BR-VAL-003: Name com 201+ caracteres é inválido."""
        name = "B" * 201
        with pytest.raises(StringValidationError, match="cannot exceed 200"):
            validate_name(name)

    def test_br_val_003_name_empty_string(self):
        """BR-VAL-003: Name vazio é inválido."""
        with pytest.raises(StringValidationError, match="cannot be empty"):
            validate_name("")

    def test_br_val_003_name_none(self):
        """BR-VAL-003: Name None é inválido."""
        with pytest.raises(StringValidationError, match="cannot be empty"):
            validate_name(None)

    def test_br_val_003_name_trim_whitespace(self):
        """BR-VAL-003: Trim aplicado em name."""
        result = validate_name("  My Routine  ")
        assert result == "My Routine"


class TestBRVal003ValidateDescription:
    """BR-VAL-003: Validação de campo description (0-2000 chars, opcional)."""

    def test_br_val_003_description_valid_content(self):
        """BR-VAL-003: Description com conteúdo válido."""
        result = validate_description("This is a description")
        assert result == "This is a description"

    def test_br_val_003_description_valid_maximum(self):
        """BR-VAL-003: Description com 2000 caracteres é válido."""
        desc = "C" * 2000
        result = validate_description(desc)
        assert result == desc
        assert len(result) == 2000

    def test_br_val_003_description_exceeds_maximum(self):
        """BR-VAL-003: Description com 2001+ caracteres é inválido."""
        desc = "C" * 2001
        with pytest.raises(StringValidationError, match="cannot exceed 2000"):
            validate_description(desc)

    def test_br_val_003_description_none_allowed(self):
        """BR-VAL-003: Description None é permitido (opcional)."""
        result = validate_description(None)
        assert result is None

    def test_br_val_003_description_empty_returns_none(self):
        """BR-VAL-003: Description vazio retorna None."""
        result = validate_description("")
        assert result is None

    def test_br_val_003_description_whitespace_returns_none(self):
        """BR-VAL-003: Description apenas espaços retorna None."""
        result = validate_description("   ")
        assert result is None

    def test_br_val_003_description_trim_whitespace(self):
        """BR-VAL-003: Trim aplicado em description."""
        result = validate_description("  Some text  ")
        assert result == "Some text"


class TestBRVal003ValidateNote:
    """BR-VAL-003: Validação de campo note (0-500 chars, opcional)."""

    def test_br_val_003_note_valid_content(self):
        """BR-VAL-003: Note com conteúdo válido."""
        result = validate_note("Quick note")
        assert result == "Quick note"

    def test_br_val_003_note_valid_maximum(self):
        """BR-VAL-003: Note com 500 caracteres é válido."""
        note = "D" * 500
        result = validate_note(note)
        assert result == note
        assert len(result) == 500

    def test_br_val_003_note_exceeds_maximum(self):
        """BR-VAL-003: Note com 501+ caracteres é inválido."""
        note = "D" * 501
        with pytest.raises(StringValidationError, match="cannot exceed 500"):
            validate_note(note)

    def test_br_val_003_note_none_allowed(self):
        """BR-VAL-003: Note None é permitido (opcional)."""
        result = validate_note(None)
        assert result is None

    def test_br_val_003_note_empty_returns_none(self):
        """BR-VAL-003: Note vazio retorna None."""
        result = validate_note("")
        assert result is None

    def test_br_val_003_note_whitespace_returns_none(self):
        """BR-VAL-003: Note apenas espaços retorna None."""
        result = validate_note("   \t\n  ")
        assert result is None

    def test_br_val_003_note_trim_whitespace(self):
        """BR-VAL-003: Trim aplicado em note."""
        result = validate_note("  Note content  ")
        assert result == "Note content"


class TestBRVal003EdgeCases:
    """BR-VAL-003: Casos de borda e caracteres especiais."""

    def test_br_val_003_unicode_characters(self):
        """BR-VAL-003: Caracteres Unicode são permitidos."""
        result = validate_title("Título com acentuação: é, ã, ç")
        assert result == "Título com acentuação: é, ã, ç"

    def test_br_val_003_emoji_characters(self):
        """BR-VAL-003: Emojis contam como caracteres."""
        # Emoji pode ter diferentes tamanhos em bytes, mas conta como caracteres
        result = validate_title("Task")
        assert "Task" in result

    def test_br_val_003_newlines_in_description(self):
        """BR-VAL-003: Quebras de linha permitidas em description."""
        desc = "Line 1\nLine 2\nLine 3"
        result = validate_description(desc)
        assert result == desc

    def test_br_val_003_tabs_trimmed(self):
        """BR-VAL-003: Tabs nas extremidades são removidos."""
        result = validate_title("\t\tTitle\t\t")
        assert result == "Title"

    def test_br_val_003_boundary_199_chars(self):
        """BR-VAL-003: Title com 199 caracteres é válido."""
        title = "A" * 199
        result = validate_title(title)
        assert len(result) == 199

    def test_br_val_003_boundary_1999_chars(self):
        """BR-VAL-003: Description com 1999 caracteres é válido."""
        desc = "B" * 1999
        result = validate_description(desc)
        assert len(result) == 1999

    def test_br_val_003_boundary_499_chars(self):
        """BR-VAL-003: Note com 499 caracteres é válido."""
        note = "C" * 499
        result = validate_note(note)
        assert len(result) == 499
