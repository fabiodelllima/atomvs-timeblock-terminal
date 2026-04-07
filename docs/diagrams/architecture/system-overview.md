# Visão Geral da Arquitetura

- **Status:** Aceito
- **Data:** 2026-04-06

---

## Visão Geral

Este diagrama apresenta a arquitetura completa do ATOMVS Time Planner em uma única visão, combinando o modelo de domínio, as camadas da aplicação e o fluxo de dados. Serve como ponto de entrada para compreender o sistema antes de consultar os diagramas C4 e de dados mais detalhados.

---

## Modelo de Domínio

O ATOMVS organiza o tempo através de cinco conceitos centrais. Rotinas agrupam hábitos tematicamente (ex: "Rotina Matinal"). Hábitos são templates recorrentes que geram instâncias concretas para cada dia aplicável. Tarefas são eventos pontuais, independentes de rotinas. Tags categorizam tanto hábitos quanto tarefas. O timer rastreia tempo dedicado via TimeLog.

```mermaid
graph LR
    subgraph Domínio["Modelo de Domínio"]
        ROUTINE["Routine<br/>(coleção)"]
        HABIT["Habit<br/>(template recorrente)"]
        INSTANCE["HabitInstance<br/>(ocorrência diária)"]
        TASK["Task<br/>(evento pontual)"]
        TAG["Tag<br/>(categoria)"]
        TIMELOG["TimeLog<br/>(tracking)"]
    end

    ROUTINE -->|"1:N"| HABIT
    HABIT -->|"1:N"| INSTANCE
    INSTANCE -->|"1:N"| TIMELOG
    TAG -.->|"categoriza"| HABIT
    TAG -.->|"categoriza"| TASK
    TASK -->|"1:N"| TIMELOG

    style ROUTINE fill:#1168bd,stroke:#0b4884,color:#fff
    style HABIT fill:#1168bd,stroke:#0b4884,color:#fff
    style INSTANCE fill:#1168bd,stroke:#0b4884,color:#fff
    style TASK fill:#1168bd,stroke:#0b4884,color:#fff
    style TAG fill:#666,stroke:#444,color:#fff
    style TIMELOG fill:#666,stroke:#444,color:#fff
```

---

## Camadas da Aplicação

A arquitetura segue o padrão de camadas com separação estrita de responsabilidades. CLI e TUI são thin wrappers que delegam toda a lógica para a camada de services. Nenhuma regra de negócio reside na camada de apresentação.

```mermaid
graph TB
    subgraph Presentation["Apresentação"]
        CLI["CLI<br/>Typer<br/>commands/"]
        TUI["TUI<br/>Textual<br/>tui/screens + widgets"]
    end

    subgraph Business["Lógica de Negócio"]
        SVC["Services (8)<br/>routine, habit, habit_instance,<br/>task, timer, tag, backup,<br/>event_reordering"]
    end

    subgraph Data["Acesso a Dados"]
        MDL["Models (9)<br/>SQLModel + Pydantic"]
        DB_MOD["Database<br/>engine + migrations"]
    end

    subgraph Cross["Transversal"]
        UTL["Utils<br/>validators, date_parser,<br/>logger, conflict_display"]
    end

    DB[(SQLite<br/>~/.local/share/atomvs/)]

    CLI --> SVC
    TUI --> SVC
    SVC --> MDL
    SVC --> UTL
    MDL --> DB_MOD
    DB_MOD --> DB

    style CLI fill:#1168bd,stroke:#0b4884,color:#fff
    style TUI fill:#1168bd,stroke:#0b4884,color:#fff
    style SVC fill:#2a9d8f,stroke:#1a7a6e,color:#fff
    style MDL fill:#e76f51,stroke:#c45a3e,color:#fff
    style DB_MOD fill:#e76f51,stroke:#c45a3e,color:#fff
    style DB fill:#999,stroke:#666,color:#fff
    style UTL fill:#666,stroke:#444,color:#fff
```

---

## Fluxo de Dados

O fluxo é unidirecional: input do usuário entra pela camada de apresentação, atravessa services (que aplicam regras de negócio e validações), chega aos models (que mapeiam para tabelas SQLite via SQLModel) e persiste no banco local.

Na TUI, a comunicação entre widgets segue o padrão de message passing do Textual. Widgets emitem Messages tipadas (ex: `TimerStartRequest`, `HabitDoneRequest`), que o DashboardScreen recebe como coordinator e delega para services via `service_action()`.

```mermaid
sequenceDiagram
    participant U as Usuário
    participant P as CLI/TUI
    participant S as Service
    participant M as Model
    participant DB as SQLite

    U->>P: Ação (comando ou keybinding)
    P->>S: Chamada de método
    S->>S: Validação + regras de negócio
    S->>M: Criação/atualização de entidade
    M->>DB: SQL (via SQLModel/SQLAlchemy)
    DB-->>M: Resultado
    M-->>S: Entidade atualizada
    S-->>P: Retorno
    P-->>U: Feedback (output CLI ou atualização de widget)
```

---

## Referências

- [ER Diagram](../data/er-diagram.md) — modelo relacional detalhado (9 tabelas)
- [Class Diagram](../data/class-diagram.md) — classes, campos e relationships
- [L1 System Context](../c4-model/L1-system-context.md) — contexto externo
- [L2 Containers](../c4-model/L2-containers.md) — containers e dependências
- [L3 Components](../c4-model/L3-components-core.md) — componentes internos
- [Deployment](../infrastructure/deployment.md) — infraestrutura de runtime e CI/CD
- ADR-006: Textual TUI
- ADR-007: Service Layer pattern
- ADR-034: Dashboard-first CRUD
