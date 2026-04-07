# Sequência: Event Reordering

- **Status:** Aceito
- **Data:** 2026-04-06

```mermaid
sequenceDiagram
    participant User
    participant TUI as Dashboard (TUI)
    participant CRUD as crud_habits
    participant ERS as EventReorderingService
    participant DB as SQLite

    User->>TUI: Cria ou edita hábito via CRUD modal
    TUI->>CRUD: Submete formulário
    CRUD->>ERS: detect_conflicts(event_id, event_type, session)
    ERS->>DB: SELECT tasks, instances, events no range
    DB-->>ERS: entities
    ERS->>ERS: _has_overlap() para cada par
    ERS-->>CRUD: list[Conflict]

    alt Conflitos detectados
        CRUD->>TUI: Notifica conflitos encontrados
        TUI->>User: Exibe aviso de sobreposição
    else Sem conflitos
        CRUD->>TUI: Operação concluída sem conflitos
    end
```

**Modelo de dados:** Conflitos são representados por dataclasses em `event_reordering_models.py`: `ConflictType` (enum), `Conflict`, `ProposedChange`, `ReorderingProposal`.

**Métodos públicos:**

- `detect_conflicts(triggered_event_id, event_type, session)` — detecta conflitos para uma entidade específica após CRUD
- `get_conflicts_for_day(target_date, session)` — detecta todos os conflitos de um dia (disponível mas não usado na TUI atualmente)

**Referências:**

- BR-EVENT-001: Detecção de conflitos
- ADR-003: Event reordering
