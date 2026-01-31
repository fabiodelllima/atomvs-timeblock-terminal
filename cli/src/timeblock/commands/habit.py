"""Comandos para gerenciar hábitos."""

from datetime import date, timedelta
from datetime import time as dt_time

import typer
from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]
from rich.console import Console
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.models import Recurrence
from timeblock.models.enums import SkipReason, Status
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.habit_service import HabitService
from timeblock.services.routine_service import RoutineService
from timeblock.services.timer_service import TimerService
from timeblock.utils.conflict_display import display_conflicts

app = typer.Typer(help="Gerenciar hábitos")
console = Console()


# Sub-app para comandos de instância (atom)
atom_app = typer.Typer(help="Gerenciar instâncias de hábitos")
app.add_typer(atom_app, name="atom")


@app.command("create")
def create_habit(
    title: str = typer.Option(..., "--title", "-t", help="Título do hábito"),
    start: str = typer.Option(..., "--start", "-s", help="Hora início (HH:MM)"),
    end: str = typer.Option(..., "--end", "-e", help="Hora fim (HH:MM)"),
    repeat: str = typer.Option(..., "--repeat", "-r", help="Padrão de repetição"),
    color: str = typer.Option(None, "--color", "-c", help="Cor do hábito"),
    routine: int = typer.Option(None, "--routine", help="ID da rotina (padrão: ativa)"),
    generate: int = typer.Option(None, "--generate", "-g", help="Gerar instâncias (meses)"),
):
    """Cria um novo hábito."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            habit_service = HabitService(session)

            # Determinar rotina
            if routine is None:
                active_routine = routine_service.get_active_routine()
                if active_routine is None:
                    console.print(
                        "[red]Nenhuma rotina ativa. Crie e ative uma rotina primeiro.[/red]"
                    )
                    raise typer.Exit(1)
                console.print(
                    f"Rotina ativa: [bold]{active_routine.name}[/bold] (ID: {active_routine.id})"
                )
                if not typer.confirm("Criar hábito nesta rotina?", default=True):
                    routine_id = typer.prompt("ID da rotina", type=int)
                else:
                    routine_id = active_routine.id
            else:
                routine_id = routine

            # Guard clause - routine_id deve estar definido
            if routine_id is None:
                console.print("[red]Erro: ID da rotina não definido[/red]")
                raise typer.Exit(1)
            # Validar rotina existe
            routine_obj = routine_service.get_routine(routine_id)
            if routine_obj is None:
                console.print(f"[red]Rotina {routine_id} não encontrada[/red]")
                raise typer.Exit(1)

            # Parse recurrence
            try:
                rec = Recurrence(repeat.upper())
            except ValueError:
                valid = ", ".join([r.value for r in Recurrence])
                console.print(f"[red]Recorrência inválida. Use: {valid}[/red]")
                raise typer.Exit(1)

            # Parse times
            start_time = dt_time.fromisoformat(start)
            end_time = dt_time.fromisoformat(end)

            # Guard clause - routine_id validado
            if routine_id is None:
                console.print("[red]Erro interno: routine_id inválido[/red]")
                raise typer.Exit(1)
            # Criar hábito
            habit = habit_service.create_habit(
                routine_id=routine_id,
                title=title,
                scheduled_start=start_time,
                scheduled_end=end_time,
                recurrence=rec,
                color=color,
            )

            console.print("\n[green]Hábito criado com sucesso![/green]\n")
            console.print(f"ID: [cyan]{habit.id}[/cyan]")
            console.print(f"Título: [bold]{habit.title}[/bold]")
            console.print(
                f"Horário: {habit.scheduled_start.strftime('%H:%M')} - {habit.scheduled_end.strftime('%H:%M')}"
            )
            console.print(f"Recorrência: {habit.recurrence.value}")

            if generate:
                start_date = date.today()
                end_date = start_date + relativedelta(months=generate)

                assert habit.id is not None, "Habit must be persisted before generating instances"
                instances = HabitInstanceService.generate_instances(
                    habit_id=habit.id,
                    start_date=start_date,
                    end_date=end_date,
                )
                console.print(f"\n[green]{len(instances)} instâncias geradas[/green]")

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_habits(
    routine: str = typer.Option("active", "--routine", "-R", help="Filtrar: active, all ou ID"),
):
    """Lista hábitos."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            routine_service = RoutineService(session)
            habit_service = HabitService(session)

            # Determinar rotina
            if routine == "active":
                active_routine = routine_service.get_active_routine()
                if active_routine is None:
                    console.print("[red]Nenhuma rotina ativa[/red]")
                    raise typer.Exit(1)
                routine_id: int | None = active_routine.id
                title = f"Hábitos - {active_routine.name} (ativa)"
            elif routine == "all":
                routine_id = None
                title = "Todos os Hábitos"
            else:
                routine_id = int(routine)
                routine_obj = routine_service.get_routine(routine_id)
                if routine_obj is None:
                    console.print(f"[red]Rotina {routine_id} não encontrada[/red]")
                    raise typer.Exit(1)
                title = f"Hábitos - {routine_obj.name}"

            # Buscar hábitos
            habits = habit_service.list_habits(routine_id)

            if not habits:
                console.print("[yellow]Nenhum hábito encontrado.[/yellow]")
                return

            console.print(f"\n[bold]{title}[/bold]\n")
            for h in habits:
                rec = h.recurrence.value.replace("_", " ").title()
                console.print(
                    f"[cyan]{h.id}[/cyan] [bold]{h.title}[/bold] "
                    f"({rec} {h.scheduled_start.strftime('%H:%M')}-{h.scheduled_end.strftime('%H:%M')})"
                )
            console.print()

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("update")
def update_habit(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    title: str = typer.Option(None, "--title", "-t", help="Novo título"),
    start: str = typer.Option(None, "--start", "-s", help="Nova hora início (HH:MM)"),
    end: str = typer.Option(None, "--end", "-e", help="Nova hora fim (HH:MM)"),
    repeat: str = typer.Option(None, "--repeat", "-r", help="Novo padrão"),
    color: str = typer.Option(None, "--color", "-c", help="Nova cor"),
):
    """Atualiza um hábito."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            habit_service = HabitService(session)

            habit = habit_service.get_habit(habit_id)
            if habit is None:
                console.print(f"[red]Hábito {habit_id} não encontrado[/red]")
                raise typer.Exit(1)

            updates: dict = {}
            if title:
                updates["title"] = title
            if start:
                updates["scheduled_start"] = dt_time.fromisoformat(start)
            if end:
                updates["scheduled_end"] = dt_time.fromisoformat(end)
            if repeat:
                try:
                    updates["recurrence"] = Recurrence(repeat.upper())
                except ValueError:
                    valid = ", ".join([r.value for r in Recurrence])
                    console.print(f"[red]Recorrência inválida. Use: {valid}[/red]")
                    raise typer.Exit(1)
            if color:
                updates["color"] = color

            if not updates:
                console.print("[yellow]Nenhuma alteração especificada.[/yellow]")
                return

            habit_service.update_habit(habit_id, **updates)
            console.print(f"[green]Hábito atualizado: [bold]{habit.title}[/bold][/green]")

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("delete")
def delete_habit(
    habit_id: int = typer.Argument(..., help="ID do hábito"),
    force: bool = typer.Option(False, "--force", "-f", help="Não pedir confirmação"),
):
    """Deleta um hábito."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            habit_service = HabitService(session)

            habit = habit_service.get_habit(habit_id)
            if habit is None:
                console.print(f"[red]Hábito {habit_id} não encontrado[/red]")
                raise typer.Exit(1)

            if not force:
                if not typer.confirm(f"Deletar hábito '{habit.title}'?", default=False):
                    console.print("[yellow]Cancelado.[/yellow]")
                    return

            habit_service.delete_habit(habit_id)
            console.print(f"[green]Hábito deletado: [bold]{habit.title}[/bold][/green]")

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("adjust")
def adjust_instance(
    instance_id: int = typer.Argument(..., help="ID da instância"),
    start: str = typer.Option(..., "--start", "-s", help="Nova hora início (HH:MM)"),
    end: str = typer.Option(..., "--end", "-e", help="Nova hora fim (HH:MM)"),
):
    """
    Ajusta horário de instância específica de hábito.

    Este comando modifica apenas a instância especificada. O hábito na rotina
    e outras instâncias permanecem inalterados.
    """
    try:
        new_start = dt_time.fromisoformat(start)
        new_end = dt_time.fromisoformat(end)

        _instance, conflicts = HabitInstanceService.adjust_instance_time(
            instance_id, new_start, new_end
        )

        console.print(f"[green]Instância {instance_id} ajustada: {new_start} - {new_end}[/green]")

        # Exibir conflitos se houver
        if conflicts:
            console.print("\n[yellow]Atenção: O ajuste resultou em conflitos:[/yellow]")
            display_conflicts(conflicts, console)

    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


