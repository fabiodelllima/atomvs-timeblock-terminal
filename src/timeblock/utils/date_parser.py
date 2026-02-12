"""Parser de datas com suporte a múltiplos formatos."""

import re
from datetime import date, datetime

from timeblock.utils.validators import validate_date

# Patterns para detectar formato aparente (estrutura correta, valores podem ser inválidos)
ISO_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DAY_FIRST_DASH_PATTERN = re.compile(r"^\d{2}-\d{2}-\d{4}$")
DAY_FIRST_SLASH_PATTERN = re.compile(r"^\d{2}/\d{2}/\d{4}$")


def parse_date_input(date_input: str | date) -> date:
    """Parse date from multiple formats (BR-CLI-002).

    Formatos aceitos:
    - YYYY-MM-DD (ISO 8601)
    - DD-MM-YYYY (day-first com traço)
    - DD/MM/YYYY (day-first com barra)
    - date object (passthrough)

    Args:
        date_input: String em um dos formatos suportados ou objeto date

    Returns:
        Objeto date validado

    Raises:
        ValueError: Formato inválido ou data fora do range
    """
    # Se já é objeto date, validar e retornar
    if isinstance(date_input, date):
        return validate_date(date_input)

    # Se não é string, rejeitar com erro de formato
    if not isinstance(date_input, str):
        raise ValueError("Date must be in ISO 8601 format (YYYY-MM-DD)")

    # Verificar string vazia/whitespace
    if not date_input.strip():
        raise ValueError("Date cannot be empty")

    date_str = date_input.strip()

    # Detectar formato aparente e tentar parsear
    format_map = [
        (ISO_PATTERN, "%Y-%m-%d"),
        (DAY_FIRST_DASH_PATTERN, "%d-%m-%Y"),
        (DAY_FIRST_SLASH_PATTERN, "%d/%m/%Y"),
    ]

    for pattern, fmt in format_map:
        if pattern.match(date_str):
            # String tem estrutura correta para este formato
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
            except ValueError:
                # Estrutura correta mas valores inválidos (ex: mês 13)
                raise ValueError("Invalid date: day is out of range for month")
            # Parsing OK - validar range (pode levantar ValueError próprio)
            return validate_date(parsed_date)

    # Nenhum pattern casou - formato desconhecido
    raise ValueError("Date must be in ISO 8601 format (YYYY-MM-DD)")
