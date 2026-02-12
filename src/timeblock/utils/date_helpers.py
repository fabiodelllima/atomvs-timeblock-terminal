"""Utilitarios de manipulacao de datas para calculos de intervalos de tempo."""

from datetime import UTC, datetime, timedelta

from dateutil.relativedelta import relativedelta


def add_months(base_date: datetime, months_offset: int) -> datetime:
    """Adiciona ou subtrai meses de um datetime.

    Args:
        base_date: Data base.
        months_offset: Numero de meses para adicionar (positivo) ou subtrair (negativo).

    Returns:
        Novo datetime com meses adicionados/subtraidos.

    Examples:
        >>> from datetime import datetime
        >>> date = datetime(2025, 1, 15)
        >>> add_months(date, 2)  # 15 de Marco de 2025
        >>> add_months(date, -1)  # 15 de Dezembro de 2024
    """
    result: datetime = base_date + relativedelta(months=months_offset)
    return result


def get_month_range(months_offset: int = 0) -> tuple[datetime, datetime]:
    """Retorna inicio e fim de um mes com offset relativo.

    Args:
        months_offset: Numero de meses a partir do mes atual.
                      0 = este mes, +1 = proximo mes, -1 = mes anterior.

    Returns:
        Tupla (inicio_do_mes, fim_do_mes) como datetimes com timezone.

    Examples:
        >>> start, end = get_month_range(0)   # Este mes
        >>> start, end = get_month_range(+1)  # Proximo mes
    """
    now = datetime.now(UTC)
    target_month = add_months(now, months_offset)

    # Inicio: primeiro dia do mes as 00:00:00
    start_of_month = target_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Fim: primeiro dia do proximo mes as 00:00:00
    end_of_month = add_months(start_of_month, 1)

    return (start_of_month, end_of_month)


def get_week_range(weeks_offset: int = 0) -> tuple[datetime, datetime]:
    """Retorna inicio e fim de uma semana com offset relativo.

    Semana definida como Segunda 00:00:00 ate Domingo 23:59:59.

    Args:
        weeks_offset: Numero de semanas a partir da semana atual.
                     0 = esta semana, +1 = proxima semana, -1 = semana anterior.

    Returns:
        Tupla (inicio_da_semana, fim_da_semana) como datetimes com timezone.

    Examples:
        >>> start, end = get_week_range(0)   # Esta semana
        >>> start, end = get_week_range(-1)  # Semana passada
    """
    now = datetime.now(UTC)

    # Calcula inicio da semana atual (Segunda-feira)
    days_since_monday = now.weekday()
    start_of_current_week = now - timedelta(days=days_since_monday)
    start_of_current_week = start_of_current_week.replace(hour=0, minute=0, second=0, microsecond=0)

    # Aplica offset
    start_of_target_week = start_of_current_week + timedelta(weeks=weeks_offset)

    # Fim: 7 dias depois
    end_of_target_week = start_of_target_week + timedelta(days=7)

    return (start_of_target_week, end_of_target_week)


def get_day_range(days_offset: int = 0) -> tuple[datetime, datetime]:
    """Retorna inicio e fim de um dia com offset relativo.

    Args:
        days_offset: Numero de dias a partir de hoje.
                    0 = hoje, +1 = amanha, -1 = ontem.

    Returns:
        Tupla (inicio_do_dia, fim_do_dia) como datetimes com timezone.

    Examples:
        >>> start, end = get_day_range(0)   # Hoje
        >>> start, end = get_day_range(+1)  # Amanha
    """
    now = datetime.now(UTC)
    target_day = now + timedelta(days=days_offset)

    # Inicio: 00:00:00 do dia alvo
    start_of_day = target_day.replace(hour=0, minute=0, second=0, microsecond=0)

    # Fim: 00:00:00 do dia seguinte
    end_of_day = start_of_day + timedelta(days=1)

    return (start_of_day, end_of_day)