@app.command("skip")
def skip_instance(
    instance_id: int = typer.Argument(..., help="ID da instância do hábito"),
    category: str = typer.Option(
        None,
        "--category",
        "-c",
        help="Categoria do skip (HEALTH|WORK|FAMILY|TRAVEL|WEATHER|LACK_RESOURCES|EMERGENCY|OTHER)",
    ),
    note: str = typer.Option(None, "--note", "-n", help="Nota opcional (máx 500 chars)"),
):
    """
    Marca instância de hábito como skipped (pulada) com categorização.

    Exemplos:
        timeblock habit skip 42 --category WORK --note "Reunião urgente"
        timeblock habit skip 42 --category HEALTH
    """
    try:
        # Validar categoria
        if category is None:
            console.print("[red]Categoria obrigatória. Use --category[/red]")
            console.print("\nCategorias válidas:")
            console.print("  HEALTH, WORK, FAMILY, TRAVEL, WEATHER,")
            console.print("  LACK_RESOURCES, EMERGENCY, OTHER")
            raise typer.Exit(1)

        # Converter categoria string para enum
        try:
            skip_reason = SkipReason[category.upper()]
        except KeyError:
            console.print(f"[red]Categoria inválida: {category}[/red]")
            console.print("\nCategorias válidas:")
            console.print("  HEALTH, WORK, FAMILY, TRAVEL, WEATHER,")
            console.print("  LACK_RESOURCES, EMERGENCY, OTHER")
            raise typer.Exit(1)

        # Validar tamanho da nota
        if note and len(note) > 500:
            console.print("[red]Nota muito longa (máximo 500 caracteres)[/red]")
            raise typer.Exit(1)

        # Executar skip
        with get_engine_context() as engine, Session(engine) as session:
            service = HabitInstanceService()
            service.skip_habit_instance(
                habit_instance_id=instance_id,
                skip_reason=skip_reason,
                skip_note=note,
                session=session,
            )

            # Mapear enum para português
            category_pt = {
                "health": "Saúde",
                "work": "Trabalho",
                "family": "Família",
                "travel": "Viagem",
                "weather": "Clima",
                "lack_resources": "Falta de recursos",
                "emergency": "Emergência",
                "other": "Outro",
            }

            console.print("[green]Hábito marcado como skipped[/green]")
            console.print(f"  Categoria: {category_pt.get(skip_reason.value, skip_reason.value)}")
            if note:
                console.print(f"  Nota: {note}")

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            console.print(f"[red]HabitInstance {instance_id} não encontrada[/red]")
            raise typer.Exit(2)
        elif "timer" in error_msg.lower():
            console.print("[red]Pare o timer antes de marcar skip[/red]")
            raise typer.Exit(1)
        elif "completed" in error_msg.lower():
            console.print("[red]Não é possível skip de instância completada[/red]")
            raise typer.Exit(1)
        else:
            console.print(f"[red]Erro: {e}[/red]")
            raise typer.Exit(1)


