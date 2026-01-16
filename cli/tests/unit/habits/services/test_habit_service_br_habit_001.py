"""
Testes para BR-HABIT-001: Criação de Hábitos em Rotinas.

Este arquivo serve como TEMPLATE para refactoring de testes existentes.
Demonstra o padrão completo a ser seguido em todo o projeto.

Referências:
    - BR: docs/04-specifications/business-rules/habit-instances.md#br-habit-001
    - ADR: docs/03-decisions/ADR-019-test-naming-convention.md
    - RTM: docs/05-testing/requirements-traceability-matrix.md
"""

from datetime import time

import pytest
from sqlmodel import Session

from timeblock.models import Recurrence, Routine
from timeblock.services.habit_service import HabitService


@pytest.fixture
def test_routine(session: Session) -> Routine:
    """
    Cria rotina de teste.

    Necessária pois BR-HABIT-001 especifica que hábitos devem
    pertencer a uma rotina válida.
    """
    routine = Routine(name="Rotina Teste", is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


class TestBRHabit001Creation:
    """
    Suite de testes para BR-HABIT-001: Criação de Hábitos em Rotinas.

    Valida todos os cenários de criação de hábitos conforme especificado
    na Business Rule, incluindo validações de título, horários e recorrência.

    Cenários cobertos:
    - Criação com dados válidos (caminho feliz)
    - Criação com campos opcionais
    - Validações de título (vazio, whitespace, tamanho)
    - Validações de horário (início >= fim)

    Referências:
        - BR-HABIT-001: docs/04-specifications/business-rules/habit-instances.md
        - Código: src/timeblock/services/habit_service.py::create_habit
    """

    def test_br_habit_001_creates_successfully(
        self, session: Session, test_routine: Routine
    ) -> None:
        """
        BR-HABIT-001: Sistema cria hábito quando dados válidos são fornecidos.

        DADO: Uma rotina válida existe no sistema
        QUANDO: Usuário fornece título, horário de início/fim e recorrência válidos
        ENTÃO: Hábito é criado com ID único e atributos corretos
        E: Hábito é associado à rotina especificada
        """
        assert test_routine.id is not None
        habit_service = HabitService(session)
        title = "Exercício Matinal"
        start = time(6, 0)
        end = time(7, 0)
        recurrence = Recurrence.EVERYDAY

        habit = habit_service.create_habit(
            routine_id=test_routine.id,
            title=title,
            scheduled_start=start,
            scheduled_end=end,
            recurrence=recurrence,
        )

        assert habit.id is not None, "Hábito deve ter ID após criação"
        assert habit.routine_id == test_routine.id
        assert habit.title == title
        assert habit.scheduled_start == start
        assert habit.scheduled_end == end
        assert habit.recurrence == recurrence

    def test_br_habit_001_creates_with_optional_color(
        self, session: Session, test_routine: Routine
    ) -> None:
        """
        BR-HABIT-001: Sistema cria hábito com campo opcional color.

        DADO: Rotina válida existe
        QUANDO: Usuário fornece cor hexadecimal opcional
        ENTÃO: Hábito é criado com cor especificada
        """
        assert test_routine.id is not None
        habit_service = HabitService(session)
        color = "#FF5733"

        habit = habit_service.create_habit(
            routine_id=test_routine.id,
            title="Meditação",
            scheduled_start=time(6, 0),
            scheduled_end=time(6, 30),
            recurrence=Recurrence.WEEKDAYS,
            color=color,
        )

        assert habit.color == color

    def test_br_habit_001_strips_title_whitespace(
        self, session: Session, test_routine: Routine
    ) -> None:
        """
        BR-HABIT-001: Sistema remove espaços em branco do título.

        DADO: Rotina válida existe
        QUANDO: Usuário fornece título com espaços no início/fim
        ENTÃO: Título é armazenado sem espaços extras
        """
        assert test_routine.id is not None
        habit_service = HabitService(session)
        title_with_spaces = "  Leitura  "
        expected_title = "Leitura"

        habit = habit_service.create_habit(
            routine_id=test_routine.id,
            title=title_with_spaces,
            scheduled_start=time(20, 0),
            scheduled_end=time(21, 0),
            recurrence=Recurrence.EVERYDAY,
        )

        assert habit.title == expected_title

    def test_br_habit_001_rejects_empty_title(
        self, session: Session, test_routine: Routine
    ) -> None:
        """
        BR-HABIT-001: Sistema rejeita criação quando título está vazio.

        DADO: Rotina válida existe
        QUANDO: Usuário tenta criar hábito com título vazio ou apenas espaços
        ENTÃO: ValueError é levantado com mensagem apropriada
        E: Nenhum hábito é persistido no banco de dados
        """
        assert test_routine.id is not None
        habit_service = HabitService(session)
        empty_title = "   "

        with pytest.raises(ValueError, match="cannot be empty"):
            habit_service.create_habit(
                routine_id=test_routine.id,
                title=empty_title,
                scheduled_start=time(10, 0),
                scheduled_end=time(11, 0),
                recurrence=Recurrence.EVERYDAY,
            )

    def test_br_habit_001_rejects_long_title(
        self, session: Session, test_routine: Routine
    ) -> None:
        """
        BR-HABIT-001: Sistema rejeita título que excede 200 caracteres.

        DADO: Rotina válida existe
        QUANDO: Usuário tenta criar hábito com título > 200 caracteres
        ENTÃO: ValueError é levantado
        """
        assert test_routine.id is not None
        habit_service = HabitService(session)
        long_title = "X" * 201

        with pytest.raises(ValueError, match="cannot exceed 200"):
            habit_service.create_habit(
                routine_id=test_routine.id,
                title=long_title,
                scheduled_start=time(10, 0),
                scheduled_end=time(11, 0),
                recurrence=Recurrence.EVERYDAY,
            )

    def test_br_habit_001_rejects_invalid_time_range(
        self, session: Session, test_routine: Routine
    ) -> None:
        """
        BR-HABIT-001: Sistema rejeita quando horário fim é antes do início.

        DADO: Rotina válida existe
        QUANDO: Usuário especifica scheduled_end antes de scheduled_start
        ENTÃO: ValueError é levantado
        """
        assert test_routine.id is not None
        habit_service = HabitService(session)
        start = time(7, 0)
        end = time(6, 0)

        with pytest.raises(ValueError, match="Start time must be before end time"):
            habit_service.create_habit(
                routine_id=test_routine.id,
                title="Inválido",
                scheduled_start=start,
                scheduled_end=end,
                recurrence=Recurrence.EVERYDAY,
            )

    def test_br_habit_001_rejects_equal_start_end(
        self, session: Session, test_routine: Routine
    ) -> None:
        """
        BR-HABIT-001: Sistema rejeita quando início e fim são iguais.

        DADO: Rotina válida existe
        QUANDO: scheduled_start == scheduled_end (duração zero)
        ENTÃO: ValueError é levantado
        """
        assert test_routine.id is not None
        habit_service = HabitService(session)
        same_time = time(6, 0)

        with pytest.raises(ValueError, match="Start time must be before end time"):
            habit_service.create_habit(
                routine_id=test_routine.id,
                title="Zero Duração",
                scheduled_start=same_time,
                scheduled_end=same_time,
                recurrence=Recurrence.EVERYDAY,
            )


class TestBRHabit001Integration:
    """
    Testes de integração para BR-HABIT-001.

    Valida que create_habit funciona corretamente com banco de dados real
    e múltiplas operações sequenciais.
    """

    def test_br_habit_001_creates_multiple_habits(
        self, session: Session, test_routine: Routine
    ) -> None:
        """
        BR-HABIT-001: Sistema permite criar múltiplos hábitos na mesma rotina.

        DADO: Rotina válida existe
        QUANDO: Usuário cria múltiplos hábitos
        ENTÃO: Todos são criados com IDs únicos
        """
        assert test_routine.id is not None
        habit_service = HabitService(session)

        habit1 = habit_service.create_habit(
            routine_id=test_routine.id,
            title="Exercício",
            scheduled_start=time(6, 0),
            scheduled_end=time(7, 0),
            recurrence=Recurrence.EVERYDAY,
        )

        habit2 = habit_service.create_habit(
            routine_id=test_routine.id,
            title="Meditação",
            scheduled_start=time(7, 0),
            scheduled_end=time(7, 30),
            recurrence=Recurrence.EVERYDAY,
        )

        assert habit1.id != habit2.id
        assert habit1.routine_id == habit2.routine_id == test_routine.id
