"""Service para gerenciar timers de HabitInstance."""

from datetime import date, datetime, time, timedelta

from sqlmodel import Session, select

from timeblock.database.engine import get_engine_context
from timeblock.models.enums import DoneSubstatus, Status, TimerStatus
from timeblock.models.habit_instance import HabitInstance
from timeblock.models.time_log import TimeLog


class TimerService:
    """Service para operações de timer.

    Estados do timer (BR-TIMER-002):
    - RUNNING: Timer contando tempo
    - PAUSED: Timer pausado temporariamente
    - DONE: Timer finalizado com stop
    - CANCELLED: Timer resetado
    """

    def get_timelog(
        self,
        timelog_id: int,
        session: Session | None = None,
    ) -> TimeLog | None:
        """Recupera TimeLog por ID.

        Args:
            timelog_id: ID do timelog
            session: Sessão opcional

        Returns:
            TimeLog se encontrado, None caso contrário.
        """

        def _get(sess: Session) -> TimeLog | None:
            return sess.get(TimeLog, timelog_id)

        if session is not None:
            return _get(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _get(sess)

    def list_timelogs(
        self,
        habit_instance_id: int | None = None,
        date_start: date | None = None,
        date_end: date | None = None,
        session: Session | None = None,
    ) -> list[TimeLog]:
        """Lista timelogs com filtros opcionais.

        BR-TIMER-008: Listagem de TimeLogs.

        Args:
            habit_instance_id: Filtra por instância específica
            date_start: Data inicial do período
            date_end: Data final do período
            session: Sessão opcional

        Returns:
            Lista de timelogs (vazia se nenhum resultado).
        """

        def _list(sess: Session) -> list[TimeLog]:
            statement = select(TimeLog)

            if habit_instance_id is not None:
                statement = statement.where(TimeLog.habit_instance_id == habit_instance_id)

            if date_start is not None:
                start_datetime = datetime.combine(date_start, datetime.min.time())
                statement = statement.where(TimeLog.start_time >= start_datetime)

            if date_end is not None:
                end_datetime = datetime.combine(date_end, datetime.max.time())
                statement = statement.where(TimeLog.start_time <= end_datetime)

            statement = statement.order_by(TimeLog.start_time)  # type: ignore[arg-type]
            return list(sess.exec(statement).all())

        if session is not None:
            return _list(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _list(sess)

    @staticmethod
    def start_timer(habit_instance_id: int, session: Session | None = None) -> TimeLog:
        """Inicia timer para HabitInstance.

        BR-TIMER-002: Cria timer com status RUNNING.

        Args:
            habit_instance_id: ID da instância
            session: Sessão opcional

        Returns:
            TimeLog criado com status RUNNING

        Raises:
            ValueError: Se instance não existe ou timer já ativo
        """

        def _start(sess: Session) -> TimeLog:
            instance = sess.get(HabitInstance, habit_instance_id)
            if not instance:
                raise ValueError(f"HabitInstance {habit_instance_id} not found")

            # BR-TIMER-001: Verificar se já existe timer ativo
            statement = select(TimeLog).where(
                TimeLog.status.in_([TimerStatus.RUNNING, TimerStatus.PAUSED])  # type: ignore[union-attr]
            )
            existing_timer = sess.exec(statement).first()
            if existing_timer:
                raise ValueError("Timer already active")

            timelog = TimeLog(
                habit_instance_id=habit_instance_id,
                start_time=datetime.now(),
                status=TimerStatus.RUNNING,
            )
            sess.add(timelog)
            sess.commit()
            sess.refresh(timelog)
            return timelog

        if session is not None:
            return _start(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _start(sess)

    @staticmethod
    def stop_timer(timelog_id: int, session: Session | None = None) -> TimeLog:
        """Para timer e calcula substatus automaticamente.

        BR-TIMER-002: Muda status para DONE.
        BR-TIMER-003: Salva sessão e atualiza instance.

        Args:
            timelog_id: ID do timer
            session: Sessão opcional

        Returns:
            TimeLog atualizado com status DONE

        Raises:
            ValueError: Se timer não existe ou já finalizado
        """

        def _stop(sess: Session) -> TimeLog:
            timelog = sess.get(TimeLog, timelog_id)
            if not timelog:
                raise ValueError(f"TimeLog {timelog_id} not found")

            if timelog.status not in [TimerStatus.RUNNING, TimerStatus.PAUSED]:
                raise ValueError("Timer not active")

            # Se estava pausado, acumula última pausa
            if timelog.status == TimerStatus.PAUSED and timelog.pause_start:
                pause_duration = (datetime.now() - timelog.pause_start).total_seconds()
                timelog.paused_duration = (timelog.paused_duration or 0) + int(pause_duration)
                timelog.pause_start = None

            # Parar timer
            timelog.end_time = datetime.now()
            timelog.status = TimerStatus.DONE

            total_duration = (timelog.end_time - timelog.start_time).total_seconds()
            paused_duration = timelog.paused_duration or 0
            timelog.duration_seconds = int(total_duration - paused_duration)

            # Buscar HabitInstance
            if timelog.habit_instance_id is None:
                raise ValueError("TimeLog must have habit_instance_id")

            instance = sess.get(HabitInstance, timelog.habit_instance_id)
            if not instance:
                raise ValueError(f"HabitInstance {timelog.habit_instance_id} not found")

            # Calcular completion percentage (BR-TIMER-005)
            target_start = datetime.combine(instance.date, instance.scheduled_start)
            target_end = datetime.combine(instance.date, instance.scheduled_end)
            target_seconds = (target_end - target_start).total_seconds()

            if target_seconds <= 0:
                raise ValueError("Target duration must be positive")

            actual_seconds = timelog.duration_seconds
            completion_percentage = int((actual_seconds / target_seconds) * 100)

            # Determinar substatus
            if completion_percentage < 90:
                done_substatus = DoneSubstatus.PARTIAL
            elif completion_percentage <= 110:
                done_substatus = DoneSubstatus.FULL
            elif completion_percentage <= 150:
                done_substatus = DoneSubstatus.OVERDONE
            else:
                done_substatus = DoneSubstatus.EXCESSIVE

            # Atualizar HabitInstance
            instance.status = Status.DONE
            instance.done_substatus = done_substatus
            instance.completion_percentage = completion_percentage
            instance.not_done_substatus = None
            instance.validate_status_consistency()

            sess.add(timelog)
            sess.add(instance)
            sess.commit()
            sess.refresh(timelog)
            sess.refresh(instance)

            return timelog

        if session is not None:
            return _stop(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _stop(sess)

    @staticmethod
    def pause_timer(timelog_id: int, session: Session | None = None) -> TimeLog:
        """Pausa timer ativo.

        BR-TIMER-002: Muda status de RUNNING para PAUSED.
        BR-TIMER-006: Registra pause_start para tracking.

        Args:
            timelog_id: ID do TimeLog
            session: Sessão opcional

        Returns:
            TimeLog com status PAUSED

        Raises:
            ValueError: Se timer não existe ou já pausado
        """

        def _pause(sess: Session) -> TimeLog:
            timelog = sess.get(TimeLog, timelog_id)
            if not timelog:
                raise ValueError(f"TimeLog {timelog_id} not found")

            if timelog.status == TimerStatus.PAUSED:
                raise ValueError("Timer already paused")

            if timelog.status != TimerStatus.RUNNING:
                raise ValueError("Timer not running")

            timelog.status = TimerStatus.PAUSED
            timelog.pause_start = datetime.now()

            sess.add(timelog)
            sess.commit()
            sess.refresh(timelog)
            return timelog

        if session is not None:
            return _pause(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _pause(sess)

    @staticmethod
    def resume_timer(timelog_id: int, session: Session | None = None) -> TimeLog:
        """Retoma timer pausado.

        BR-TIMER-002: Muda status de PAUSED para RUNNING.
        BR-TIMER-006: Acumula paused_duration.

        Args:
            timelog_id: ID do TimeLog
            session: Sessão opcional

        Returns:
            TimeLog com status RUNNING

        Raises:
            ValueError: Se timer não existe ou não está pausado
        """

        def _resume(sess: Session) -> TimeLog:
            timelog = sess.get(TimeLog, timelog_id)
            if not timelog:
                raise ValueError(f"TimeLog {timelog_id} not found")

            if timelog.status != TimerStatus.PAUSED:
                raise ValueError("Timer already running")

            # Calcular e acumular duração da pausa
            if timelog.pause_start:
                pause_duration = (datetime.now() - timelog.pause_start).total_seconds()
                timelog.paused_duration = (timelog.paused_duration or 0) + int(pause_duration)

            timelog.status = TimerStatus.RUNNING
            timelog.pause_start = None

            sess.add(timelog)
            sess.commit()
            sess.refresh(timelog)
            return timelog

        if session is not None:
            return _resume(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _resume(sess)

    @staticmethod
    def reset_timer(
        timelog_id: int,
        session: Session | None = None,
        reason: str | None = None,
    ) -> TimeLog:
        """Reseta timer (cancela sem salvar progresso).

        BR-TIMER-002: Muda status para CANCELLED.
        BR-TIMER-003: Instance permanece PENDING.

        Args:
            timelog_id: ID do TimeLog
            session: Sessão opcional
            reason: Motivo do cancelamento (opcional)

        Returns:
            TimeLog com status CANCELLED

        Raises:
            ValueError: Se timer não existe ou já cancelado
        """

        def _reset(sess: Session) -> TimeLog:
            timelog = sess.get(TimeLog, timelog_id)
            if not timelog:
                raise ValueError(f"TimeLog {timelog_id} not found")

            if timelog.status == TimerStatus.CANCELLED:
                raise ValueError("Session already cancelled")

            timelog.status = TimerStatus.CANCELLED
            timelog.pause_start = None
            if reason:
                timelog.cancel_reason = reason

            sess.add(timelog)
            sess.commit()
            sess.refresh(timelog)
            return timelog

        if session is not None:
            return _reset(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _reset(sess)

    @staticmethod
    def cancel_timer(timelog_id: int, session: Session | None = None) -> None:
        """Alias para reset_timer (compatibilidade).

        DEPRECATED: Use reset_timer() ao invés.
        """
        TimerService.reset_timer(timelog_id, session)

    @staticmethod
    def get_active_timer(habit_instance_id: int, session: Session | None = None) -> TimeLog | None:
        """Busca timer ativo para HabitInstance.

        Timer ativo: status IN (RUNNING, PAUSED)

        Args:
            habit_instance_id: ID da instância
            session: Sessão opcional

        Returns:
            TimeLog ativo ou None
        """

        def _get(sess: Session) -> TimeLog | None:
            statement = select(TimeLog).where(
                TimeLog.habit_instance_id == habit_instance_id,
                TimeLog.status.in_([TimerStatus.RUNNING, TimerStatus.PAUSED]),  # type: ignore[union-attr]
            )
            return sess.exec(statement).first()

        if session is not None:
            return _get(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _get(sess)

    @staticmethod
    def get_any_active_timer(session: Session | None = None) -> TimeLog | None:
        """Busca qualquer timer ativo (global).

        BR-TIMER-001: Apenas um timer ativo por vez.

        Args:
            session: Sessão opcional

        Returns:
            TimeLog ativo ou None
        """

        def _get(sess: Session) -> TimeLog | None:
            statement = select(TimeLog).where(
                TimeLog.status.in_([TimerStatus.RUNNING, TimerStatus.PAUSED])  # type: ignore[union-attr]
            )
            return sess.exec(statement).first()

        if session is not None:
            return _get(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _get(sess)

    def log_manual(
        self,
        habit_instance_id: int,
        start_time: time | None = None,
        end_time: time | None = None,
        duration_minutes: int | None = None,
        session: Session | None = None,
    ) -> TimeLog:
        """Registra tempo manualmente sem usar timer (BR-TIMER-007).

        Dois modos mutuamente exclusivos:
            - Intervalo: start_time + end_time
            - Duração: duration_minutes

        Args:
            habit_instance_id: ID da instância
            start_time: Hora início (modo intervalo)
            end_time: Hora fim (modo intervalo)
            duration_minutes: Duração em minutos (modo duração)
            session: Sessão opcional

        Returns:
            TimeLog criado com status DONE

        Raises:
            ValueError: Se validação falhar
        """

        def _log(sess: Session) -> TimeLog:
            # Validar modos mutuamente exclusivos
            has_interval = start_time is not None or end_time is not None
            has_duration = duration_minutes is not None

            if has_interval and has_duration:
                raise ValueError("cannot mix interval and duration modes")

            if not has_interval and not has_duration:
                raise ValueError("must provide interval (start/end) or duration")

            # Validar modo intervalo
            if has_interval:
                if start_time is None or end_time is None:
                    raise ValueError("start requires end")
                if start_time >= end_time:
                    raise ValueError("start must be before end")

            # Validar modo duração
            if has_duration:
                if duration_minutes is not None and duration_minutes <= 0:
                    raise ValueError("duration must be positive")

            # Buscar HabitInstance
            instance = sess.get(HabitInstance, habit_instance_id)
            if not instance:
                raise ValueError(f"HabitInstance {habit_instance_id} not found")

            # Calcular duração em segundos
            if has_interval and start_time and end_time:
                start_dt = datetime.combine(instance.date, start_time)
                end_dt = datetime.combine(instance.date, end_time)
                duration_seconds = int((end_dt - start_dt).total_seconds())
            else:
                duration_seconds = (duration_minutes or 0) * 60
                start_dt = datetime.combine(instance.date, instance.scheduled_start)
                end_dt = start_dt + timedelta(seconds=duration_seconds)

            # Criar TimeLog com status DONE
            timelog = TimeLog(
                habit_instance_id=habit_instance_id,
                start_time=start_dt,
                end_time=end_dt,
                duration_seconds=duration_seconds,
                status=TimerStatus.DONE,
            )
            sess.add(timelog)

            # Calcular completion percentage
            target_start = datetime.combine(instance.date, instance.scheduled_start)
            target_end = datetime.combine(instance.date, instance.scheduled_end)
            target_seconds = (target_end - target_start).total_seconds()

            if target_seconds <= 0:
                raise ValueError("Target duration must be positive")

            completion_percentage = int((duration_seconds / target_seconds) * 100)

            # Determinar substatus
            if completion_percentage < 90:
                done_substatus = DoneSubstatus.PARTIAL
            elif completion_percentage <= 110:
                done_substatus = DoneSubstatus.FULL
            elif completion_percentage <= 150:
                done_substatus = DoneSubstatus.OVERDONE
            else:
                done_substatus = DoneSubstatus.EXCESSIVE

            # Atualizar HabitInstance
            instance.status = Status.DONE
            instance.done_substatus = done_substatus
            instance.completion_percentage = completion_percentage
            instance.not_done_substatus = None
            instance.validate_status_consistency()

            sess.add(instance)
            sess.commit()
            sess.refresh(timelog)

            return timelog

        if session is not None:
            return _log(session)

        with get_engine_context() as engine, Session(engine) as sess:
            return _log(sess)
