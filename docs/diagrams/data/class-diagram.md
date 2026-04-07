# Diagrama de Classes: Models

- **Status:** Aceito
- **Data:** 2026-04-06

```mermaid
classDiagram
    class Routine {
        +int id
        +str name
        +bool is_active
        +datetime created_at
        +int best_streak
        +list~Habit~ habits
    }

    class Habit {
        +int id
        +int routine_id
        +str title
        +time scheduled_start
        +time scheduled_end
        +Recurrence recurrence
        +str color
        +int tag_id
        +Routine routine
        +list~HabitInstance~ instances
        +Tag tag
    }

    class HabitInstance {
        +int id
        +int habit_id
        +date date
        +time scheduled_start
        +time scheduled_end
        +Status status
        +DoneSubstatus done_substatus
        +NotDoneSubstatus not_done_substatus
        +SkipReason skip_reason
        +str skip_note
        +int completion_percentage
        +Habit habit
        +validate_status_consistency()
        +reset_to_pending()
    }

    class Task {
        +int id
        +str title
        +datetime scheduled_datetime
        +datetime original_scheduled_datetime
        +datetime completed_datetime
        +datetime cancelled_datetime
        +int postponement_count
        +str description
        +str color
        +int tag_id
        +Tag tag
        +derived_status() str
    }

    class Event {
        +int id
        +str title
        +str description
        +str color
        +EventStatus status
        +datetime scheduled_start
        +datetime scheduled_end
        +datetime created_at
        +datetime updated_at
    }

    class Tag {
        +int id
        +str name
        +str color
        +list~Task~ tasks
        +list~Habit~ habits
    }

    class TimeLog {
        +int id
        +int event_id
        +int task_id
        +int habit_instance_id
        +TimerStatus status
        +datetime start_time
        +datetime end_time
        +int duration_seconds
        +int paused_duration
        +datetime pause_start
        +str notes
        +str cancel_reason
    }

    class PauseLog {
        +int id
        +int timelog_id
        +datetime pause_start
        +datetime pause_end
        +datetime created_at
    }

    class ChangeLog {
        +int id
        +int event_id
        +ChangeType change_type
        +str field_name
        +str old_value
        +str new_value
        +datetime changed_at
    }

    Routine "1" --> "*" Habit : contém
    Habit "1" --> "*" HabitInstance : gera (cascade delete)
    Tag "1" --> "*" Habit : categoriza
    Tag "1" --> "*" Task : categoriza
    HabitInstance "1" --> "*" TimeLog : registra
    Event "1" --> "*" TimeLog : registra
    Task "1" --> "*" TimeLog : registra
    TimeLog "1" --> "*" PauseLog : detalha
    Event "1" --> "*" ChangeLog : audita
```

**Relacionamentos principais:**

- Routine → Habit: 1:N (back_populates)
- Habit → HabitInstance: 1:N (cascade delete)
- Tag → Habit: 1:N (opcional)
- Tag → Task: 1:N (opcional)
- TimeLog → HabitInstance/Event/Task: N:1 (FKs opcionais, polimórfico)
- PauseLog → TimeLog: N:1
- ChangeLog → Event: N:1

**Nota:** `Task.derived_status()` é uma property computada — retorna "pending", "overdue", "completed" ou "cancelled" a partir de timestamps. Não existe campo `status` persistido em Task.

**Referências:**

- ADR-004: Habit vs Instance separation
- ADR-007: Service Layer pattern
- ADR-021: Refatoração status/substatus
