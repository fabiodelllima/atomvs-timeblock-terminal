"""Helpers de formatação para comandos de habit."""

from datetime import date

from rich.console import Console

from timeblock.models.enums import Status

console = Console()


def _resolve_date_range(
    today: bool, week: bool, habit_id: int | None
) -> tuple[date | None, date | None]:
    """Determina período para listagem de instâncias."""
    from datetime import timedelta

    if today and week:
        raise ValueError("--today e --week são mutuamente exclusivos")

    if today:
        return date.today(), date.today()
    if week or habit_id is None:
        return date.today(), date.today() + timedelta(days=6)
    return None, None


def _resolve_status_filter(
    pending: bool, done: bool, all_status: bool, habit_id: int | None
) -> Status | None:
    """Determina filtro de status para listagem."""
    if pending and done:
        raise ValueError("--pending e --done são mutuamente exclusivos")

    if pending:
        return Status.PENDING
    if done:
        return Status.DONE
    if not all_status and habit_id is None:
        return Status.PENDING
    return None


def display_instances(
    instances: list,
    today: bool,
    week: bool,
    habit_id: int | None,
    status_filter: Status | None,
) -> None:
    """Formata e exibe instâncias agrupadas por data."""
    if not instances:
        if habit_id:
            console.print(f"Nenhuma instância encontrada para hábito {habit_id}.")
        else:
            console.print("Nenhuma instância encontrada.")
        return

    instances_by_date: dict[date, list] = {}
    for inst in instances:
        if inst.date not in instances_by_date:
            instances_by_date[inst.date] = []
        instances_by_date[inst.date].append(inst)

    period_desc = "hoje" if today else "semana atual" if week or habit_id is None else "todas"
    status_desc = (
        "pendentes"
        if status_filter == Status.PENDING
        else "concluídas"
        if status_filter == Status.DONE
        else "todos status"
    )
    console.print(f"\n[bold]Instâncias ({period_desc}, {status_desc}):[/bold]\n")

    weekdays = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

    for dt in sorted(instances_by_date.keys()):
        console.print(f"[cyan]{weekdays[dt.weekday()]}, {dt.strftime('%d/%m')}:[/cyan]")
        for inst in sorted(instances_by_date[dt], key=lambda x: x.scheduled_start):
            _display_single_instance(inst)
        console.print()


def _display_single_instance(inst) -> None:
    """Exibe uma única instância formatada."""
    if inst.status == Status.DONE:
        marker, status_text = "[green][x][/green]", "concluída"
    elif inst.status == Status.NOT_DONE:
        marker, status_text = "[red][-][/red]", "não concluída"
    else:
        marker, status_text = "[ ]", "pendente"

    start = inst.scheduled_start.strftime("%H:%M")
    end = inst.scheduled_end.strftime("%H:%M")
    title = inst.habit.title if inst.habit else f"Hábito #{inst.habit_id}"

    console.print(f"  {marker} {start}-{end} {title} [dim](ID: {inst.id}, {status_text})[/dim]")


def display_log_result(timelog, instance) -> None:
    """Exibe resultado do log manual."""
    duration_secs = timelog.duration_seconds or 0
    hours, remainder = divmod(duration_secs, 3600)
    minutes = remainder // 60

    substatus_pt = {
        "full": "Completo",
        "partial": "Parcial",
        "overdone": "Acima da meta",
        "excessive": "Excessivo",
    }

    console.print("[green]Tempo registrado com sucesso[/green]")
    console.print(f"  Duração: {hours:02d}h{minutes:02d}min")

    if instance:
        console.print(f"  Completion: {instance.completion_percentage}%")
        if instance.done_substatus:
            substatus_str = substatus_pt.get(
                instance.done_substatus.value, instance.done_substatus.value
            )
            console.print(f"  Status: DONE ({substatus_str})")


def handle_log_error(e: ValueError, instance_id: int) -> None:
    """Trata erros específicos do log manual."""
    error_msg = str(e)
    if "not found" in error_msg.lower():
        console.print(f"[red]HabitInstance {instance_id} não encontrada[/red]")
    elif "start must be before end" in error_msg:
        console.print("[red]Erro: hora início deve ser anterior à hora fim[/red]")
    elif "duration must be positive" in error_msg:
        console.print("[red]Erro: duração deve ser maior que zero[/red]")
    else:
        console.print(f"[red]Erro: {e}[/red]")
