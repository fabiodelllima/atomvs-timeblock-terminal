"""Utilitários de validação de entrada."""

import re
from datetime import UTC, date, datetime, timedelta


def parse_time(time_str: str) -> datetime:
    """Converte string de horário para datetime com data atual.

    Suporta dois formatos:
    - HH:MM (ex: "09:30", "14:00", "00:45")
    - HHh ou HHhMM (ex: "9h", "14h30", "0h", "0h45")

    Args:
        time_str: String de horário em um dos formatos suportados

    Returns:
        Objeto datetime com data de hoje e horário especificado (UTC)

    Raises:
        ValueError: Se o formato for inválido ou valores fora do range

    Examples:
        >>> parse_time("09:30")  # Formato tradicional
        >>> parse_time("9h30")   # Formato brasileiro
        >>> parse_time("14h")    # Apenas hora (minutos padrão 00)
        >>> parse_time("0h45")   # Após meia-noite
    """
    if not time_str or not isinstance(time_str, str):
        raise ValueError("Time string cannot be empty")

    time_str = time_str.strip()
    hour = None
    minute = None

    # Tentar formato: HHh ou HHhMM (ex: "14h", "9h30", "0h45")
    h_pattern = r"^(\d{1,2})h(\d{1,2})?$"
    h_match = re.match(h_pattern, time_str)

    if h_match:
        hour = int(h_match.group(1))
        minute = int(h_match.group(2)) if h_match.group(2) else 0

    # Tentar formato: HH:MM (ex: "09:30", "14:00")
    elif ":" in time_str:
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in HH:MM or HHh or HHhMM format")

        try:
            hour = int(parts[0])
            minute = int(parts[1])
        except ValueError as e:
            raise ValueError("Time must contain only numbers") from e

    else:
        raise ValueError("Time must be in HH:MM or HHh or HHhMM format")

    # Validar ranges
    if not (0 <= hour <= 23):
        raise ValueError("Hour must be between 0 and 23")
    if not (0 <= minute <= 59):
        raise ValueError("Minute must be between 0 and 59")

    # Criar datetime com data atual
    now = datetime.now(UTC)
    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)


def is_valid_hex_color(color: str) -> bool:
    """Valida código de cor hexadecimal.

    Args:
        color: Código de cor (ex: "#FF5733")

    Returns:
        True se cor hexadecimal válida, False caso contrário
    """
    if not color:
        return False

    pattern = r"^#[0-9A-Fa-f]{6}$"
    return bool(re.match(pattern, color))


def validate_time_range(start: datetime, end: datetime) -> datetime:
    """Valida e ajusta intervalo de tempo para cruzamento de meia-noite.

    Regras de Negócio:
    1. Se end <= start, assume evento cruza meia-noite (próximo dia)
    2. Duração mínima: 1 minuto
    3. Duração máxima: < 24 horas (time blocking é para tarefas específicas)

    Args:
        start: Datetime de início (com data + horário)
        end: Datetime de término (com data + horário)

    Returns:
        Datetime de término ajustado (pode ser +1 dia se cruzar meia-noite)

    Raises:
        ValueError: Se a duração for inválida

    Examples:
        >>> # Evento no mesmo dia
        >>> start = datetime(2025, 10, 14, 9, 0)
        >>> end = datetime(2025, 10, 14, 10, 30)
        >>> validate_time_range(start, end)  # Retorna end sem alteração

        >>> # Cruza meia-noite
        >>> start = datetime(2025, 10, 14, 23, 0)
        >>> end = datetime(2025, 10, 14, 2, 0)  # 02:00 mesmo dia
        >>> validate_time_range(start, end)
        >>> # Retorna: datetime(2025, 10, 15, 2, 0)  # Próximo dia!
    """
    # Detectar cruzamento de meia-noite: se end <= start, deve ser próximo dia
    adjusted_end = end
    if end <= start:
        adjusted_end = end + timedelta(days=1)

    # Calcular duração em segundos
    duration = (adjusted_end - start).total_seconds()

    # Duração mínima: 1 minuto
    if duration < 60:
        raise ValueError("Event must be at least 1 minute long")

    # Duração máxima: < 24 horas
    if duration >= 86400:
        raise ValueError(
            "Event duration cannot be 24 hours or more. "
            "Time blocking is designed for specific activities, not entire days."
        )

    return adjusted_end


def validate_date(date_input: str | date) -> date:
    """Valida data conforme BR-VAL-002.

    Requisitos:
    - Data não pode ser anterior a 2025-01-01
    - Sem limite para datas futuras
    - Formato ISO 8601 (YYYY-MM-DD) para strings

    Args:
        date_input: String no formato ISO 8601 (YYYY-MM-DD) ou objeto date

    Returns:
        Objeto date validado

    Raises:
        ValueError: Se a data for inválida ou não atender aos requisitos
        TypeError: Se o tipo do argumento for inválido (None, int, etc)

    Examples:
        >>> validate_date("2025-06-15")
        date(2025, 6, 15)
        >>> validate_date(date(2025, 6, 15))
        date(2025, 6, 15)
    """
    minimum_date = date(2025, 1, 1)

    # Rejeitar None
    if date_input is None:
        raise ValueError("Date cannot be empty")

    # Rejeitar tipos inválidos (int, float, etc)
    if not isinstance(date_input, (str, date)):
        raise ValueError("Date must be in ISO 8601 format (YYYY-MM-DD)")

    # Se já é objeto date, validar range apenas
    if isinstance(date_input, date):
        if date_input < minimum_date:
            raise ValueError(f"Date cannot be before {minimum_date.isoformat()}")
        return date_input

    # A partir daqui, date_input é string
    # Rejeitar strings vazias ou apenas espaços
    if not date_input or not date_input.strip():
        raise ValueError("Date cannot be empty")

    date_str = date_input.strip()

    # Validar formato ISO 8601: YYYY-MM-DD
    iso_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(iso_pattern, date_str):
        raise ValueError("Date must be in ISO 8601 format (YYYY-MM-DD)")

    # Tentar fazer parsing
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        # ValueError do strptime indica data inválida no calendário
        # (ex: 30/02, 29/02 em ano não-bissexto, 31/04, etc)
        raise ValueError(f"Invalid date: {e}") from e

    # Validar range mínimo
    if parsed_date < minimum_date:
        raise ValueError(f"Date cannot be before {minimum_date.isoformat()}")

    return parsed_date
