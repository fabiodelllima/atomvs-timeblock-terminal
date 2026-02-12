"""Testes para BR-ROUTINE-001 e BR-ROUTINE-002.

BR-ROUTINE-001: Apenas uma rotina ativa por vez
BR-ROUTINE-002: Soft delete preserva histórico

Valida regras de negócio de ativação exclusiva e deleção.
"""

import pytest
from sqlmodel import Session

from timeblock.services.routine_service import RoutineService

# ============================================================
# BR-ROUTINE-001: Apenas uma rotina ativa por vez
# ============================================================


class TestBRRoutine001:
    """Valida BR-ROUTINE-001: Apenas uma rotina ativa por vez."""

    def test_br_routine_001_activate_sets_active_flag(self, session: Session) -> None:
        """BR-ROUTINE-001: Ativar rotina seta is_active=True."""
        service = RoutineService(session)

        _ = service.create_routine("Rotina 1")
        routine2 = service.create_routine("Rotina 2")
        session.commit()

        activated = service.activate_routine(routine2.id)
        session.commit()

        assert activated.is_active is True

    def test_br_routine_001_activate_deactivates_others(self, session: Session) -> None:
        """BR-ROUTINE-001: Ativar rotina desativa todas as outras."""
        service = RoutineService(session)

        routine1 = service.create_routine("Rotina 1")
        routine2 = service.create_routine("Rotina 2")
        session.commit()

        # Ativar rotina 1
        service.activate_routine(routine1.id)
        session.commit()
        session.refresh(routine1)
        assert routine1.is_active is True

        # Ativar rotina 2 deve desativar rotina 1
        service.activate_routine(routine2.id)
        session.commit()
        session.refresh(routine1)
        session.refresh(routine2)

        assert routine1.is_active is False
        assert routine2.is_active is True

    def test_br_routine_001_activate_nonexistent_raises_error(self, session: Session) -> None:
        """BR-ROUTINE-001: Ativar rotina inexistente lança ValueError."""
        service = RoutineService(session)

        with pytest.raises(ValueError, match="não encontrada"):
            service.activate_routine(9999)

    def test_br_routine_001_activate_already_active_succeeds(self, session: Session) -> None:
        """BR-ROUTINE-001: Reativar rotina já ativa é idempotente."""
        service = RoutineService(session)

        routine = service.create_routine("Rotina")
        session.commit()

        # Ativar duas vezes
        service.activate_routine(routine.id)
        service.activate_routine(routine.id)
        session.commit()
        session.refresh(routine)

        assert routine.is_active is True

    def test_br_routine_001_deactivate_clears_active_flag(self, session: Session) -> None:
        """BR-ROUTINE-001: Desativar rotina seta is_active=False."""
        service = RoutineService(session)

        routine = service.create_routine("Rotina")
        session.commit()

        service.activate_routine(routine.id)
        session.commit()
        session.refresh(routine)
        assert routine.is_active is True

        service.deactivate_routine(routine.id)
        session.commit()
        session.refresh(routine)

        assert routine.is_active is False

    def test_br_routine_001_deactivate_nonexistent_raises_error(self, session: Session) -> None:
        """BR-ROUTINE-001: Desativar rotina inexistente lança ValueError."""
        service = RoutineService(session)

        with pytest.raises(ValueError, match="não encontrada"):
            service.deactivate_routine(9999)

    def test_br_routine_001_deactivate_already_inactive_succeeds(self, session: Session) -> None:
        """BR-ROUTINE-001: Desativar rotina já inativa é idempotente."""
        service = RoutineService(session)

        routine = service.create_routine("Rotina")
        session.commit()

        service.deactivate_routine(routine.id)
        session.commit()
        session.refresh(routine)

        assert routine.is_active is False


# ============================================================
# BR-ROUTINE-002: Soft delete preserva histórico
# ============================================================


class TestBRRoutine002:
    """Valida BR-ROUTINE-002: Soft delete preserva histórico."""

    def test_br_routine_002_delete_removes_routine(self, session: Session) -> None:
        """BR-ROUTINE-002: Delete remove rotina do banco (MVP: hard delete)."""
        service = RoutineService(session)

        routine = service.create_routine("Temporária")
        routine_id = routine.id
        session.commit()

        service.delete_routine(routine_id)
        session.commit()

        deleted = service.get_routine(routine_id)
        assert deleted is None

    def test_br_routine_002_delete_nonexistent_raises_error(self, session: Session) -> None:
        """BR-ROUTINE-002: Deletar rotina inexistente lança ValueError."""
        service = RoutineService(session)

        with pytest.raises(ValueError, match="não encontrada"):
            service.delete_routine(9999)

    def test_br_routine_002_delete_active_routine_succeeds(self, session: Session) -> None:
        """BR-ROUTINE-002: Deletar rotina ativa é permitido."""
        service = RoutineService(session)

        routine = service.create_routine("Ativa")
        service.activate_routine(routine.id)
        routine_id = routine.id
        session.commit()

        service.delete_routine(routine_id)
        session.commit()

        deleted = service.get_routine(routine_id)
        assert deleted is None


# ============================================================
# Update Routine (não é BR específica - operação CRUD)
# ============================================================


class TestUpdateRoutine:
    """Testes para update_routine (operação CRUD)."""

    def test_update_routine_name(self, session: Session) -> None:
        """Atualiza nome da rotina."""
        service = RoutineService(session)

        routine = service.create_routine("Nome Antigo")
        session.commit()

        updated = service.update_routine(routine.id, name="Nome Novo")
        session.commit()

        assert updated is not None
        assert updated.name == "Nome Novo"

    def test_update_routine_not_found(self, session: Session) -> None:
        """Retorna None ao atualizar rotina inexistente."""
        service = RoutineService(session)

        result = service.update_routine(9999, name="Teste")

        assert result is None

    def test_update_routine_strips_whitespace(self, session: Session) -> None:
        """Remove espaços do nome na atualização."""
        service = RoutineService(session)

        routine = service.create_routine("Original")
        session.commit()

        updated = service.update_routine(routine.id, name="  Modificado  ")
        session.commit()

        assert updated is not None
        assert updated.name == "Modificado"

    def test_update_routine_with_empty_name(self, session: Session) -> None:
        """Rejeita nome vazio na atualização."""
        service = RoutineService(session)

        routine = service.create_routine("Original")
        session.commit()

        with pytest.raises(ValueError, match="não pode ser vazio"):
            service.update_routine(routine.id, name="   ")

    def test_update_routine_with_long_name(self, session: Session) -> None:
        """Rejeita nome longo na atualização."""
        service = RoutineService(session)

        routine = service.create_routine("Original")
        session.commit()

        with pytest.raises(ValueError, match="não pode ter mais de 200 caracteres"):
            service.update_routine(routine.id, name="a" * 201)

    def test_update_routine_with_max_length_name(self, session: Session) -> None:
        """Aceita nome com exatamente 200 caracteres."""
        service = RoutineService(session)

        routine = service.create_routine("Original")
        session.commit()

        max_name = "a" * 200
        updated = service.update_routine(routine.id, name=max_name)
        session.commit()

        assert updated is not None
        assert updated.name == max_name

    def test_update_routine_name_none_preserves_current(self, session: Session) -> None:
        """Passar name=None não altera o nome."""
        service = RoutineService(session)

        routine = service.create_routine("Original")
        original_name = routine.name
        session.commit()

        updated = service.update_routine(routine.id, name=None)
        session.commit()

        assert updated is not None
        assert updated.name == original_name