# ============================================================
# Comandos atom (instâncias)
# ============================================================


@atom_app.command("list")
def atom_list(
    habit_id: int = typer.Argument(None, help="Filtrar por ID do hábito"),
    today: bool = typer.Option(False, "--today", "-T", help="Apenas hoje"),
    week: bool = typer.Option(False, "--week", "-w", help="Semana atual"),
    pending: bool = typer.Option(False, "--pending", "-P", help="Apenas PENDING"),
    done: bool = typer.Option(False, "--done", "-C", help="Apenas DONE"),
    all_status: bool = typer.Option(False, "--all", "-a", help="Todos status"),
):
    """
    Lista instâncias de hábitos (BR-HABITINSTANCE-006).

    Defaults:
        Sem flags: semana atual, apenas pendentes
        Com HABIT_ID: todas datas, todos status

    Exemplos:
        timeblock habit atom list              # Semana, pendentes
        timeblock habit atom list 1            # Todas do hábito 1
        timeblock habit atom list -T           # Hoje, todos status
        timeblock habit atom list -T -C        # Hoje, completadas
    """
    try:
        with get_engine_context() as engine, Session(engine) as session:
            service = HabitInstanceService()

            # Determinar período
            date_start = None
            date_end = None

            if today and week:
                console.print("[red]Erro: --today e --week são mutuamente exclusivos[/red]")
                raise typer.Exit(1)

            if today:
                date_start = date.today()
                date_end = date.today()
            elif week or (habit_id is None and not today):
                # Default: semana atual quando sem HABIT_ID
                date_start = date.today()
                date_end = date.today() + timedelta(days=6)

            # Determinar filtro de status
            status_filter = None
            if pending and done:
                console.print("[red]Erro: --pending e --done são mutuamente exclusivos[/red]")
                raise typer.Exit(1)

            if pending:
                status_filter = Status.PENDING
            elif done:
                status_filter = Status.DONE
            elif not all_status and habit_id is None:
                # Default: apenas pendentes quando sem HABIT_ID
                status_filter = Status.PENDING

            # Buscar instâncias
            instances = service.list_instances(
                habit_id=habit_id,
                date_start=date_start,
                date_end=date_end,
                session=session,
            )

            # Filtrar por status se necessário
            if status_filter is not None:
                instances = [i for i in instances if i.status == status_filter]

            if not instances:
                if habit_id:
                    console.print(f"Nenhuma instância encontrada para hábito {habit_id}.")
                else:
                    console.print("Nenhuma instância encontrada.")
                return

            # Agrupar por data
            instances_by_date: dict[date, list] = {}
            for inst in instances:
                if inst.date not in instances_by_date:
                    instances_by_date[inst.date] = []
                instances_by_date[inst.date].append(inst)

            # Exibir
            period_desc = (
                "hoje" if today else "semana atual" if week or habit_id is None else "todas"
            )
            status_desc = (
                "pendentes"
                if status_filter == Status.PENDING
                else "concluídas"
                if status_filter == Status.DONE
                else "todos status"
            )
            console.print(f"\n[bold]Instâncias ({period_desc}, {status_desc}):[/bold]\n")

            for dt in sorted(instances_by_date.keys()):
                weekday = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][
                    dt.weekday()
                ]
                console.print(f"[cyan]{weekday}, {dt.strftime('%d/%m')}:[/cyan]")

                for inst in sorted(instances_by_date[dt], key=lambda x: x.scheduled_start):
                    # Determinar marcador de status
                    if inst.status == Status.DONE:
                        marker = "[green][x][/green]"
                        status_text = "concluída"
                    elif inst.status == Status.NOT_DONE:
                        marker = "[red][-][/red]"
                        status_text = "não concluída"
                    else:
                        marker = "[ ]"
                        status_text = "pendente"

                    start = inst.scheduled_start.strftime("%H:%M")
                    end = inst.scheduled_end.strftime("%H:%M")
                    title = inst.habit.title if inst.habit else f"Hábito #{inst.habit_id}"

                    console.print(
                        f"  {marker} {start}-{end} {title} [dim](ID: {inst.id}, {status_text})[/dim]"
                    )

                console.print()

    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)


