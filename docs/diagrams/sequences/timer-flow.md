# Sequência: Timer Lifecycle

- **Status:** Aceito
- **Data:** 2026-04-06

```mermaid
sequenceDiagram
    participant User
    participant HP as HabitsPanel
    participant TP as TimerPanel
    participant DS as DashboardScreen
    participant TS as TimerService
    participant DB as SQLite

    User->>HP: Seleciona instance, pressiona t
    HP->>DS: TimerStartRequest(instance_id)
    DS->>TS: start_timer(instance_id)
    TS->>DB: INSERT time_log (status=RUNNING, start_time=now)
    TS-->>DS: TimeLog criado
    DS->>TP: update_data(timer_info)
    TP-->>User: Exibe contagem e keybindings

    Note over User: trabalha...

    opt Pausar/Retomar
        User->>TP: Pressiona space (pause)
        TP->>DS: TimerPauseRequest(timer_id)
        DS->>TS: pause_timer(timelog_id)
        TS->>DB: UPDATE time_log status=PAUSED, pause_start=now
        TS-->>DS: TimeLog atualizado

        User->>TP: Pressiona space (resume)
        TP->>DS: TimerResumeRequest(timer_id)
        DS->>TS: resume_timer(timelog_id)
        TS->>DB: UPDATE time_log status=RUNNING, acumula paused_duration
        TS-->>DS: TimeLog atualizado
    end

    User->>TP: Pressiona s (stop)
    TP->>DS: TimerStopRequest(timer_id)
    DS->>TS: stop_timer(timelog_id)
    TS->>TS: Calcula duration_seconds e completion_percentage
    TS->>DB: UPDATE time_log status=DONE, end_time, duration_seconds
    TS->>DB: UPDATE habit_instance status=DONE, done_substatus, completion_percentage
    TS-->>DS: TimeLog finalizado
    DS->>TP: update_data(None)
    TP-->>User: Timer limpo, MetricsPanel atualiza streak
```

**Keybindings (TimerPanel):** `space` pause/resume, `s` stop, `c` cancel.

**Referências:**

- BR-TIMER-001 a BR-TIMER-006
- BR-TUI-021: Keybinding t inicia timer
- BR-TUI-033: MetricsPanel
