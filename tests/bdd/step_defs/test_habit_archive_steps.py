"""Step definitions para o ciclo do archive de Habit (BR-HABIT-005/006).

Conecta os cenários de tests/bdd/features/habit_archive.feature ao código.
Cobre archive (soft delete preserva histórico), exclusão das listagens e a
confirmação literal com purge.

Referências:
    - ADR-057: Archive Lifecycle para Habit
    - BR-HABIT-005 / BR-HABIT-006
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING

import pytest
from pytest_bdd import given, scenarios, then, when
from sqlmodel import Session, select
from typer.testing import CliRunner

from timeblock.commands import habit as habit_commands
from timeblock.main import app
from timeblock.models import Habit, HabitInstance, Recurrence, Routine, TimeLog
from timeblock.models.enums import Status
from timeblock.services.habit_service import HabitService

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch
    from sqlalchemy.engine import Engine

scenarios("../features/habit_archive.feature")

HISTORY_DAYS = 30


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_engine_context(test_engine: Engine, monkeypatch: MonkeyPatch) -> None:
    """Faz os comandos CLI de habit usarem o engine de teste."""

    @contextmanager
    def mock_get_engine_context():
        yield test_engine

    monkeypatch.setattr(habit_commands.crud, "get_engine_context", mock_get_engine_context)


def _active_routine(session: Session) -> Routine:
    routine = Routine(name="Rotina Matinal", is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


def _make_habit(session: Session, routine_id: int, title: str = "Leitura matinal") -> Habit:
    habit = Habit(
        routine_id=routine_id,
        title=title,
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


# --- Cenário 1: Archive preserves history ---


@given("a habit with 30 days of TimeLog history", target_fixture="history_habit")
def habit_with_history(session: Session) -> Habit:
    routine = _active_routine(session)
    assert routine.id is not None
    habit = _make_habit(session, routine.id)
    assert habit.id is not None

    today = date.today()
    for offset in range(HISTORY_DAYS):
        instance = HabitInstance(
            habit_id=habit.id,
            date=today - timedelta(days=offset),
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            status=Status.DONE,
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)
        session.add(TimeLog(habit_instance_id=instance.id, start_time=datetime.now()))
        session.commit()

    return habit


@when("I delete the habit")
def delete_history_habit(session: Session, history_habit: Habit) -> None:
    assert history_habit.id is not None
    HabitService(session).delete_habit(history_habit.id)


@then("the habit is marked as archived")
def habit_is_archived(session: Session, history_habit: Habit) -> None:
    session.expire_all()
    refreshed = session.get(Habit, history_habit.id)
    assert refreshed is not None
    assert refreshed.archived_at is not None


@then("all 30 TimeLog entries remain intact")
def timelogs_intact(session: Session, history_habit: Habit) -> None:
    instance_ids = [
        i.id
        for i in session.exec(
            select(HabitInstance).where(HabitInstance.habit_id == history_habit.id)
        ).all()
    ]
    logs = session.exec(select(TimeLog).where(TimeLog.habit_instance_id.in_(instance_ids))).all()  # type: ignore[attr-defined]
    assert len(logs) == HISTORY_DAYS


@then("the streak calculation for the past period remains correct")
def streak_remains_correct(session: Session, history_habit: Habit) -> None:
    # Não há service de streak; validamos a integridade dos dados que o streak
    # consome: a sequência de instâncias DONE sobrevive intacta ao archive.
    instances = session.exec(
        select(HabitInstance)
        .where(HabitInstance.habit_id == history_habit.id)
        .order_by(HabitInstance.date.desc())  # type: ignore[attr-defined]
    ).all()
    streak = 0
    for instance in instances:
        if instance.status == Status.DONE:
            streak += 1
        else:
            break
    assert streak == HISTORY_DAYS


# --- Cenário 2: Archived habit excluded from listing ---


@given("an archived habit", target_fixture="archived_habit")
def archived_habit(session: Session) -> Habit:
    routine = _active_routine(session)
    assert routine.id is not None
    habit = _make_habit(session, routine.id, title="Hábito Arquivado")
    assert habit.id is not None
    service = HabitService(session)
    service.delete_habit(habit.id)
    return habit


@when("I list habits")
def list_habits_default(session: Session, cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(app, ["habit", "list"])
    session.info["list_default"] = result.stdout


@then("the archived habit is not shown")
def archived_not_shown(session: Session, archived_habit: Habit) -> None:
    assert archived_habit.title not in session.info["list_default"]


@when("I list habits with --all flag")
def list_habits_all(session: Session, cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(app, ["habit", "list", "--all"])
    session.info["list_all"] = result.stdout


@then("the archived habit appears with archive timestamp")
def archived_shown_with_timestamp(session: Session, archived_habit: Habit) -> None:
    output = session.info["list_all"]
    assert archived_habit.title in output
    assert "arquivado em" in output.lower()


# --- Cenário 3: Purge requires explicit confirmation ---


@given(
    "an archived habit with associated instances and timelogs",
    target_fixture="purge_habit_data",
)
def archived_habit_with_data(session: Session) -> Habit:
    routine = _active_routine(session)
    assert routine.id is not None
    habit = _make_habit(session, routine.id, title="Para Purgar")
    assert habit.id is not None

    instance = HabitInstance(
        habit_id=habit.id,
        date=date.today(),
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    session.add(TimeLog(habit_instance_id=instance.id, start_time=datetime.now()))
    session.commit()

    HabitService(session).delete_habit(habit.id)
    return habit


@when('I run "habit purge" command')
def run_purge(session: Session, cli_runner: CliRunner, purge_habit_data: Habit) -> None:
    result = cli_runner.invoke(app, ["habit", "purge", str(purge_habit_data.id)], input="y\n")
    session.info["purge_output"] = result.stdout
    session.info["purge_exit"] = result.exit_code


@then('I am prompted to type the word "purge" literally')
def prompted_for_purge(session: Session) -> None:
    assert "purge" in session.info["purge_output"].lower()


@when('I type "y" instead of "purge"')
def type_wrong_word() -> None:
    # A entrada "y" já foi fornecida no invoke do passo anterior; este passo
    # documenta a ação do usuário no cenário.
    pass


@then("the operation is aborted")
def operation_aborted(session: Session) -> None:
    assert "cancelad" in session.info["purge_output"].lower()


@then("no data is destroyed")
def no_data_destroyed(session: Session, purge_habit_data: Habit) -> None:
    session.expire_all()
    assert session.get(Habit, purge_habit_data.id) is not None
    instances = session.exec(
        select(HabitInstance).where(HabitInstance.habit_id == purge_habit_data.id)
    ).all()
    assert len(instances) == 1