@atom_app.command("log")
def atom_log(
    instance_id: int = typer.Argument(..., help="ID da instância"),
    start: str = typer.Option(None, "--start", "-s", help="Hora início (HH:MM)"),
    end: str = typer.Option(None, "--end", "-e", help="Hora fim (HH:MM)"),
    duration: int = typer.Option(None, "--duration", "-d", help="Duração em minutos"),
):
    """
    Registra tempo manualmente sem usar timer (BR-TIMER-007).

    Dois modos mutuamente exclusivos:
        - Intervalo: --start HH:MM --end HH:MM
        - Duração: --duration MINUTOS

    Exemplos:
        timeblock habit atom log 42 --start 07:00 --end 08:00
        timeblock habit atom log 42 --duration 60
    """
    try:
        # Validar modos mutuamente exclusivos (BR-CLI-001)
        has_interval = start is not None or end is not None
        has_duration = duration is not None

        if has_interval and has_duration:
            console.print("[red]Erro: não pode combinar --start/--end com --duration[/red]")
            console.print("\nUse um dos modos:")
            console.print("  Intervalo: --start HH:MM --end HH:MM")
            console.print("  Duração:   --duration MINUTOS")
            raise typer.Exit(1)

        if not has_interval and not has_duration:
            console.print(
                "[red]Erro: forneça intervalo (--start/--end) ou duração (--duration)[/red]"
            )
            console.print("\nExemplos:")
            console.print("  timeblock habit atom log 42 --start 07:00 --end 08:00")
            console.print("  timeblock habit atom log 42 --duration 60")
            raise typer.Exit(1)

        # Validar par start/end
        if has_interval:
            if start is None or end is None:
                console.print("[red]Erro: --start requer --end (e vice-versa)[/red]")
                raise typer.Exit(1)

        # Converter horários
        start_time = None
        end_time = None
        if start:
            try:
                parts = start.split(":")
                start_time = dt_time(int(parts[0]), int(parts[1]))
            except (ValueError, IndexError):
                console.print(f"[red]Formato inválido para --start: {start}[/red]")
                console.print("Use formato HH:MM (ex: 07:00, 14:30)")
                raise typer.Exit(1)

        if end:
            try:
                parts = end.split(":")
                end_time = dt_time(int(parts[0]), int(parts[1]))
            except (ValueError, IndexError):
                console.print(f"[red]Formato inválido para --end: {end}[/red]")
                console.print("Use formato HH:MM (ex: 08:00, 15:30)")
                raise typer.Exit(1)

        # Executar log manual
        with get_engine_context() as engine, Session(engine) as session:
            service = TimerService()
            timelog = service.log_manual(
                habit_instance_id=instance_id,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration,
                session=session,
            )

            # Buscar instância para feedback
            instance_service = HabitInstanceService()
            instance = instance_service.get_instance(instance_id, session=session)

            # Formatar duração
            duration_secs = timelog.duration_seconds or 0
            hours, remainder = divmod(duration_secs, 3600)
            minutes = remainder // 60

            # Mapear substatus para português
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

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            console.print(f"[red]HabitInstance {instance_id} não encontrada[/red]")
            raise typer.Exit(2)
        elif "start must be before end" in error_msg:
            console.print("[red]Erro: hora início deve ser anterior à hora fim[/red]")
            raise typer.Exit(1)
        elif "duration must be positive" in error_msg:
            console.print("[red]Erro: duração deve ser maior que zero[/red]")
            raise typer.Exit(1)
        else:
            console.print(f"[red]Erro: {e}[/red]")
            raise typer.Exit(1)
