"""Service para gerenciar rotinas."""

from sqlmodel import Session, select

from ..models.habit import Habit
from ..models.routine import Routine


class RoutineService:
    """
    Service para operações de rotinas.

    Responsabilidades:
    - CRUD de rotinas
    - Ativação/desativação de rotinas
    - Busca de rotina ativa
    - Delete behaviors (soft/hard)

    Business Rules:
    - BR-ROUTINE-001: Single Active Constraint
    - BR-ROUTINE-002: Habit Belongs to Routine
    - BR-ROUTINE-004: Activation Cascade
    """

    def __init__(self, session: Session) -> None:
        """Inicializa service com sessão do banco."""
        self.session = session

    def create_routine(self, name: str, auto_activate: bool = False) -> Routine:
        """
        Cria nova rotina.

        Args:
            name: Nome da rotina
            auto_activate: Se True, ativa rotina (primeira rotina)

        Returns:
            Rotina criada

        Business Rules:
            - BR-ROUTINE-001: Criar rotina não ativa automaticamente
            - BR-ROUTINE-004: Primeira rotina pode ser auto-ativada
        """
        # Verificar se é primeira rotina
        is_first = len(self.session.exec(select(Routine)).all()) == 0

        # Primeira rotina ou auto_activate=True → ativar
        is_active = is_first or auto_activate

        routine = Routine(name=name, is_active=is_active)
        self.session.add(routine)
        self.session.commit()
        self.session.refresh(routine)
        return routine

    def get_routine(self, routine_id: int) -> Routine | None:
        """
        Busca rotina por ID.

        Args:
            routine_id: ID da rotina

        Returns:
            Rotina encontrada ou None
        """
        return self.session.get(Routine, routine_id)

    def get_active_routine(self) -> Routine | None:
        """
        Busca a rotina ativa atual.

        Returns:
            Rotina ativa ou None se não houver rotina ativa

        Business Rules:
            - BR-ROUTINE-001: Apenas uma rotina ativa
            - BR-ROUTINE-004: Rotina ativa define contexto
        """
        statement = select(Routine).where(Routine.is_active)
        result = self.session.exec(statement).first()
        return result

    def list_routines(self, active_only: bool = False) -> list[Routine]:
        """
        Lista rotinas.

        Args:
            active_only: Se True, lista apenas rotinas ativas

        Returns:
            Lista de rotinas
        """
        statement = select(Routine)
        if active_only:
            statement = statement.where(Routine.is_active)

        routines = self.session.exec(statement).all()
        return list(routines)

    def activate_routine(self, routine_id: int) -> Routine:
        """
        Ativa uma rotina e desativa todas as outras.

        Args:
            routine_id: ID da rotina a ativar

        Returns:
            Rotina ativada

        Raises:
            ValueError: Se rotina não existe

        Business Rules:
            - BR-ROUTINE-001: Apenas uma rotina ativa por vez
        """
        # Verificar se rotina existe
        routine = self.session.get(Routine, routine_id)
        if routine is None:
            raise ValueError(f"Rotina {routine_id} não encontrada")

        # Desativar todas
        statement = select(Routine).where(Routine.is_active)
        active_routines = self.session.exec(statement).all()
        for active_routine in active_routines:
            active_routine.is_active = False
            self.session.add(active_routine)

        # Ativar a escolhida
        routine.is_active = True
        self.session.add(routine)
        self.session.commit()
        self.session.refresh(routine)

        return routine

    def deactivate_routine(self, routine_id: int) -> None:
        """
        Desativa uma rotina.

        Args:
            routine_id: ID da rotina a desativar
        """
        routine = self.session.get(Routine, routine_id)
        if routine:
            routine.is_active = False
            self.session.add(routine)
            self.session.commit()

    def delete_routine(self, routine_id: int) -> None:
        """
        Deleta rotina (SOFT DELETE por padrão).

        Define is_active = False, mantém dados no banco.

        Args:
            routine_id: ID da rotina a deletar

        Business Rules:
            - BR-ROUTINE-002: Soft delete por padrão
        """
        routine = self.session.get(Routine, routine_id)
        if routine:
            routine.is_active = False
            self.session.add(routine)
            self.session.commit()

    def hard_delete_routine(self, routine_id: int, force: bool = False) -> None:
        """
        Deleta rotina PERMANENTEMENTE (HARD DELETE).

        MVP: Bloqueia se rotina tiver habits.
        Fase 2: force=True permite cascade delete.

        Args:
            routine_id: ID da rotina a deletar
            force: Se True, permite cascade delete (Fase 2)

        Raises:
            ValueError: Se rotina tem habits e force=False

        Business Rules:
            - BR-ROUTINE-002: Hard delete bloqueia se tiver habits (MVP)
        """
        routine = self.session.get(Routine, routine_id)
        if routine is None:
            raise ValueError(f"Rotina {routine_id} não encontrada")

        # Verificar se tem habits
        habits = self.session.exec(select(Habit).where(Habit.routine_id == routine_id)).all()

        if len(habits) > 0 and not force:
            raise ValueError(
                f"Rotina possui {len(habits)} hábitos. "
                "Não é possível deletar rotina com hábitos (MVP). "
                "Remova os hábitos primeiro ou use force=True (Fase 2)."
            )

        # Hard delete
        self.session.delete(routine)
        self.session.commit()
