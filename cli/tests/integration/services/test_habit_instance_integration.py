"""Testes Sprint 2.1 - HabitInstanceService + EventReorderingService."""
import pytest
from datetime import date, time
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.habit_service import HabitService
from src.timeblock.services.routine_service import RoutineService
from src.timeblock.models.habit import Recurrence


class TestHabitInstanceReorderingIntegration:
    """Testes de integração HabitInstanceService + EventReorderingService."""
    
    def test_adjust_without_conflicts(self, integration_session):
        """Ajustar sem conflitos retorna None em proposal."""
        routine_service = RoutineService(integration_session)
        routine = routine_service.create_routine("Test")
        
        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Exercise",
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            recurrence=Recurrence.MONDAY
        )
        instances = HabitInstanceService.generate_instances(
            habit.id, date.today(), date.today()
        )
        
        if not instances:
            pytest.skip("Hoje não é segunda-feira")
        
        updated, proposal = HabitInstanceService.adjust_instance_time(
            instances[0].id, time(14, 0), time(15, 0)
        )
        
        assert updated.scheduled_start == time(14, 0)
        assert updated.user_override is True
        assert proposal is None
    
    def test_adjust_with_conflicts(self, integration_session):
        """Ajustar causando conflito retorna proposal."""
        routine_service = RoutineService(integration_session)
        routine = routine_service.create_routine("Test")
        
        habit1 = HabitService.create_habit(
            routine_id=routine.id,
            title="Exercise",
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            recurrence=Recurrence.MONDAY
        )
        habit2 = HabitService.create_habit(
            routine_id=routine.id,
            title="Breakfast",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.MONDAY
        )
        
        instances1 = HabitInstanceService.generate_instances(
            habit1.id, date.today(), date.today()
        )
        instances2 = HabitInstanceService.generate_instances(
            habit2.id, date.today(), date.today()
        )
        
        if not instances1 or not instances2:
            pytest.skip("Hoje não é segunda-feira")
        
        updated, proposal = HabitInstanceService.adjust_instance_time(
            instances1[0].id, time(8, 30), time(9, 30)
        )
        
        assert updated.scheduled_start == time(8, 30)
        assert proposal is not None
        assert len(proposal.conflicts) > 0
    
    def test_mark_completed_no_reorder(self, integration_session):
        """Marcar completo não dispara reordenamento."""
        routine_service = RoutineService(integration_session)
        routine = routine_service.create_routine("Test")
        
        habit = HabitService.create_habit(
            routine_id=routine.id,
            title="Task",
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            recurrence=Recurrence.MONDAY
        )
        instances = HabitInstanceService.generate_instances(
            habit.id, date.today(), date.today()
        )
        
        if not instances:
            pytest.skip("Hoje não é segunda-feira")
        
        updated, proposal = HabitInstanceService.mark_completed(instances[0].id)
        
        assert updated.status == "completed"
        assert proposal is None
