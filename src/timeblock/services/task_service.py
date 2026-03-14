"""Task service com detecção de conflitos e lifecycle (ADR-036)."""

from datetime import datetime

from sqlmodel import Session, col, select

from timeblock.database import get_engine_context
from timeblock.models import Task
from timeblock.utils.logger import get_logger

from .event_reordering_models import Conflict
from .event_reordering_service import EventReorderingService

logger = get_logger(__name__)


class TaskService:
    """Serviço de gerenciamento de tasks (ADR-036)."""

    @staticmethod
    def create_task(
        title: str,
        scheduled_datetime: datetime,
        description: str | None = None,
        color: str | None = None,
        tag_id: int | None = None,
        session: Session | None = None,
    ) -> Task:
        """Cria uma nova task.

        BR-TASK-008: original_scheduled_datetime é fixado com o valor de scheduled_datetime
        na criação e nunca é modificado depois.
        """
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty")
        if len(title) > 200:
            raise ValueError("Title cannot exceed 200 characters")

        def _create(sess: Session) -> Task:
            task = Task(
                title=title,
                scheduled_datetime=scheduled_datetime,
                original_scheduled_datetime=scheduled_datetime,
                description=description,
                color=color,
                tag_id=tag_id,
            )
            sess.add(task)
            sess.commit()
            sess.refresh(task)
            logger.info("Task criada: id=%s, title='%s'", task.id, task.title)
            return task

        if session is not None:
            return _create(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _create(sess)

    @staticmethod
    def get_task(task_id: int, session: Session | None = None) -> Task | None:
        """Retorna task por ID."""

        def _get(sess: Session) -> Task | None:
            return sess.get(Task, task_id)

        if session is not None:
            return _get(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _get(sess)

    @staticmethod
    def list_tasks(
        start: datetime | None = None,
        end: datetime | None = None,
        session: Session | None = None,
    ) -> list[Task]:
        """Lista todas as tasks, com filtro opcional por período."""

        def _list(sess: Session) -> list[Task]:
            statement = select(Task)
            if start:
                statement = statement.where(Task.scheduled_datetime >= start)
            if end:
                statement = statement.where(Task.scheduled_datetime <= end)
            return list(sess.exec(statement).all())

        if session is not None:
            return _list(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _list(sess)

    @staticmethod
    def list_pending_tasks(session: Session | None = None) -> list[Task]:
        """Lista tasks pendentes (não concluídas e não canceladas).

        BR-TASK-009: tasks canceladas são excluídas da lista de pendentes.
        """

        def _list(sess: Session) -> list[Task]:
            statement = select(Task).where(
                col(Task.completed_datetime).is_(None),
                col(Task.cancelled_datetime).is_(None),
            )
            return list(sess.exec(statement).all())

        if session is not None:
            return _list(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _list(sess)

    @staticmethod
    def update_task(
        task_id: int,
        title: str | None = None,
        scheduled_datetime: datetime | None = None,
        description: str | None = None,
        tag_id: int | None = None,
        session: Session | None = None,
    ) -> tuple[Task | None, list[Conflict] | None]:
        """Atualiza task existente.

        BR-TASK-008: se scheduled_datetime é movido para data posterior,
        incrementa postponement_count. original_scheduled_datetime nunca muda.
        """

        def _update(sess: Session) -> tuple[Task | None, bool]:
            task = sess.get(Task, task_id)
            if not task:
                return None, False
            datetime_changed = (
                scheduled_datetime is not None and scheduled_datetime != task.scheduled_datetime
            )
            if title is not None:
                title_stripped = title.strip()
                if not title_stripped:
                    raise ValueError("Title cannot be empty")
                if len(title_stripped) > 200:
                    raise ValueError("Title cannot exceed 200 characters")
                task.title = title_stripped
            if scheduled_datetime is not None:
                # BR-TASK-008: incrementa contador se data posterior
                if scheduled_datetime > task.scheduled_datetime:
                    task.postponement_count += 1
                task.scheduled_datetime = scheduled_datetime
            if description is not None:
                task.description = description
            if tag_id is not None:
                task.tag_id = tag_id
            sess.add(task)
            sess.commit()
            sess.refresh(task)
            return task, datetime_changed

        if session is not None:
            task, datetime_changed = _update(session)
        else:
            with get_engine_context() as engine, Session(engine) as sess:
                task, datetime_changed = _update(sess)
        # Detecta conflitos se horário mudou, mas não propõe resolução
        conflicts = None
        if datetime_changed and task:
            conflicts = EventReorderingService.detect_conflicts(task_id, "task", session=session)
        return task, conflicts

    @staticmethod
    def complete_task(task_id: int, session: Session | None = None) -> Task | None:
        """Marca task como concluída."""

        def _complete(sess: Session) -> Task | None:
            task = sess.get(Task, task_id)
            if not task:
                return None
            task.completed_datetime = datetime.now()
            sess.add(task)
            sess.commit()
            sess.refresh(task)
            logger.info("Task concluída: id=%s", task_id)
            return task

        if session is not None:
            return _complete(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _complete(sess)

    @staticmethod
    def cancel_task(task_id: int, session: Session | None = None) -> Task | None:
        """Cancela task (soft delete).

        BR-TASK-009: seta cancelled_datetime ao invés de remover o registro.
        """

        def _cancel(sess: Session) -> Task | None:
            task = sess.get(Task, task_id)
            if not task:
                return None
            task.cancelled_datetime = datetime.now()
            sess.add(task)
            sess.commit()
            sess.refresh(task)
            logger.info("Task cancelada: id=%s", task_id)
            return task

        if session is not None:
            return _cancel(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _cancel(sess)

    @staticmethod
    def reopen_task(task_id: int, session: Session | None = None) -> Task | None:
        """Reabre task cancelada.

        BR-TASK-009: limpa cancelled_datetime, retornando task para pendente.
        """

        def _reopen(sess: Session) -> Task | None:
            task = sess.get(Task, task_id)
            if not task:
                return None
            task.cancelled_datetime = None
            sess.add(task)
            sess.commit()
            sess.refresh(task)
            logger.info("Task reaberta: id=%s", task_id)
            return task

        if session is not None:
            return _reopen(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _reopen(sess)

    @staticmethod
    def delete_task(task_id: int, session: Session | None = None) -> bool:
        """Remove task permanentemente (hard delete — usar cancel_task para soft delete)."""

        def _delete(sess: Session) -> bool:
            task = sess.get(Task, task_id)
            if not task:
                return False
            sess.delete(task)
            sess.commit()
            logger.info("Task deletada: id=%s", task_id)
            return True

        if session is not None:
            return _delete(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _delete(sess)

    @staticmethod
    def list_recently_completed_tasks(
        hours: int = 24, session: Session | None = None
    ) -> list[Task]:
        """Lista tasks concluídas nas últimas N horas (BR-TUI-003-R29).

        Exclui tasks canceladas (cancelled_datetime prevalece).
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=hours)

        def _list(sess: Session) -> list[Task]:
            statement = select(Task).where(
                col(Task.completed_datetime) >= cutoff,
                col(Task.cancelled_datetime).is_(None),
            )
            return list(sess.exec(statement).all())

        if session is not None:
            return _list(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _list(sess)

    @staticmethod
    def list_recently_cancelled_tasks(
        hours: int = 24, session: Session | None = None
    ) -> list[Task]:
        """Lista tasks canceladas nas últimas N horas (BR-TUI-003-R29)."""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=hours)

        def _list(sess: Session) -> list[Task]:
            statement = select(Task).where(
                col(Task.cancelled_datetime) >= cutoff,
            )
            return list(sess.exec(statement).all())

        if session is not None:
            return _list(session)
        with get_engine_context() as engine, Session(engine) as sess:
            return _list(sess)
