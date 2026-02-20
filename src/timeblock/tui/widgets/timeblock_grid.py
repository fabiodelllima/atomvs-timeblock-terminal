"""TimeblockGrid - Grade temporal proporcional."""

import math


def calculate_block_height(duration_minutes: int) -> int:
    """Calcula altura do bloco em linhas (30min = 1 linha, minimo 1)."""
    return max(1, math.ceil(duration_minutes / 30))


def generate_time_slots(start: str, end: str) -> list[str]:
    """Gera lista de slots de 30min entre start e end (formato HH:MM)."""
    start_h, start_m = map(int, start.split(":"))
    end_h, end_m = map(int, end.split(":"))

    start_total = start_h * 60 + start_m
    end_total = end_h * 60 + end_m

    slots = []
    current = start_total
    while current < end_total:
        h, m = divmod(current, 60)
        slots.append(f"{h:02d}:{m:02d}")
        current += 30

    return slots
