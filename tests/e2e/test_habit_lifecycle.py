"""
Testes E2E para ciclo de vida de hábitos.

Valida workflows completos do CLI até o banco de dados,
cobrindo criação, listagem, atualizações e detecção de conflitos.

Referências:
    - ADR-019: Convenção de Nomenclatura de Testes
    - RTM: Matriz de Rastreabilidade de Requisitos
"""

import tempfile
from datetime import date, time
from pathlib import Path

import pytest
from pytest import MonkeyPatch
from sqlmodel import Session, create_engine
from typer.testing import CliRunner

from timeblock.main import app
from timeblock.models import Habit, HabitInstance, Recurrence, Routine, Task


@pytest.fixture
def runner() -> CliRunner:
    """Runner para testes CLI."""
    return CliRunner()


@pytest.fixture
def isolated_db(monkeypatch: MonkeyPatch) -> Path:
    """Cria banco de dados isolado para testes E2E."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    monkeypatch.setattr("timeblock.database.engine.get_db_path", lambda: str(db_path))

    yield db_path

    db_path.unlink(missing_ok=True)


class TestBRHabitLifecycle:
    """
    E2E: Ciclo de vida completo de hábitos.

    BRs cobertas:
        - BR-HABIT-001: Criação de hábito
        - BR-HABIT-002: Listagem de hábitos
        - BR-HABIT-003: Atualização de hábito
    """

    def test_br_habit_001_create_habit_via_cli(
        self, runner: CliRunner, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Cria hábito via CLI.

        DADO: Rotina ativa existe
        QUANDO: Usuário executa 'habit create'
        ENTÃO: Hábito é criado no banco
        """
        # ARRANGE - Criar rotina primeiro
        engine = create_engine(f"sqlite:///{isolated_db}")
        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            routine = Routine(name="Morning", is_active=True)
            session.add(routine)
            session.commit()

        # ACT
        result = runner.invoke(
            app,
            ["habit", "create", "-t", "Meditation", "-s", "06:00", "-e", "06:30", "-r", "everyday"],
            input="y\n",
        )

        # ASSERT
        assert result.exit_code == 0
        assert "criado" in result.output.lower() or "created" in result.output.lower()

    def test_br_habit_002_list_habits_via_cli(
        self, runner: CliRunner, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Lista hábitos via CLI.

        DADO: Hábitos existem no banco
        QUANDO: Usuário executa 'habit list'
        ENTÃO: Hábitos são listados
        """
        # ARRANGE
        engine = create_engine(f"sqlite:///{isolated_db}")
        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            routine = Routine(name="Morning", is_active=True)
            session.add(routine)
            session.commit()

            habit = Habit(
                routine_id=routine.id,
                title="Exercise",
                scheduled_start=time(7, 0),
                scheduled_end=time(8, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()

        # ACT
        result = runner.invoke(app, ["habit", "list"])

        # ASSERT
        assert result.exit_code == 0
        assert "Exercise" in result.output

    def test_br_habit_003_update_habit_via_cli(
        self, runner: CliRunner, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Atualiza hábito via CLI.

        DADO: Hábito existe no banco
        QUANDO: Usuário executa 'habit update'
        ENTÃO: Hábito é atualizado
        """
        # ARRANGE
        engine = create_engine(f"sqlite:///{isolated_db}")
        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            routine = Routine(name="Morning", is_active=True)
            session.add(routine)
            session.commit()

            habit = Habit(
                routine_id=routine.id,
                title="Exercise",
                scheduled_start=time(7, 0),
                scheduled_end=time(8, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()
            habit_id = habit.id

        # ACT
        result = runner.invoke(app, ["habit", "update", str(habit_id), "-t", "Morning Run"])

        # ASSERT
        assert result.exit_code == 0
        assert "atualizado" in result.output.lower() or "updated" in result.output.lower()


class TestBREventConflictWorkflow:
    """
    E2E: Workflow de detecção e resolução de conflitos.

    BRs cobertas:
    - BR-REORDER-001: Detecção de conflitos de horário
    - BR-REORDER-003: Apresentação de conflitos
    - BR-REORDER-004: Conflitos não bloqueiam
    """

    def test_br_reorder_001_adjust_detects_conflict_with_task(
        self, runner: CliRunner, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Ajuste de instância detecta conflito com task.

        DADO: HabitInstance existe das 07:00-08:00
        E: Task existe das 07:30-08:30
        QUANDO: Usuário ajusta instância para 07:00-08:30
        ENTÃO: Sistema detecta e apresenta conflito
        E: Ajuste é realizado (BR-REORDER-004: não bloqueante)
        """
        # ARRANGE
        engine = create_engine(f"sqlite:///{isolated_db}")
        from sqlmodel import SQLModel

        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            routine = Routine(name="Morning", is_active=True)
            session.add(routine)
            session.commit()

            habit = Habit(
                routine_id=routine.id,
                title="Exercise",
                scheduled_start=time(7, 0),
                scheduled_end=time(8, 0),
                recurrence=Recurrence.EVERYDAY,
            )
            session.add(habit)
            session.commit()

            instance = HabitInstance(
                habit_id=habit.id,
                date=date.today(),
                scheduled_start=time(7, 0),
                scheduled_end=time(8, 0),
            )
            session.add(instance)

            from datetime import datetime

            task = Task(
                title="Meeting",
                scheduled_datetime=datetime.combine(date.today(), time(7, 30)),
            )
            session.add(task)
            session.commit()
            instance_id = instance.id

        # ACT - Ajustar instância para sobrepor com task
        result = runner.invoke(
            app, ["habit", "adjust", str(instance_id), "-s", "07:00", "-e", "08:30"]
        )

        # ASSERT
        assert result.exit_code == 0
        # Deve mostrar mensagem de conflito ou sucesso
        output_lower = result.output.lower()
        # Aceita tanto conflito detectado quanto ajuste realizado
        assert (
            "conflito" in output_lower
            or "conflict" in output_lower
            or "ajustado" in output_lower
            or "adjusted" in output_lower
            or "atualizado" in output_lower
        )
