"""HabitInstanceService - Sprint 2.1 Integration com EventReorderingService."""
from datetime import date, time, timedelta
from typing import Optional
from sqlmodel import Session, select

from ..database.engine import get_engine_context
from ..models.habit import Habit, Recurrence
from ..models.habit_instance import HabitInstance
from .event_reordering_service import EventReorderingService


class HabitInstanceService:
    """Gerencia instâncias de hábitos com suporte a reordenamento."""
    
    @staticmethod
    def adjust_instance_time(
        instance_id: int,
        new_start: time,
        new_end: time,
    ) -> tuple[Optional[HabitInstance], Optional["ReorderingProposal"]]:
        """Ajusta horário de instância e detecta conflitos.
        
        Args:
            instance_id: ID da instância
            new_start: Novo horário de início
            new_end: Novo horário de fim
            
        Returns:
            Tupla (instância atualizada, proposta de reordenamento ou None)
            
        Raises:
            ValueError: Se start >= end
        """
        if new_start >= new_end:
            raise ValueError("Start time must be before end time")

        with get_engine_context() as engine, Session(engine) as session:
            instance = session.get(HabitInstance, instance_id)
            if not instance:
                return None, None

            instance.scheduled_start = new_start
            instance.scheduled_end = new_end
            instance.manually_adjusted = True
            instance.user_override = True

            session.add(instance)
            session.commit()
            session.refresh(instance)
            
            # Detectar conflitos causados pelo ajuste
            conflicts = EventReorderingService.detect_conflicts(
                triggered_event_id=instance_id,
                event_type="habit_instance"
            )
            
            proposal = None
            if conflicts:
                proposal = EventReorderingService.propose_reordering(conflicts)
            
            return instance, proposal
    
    @staticmethod
    def mark_completed(
        instance_id: int
    ) -> tuple[Optional[HabitInstance], Optional["ReorderingProposal"]]:
        """Marca instância como completa."""
        with get_engine_context() as engine, Session(engine) as session:
            instance = session.get(HabitInstance, instance_id)
            if not instance:
                return None, None
            
            instance.status = "completed"
            session.add(instance)
            session.commit()
            session.refresh(instance)
            
            return instance, None
    
    @staticmethod
    def generate_instances(
        habit_id: int,
        start_date: date,
        end_date: date
    ) -> list[HabitInstance]:
        """Gera instâncias para período."""
        with get_engine_context() as engine, Session(engine) as session:
            habit = session.get(Habit, habit_id)
            if not habit:
                return []
            
            instances = []
            current_date = start_date
            
            while current_date <= end_date:
                should_create = HabitInstanceService._should_create_for_date(
                    habit.recurrence, current_date
                )
                
                if should_create:
                    existing = session.exec(
                        select(HabitInstance).where(
                            HabitInstance.habit_id == habit_id,
                            HabitInstance.date == current_date
                        )
                    ).first()
                    
                    if not existing:
                        instance = HabitInstance(
                            habit_id=habit_id,
                            date=current_date,
                            scheduled_start=habit.start_time,
                            scheduled_end=habit.end_time,
                            status="pending"
                        )
                        session.add(instance)
                        instances.append(instance)
                
                current_date += timedelta(days=1)
            
            session.commit()
            
            for instance in instances:
                session.refresh(instance)
            
            return instances
    
    @staticmethod
    def _should_create_for_date(recurrence: Recurrence, date: date) -> bool:
        """Verifica se deve criar instância para data."""
        if recurrence == Recurrence.DAILY:
            return True
        elif recurrence == Recurrence.WEEKDAYS:
            return date.weekday() < 5
        elif recurrence == Recurrence.WEEKENDS:
            return date.weekday() >= 5
        elif recurrence == Recurrence.WEEKLY:
            return date.weekday() == 0
        return False
