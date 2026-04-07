# ER Diagram

- **Status:** Aceito
- **Data:** 2026-04-06

```mermaid
erDiagram
    Routine ||--o{ Habit : "contém"
    Habit ||--o{ HabitInstance : "gera"
    Tag ||--o{ Habit : "categoriza"
    Tag ||--o{ Task : "categoriza"
    TimeLog }o--|| HabitInstance : "registra"
    TimeLog }o--o| Event : "registra"
    TimeLog }o--o| Task : "registra"
    PauseLog }o--|| TimeLog : "detalha"
    ChangeLog }o--|| Event : "audita"

    Routine {
        int id PK
        string name
        bool is_active
        datetime created_at
        int best_streak
    }

    Habit {
        int id PK
        int routine_id FK
        string title
        time scheduled_start
        time scheduled_end
        string color
        int tag_id FK
        enum recurrence
    }

    HabitInstance {
        int id PK
        int habit_id FK
        date date
        time scheduled_start
        time scheduled_end
        enum status
        enum done_substatus
        enum not_done_substatus
        enum skip_reason
        string skip_note
        int completion_percentage
    }

    Task {
        int id PK
        string title
        datetime scheduled_datetime
        datetime original_scheduled_datetime
        datetime completed_datetime
        datetime cancelled_datetime
        int postponement_count
        string description
        string color
        int tag_id FK
    }

    Event {
        int id PK
        string title
        string description
        string color
        enum status
        datetime scheduled_start
        datetime scheduled_end
        datetime created_at
        datetime updated_at
    }

    Tag {
        int id PK
        string name
        string color
    }

    TimeLog {
        int id PK
        int event_id FK
        int task_id FK
        int habit_instance_id FK
        enum status
        datetime start_time
        datetime end_time
        int duration_seconds
        int paused_duration
        datetime pause_start
        string notes
        string cancel_reason
    }

    PauseLog {
        int id PK
        int timelog_id FK
        datetime pause_start
        datetime pause_end
        datetime created_at
    }

    ChangeLog {
        int id PK
        int event_id FK
        string field_name
        string old_value
        string new_value
        datetime changed_at
    }
```

**Tabelas (9):** routines, habits, habitinstance, tasks, event, tags, time_log, pauselog, changelog.

**Enums referenciados:** `Status` (PENDING, DONE, NOT_DONE), `DoneSubstatus`, `NotDoneSubstatus`, `SkipReason`, `TimerStatus` (RUNNING, PAUSED, DONE, CANCELLED), `EventStatus`, `Recurrence`, `ChangeType`.

**Nota:** `Task` não possui campo `status` persistido — o status é derivado via `derived_status` a partir dos timestamps (`cancelled_datetime`, `completed_datetime`, `scheduled_datetime`).

**Referências:**

- ADR-004: Habit vs Instance separation
- ADR-021: Refatoração status/substatus
