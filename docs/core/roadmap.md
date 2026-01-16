# Roadmap TimeBlock Organizer

**Versão do Documento:** 1.0.0
**Última atualização:** 14 de Janeiro de 2026
**Status:** SSOT (Single Source of Truth)

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Histórico de Entregas](#2-histórico-de-entregas)
3. [Estado Atual](#3-estado-atual)
4. [Roadmap Futuro](#4-roadmap-futuro)
5. [Backlog Técnico](#5-backlog-técnico)

---

## 1. Visão Geral

### 1.1. Objetivo do Projeto

TimeBlock Organizer é uma aplicação CLI para gerenciamento de tempo baseada em:

- **Time Blocking:** Alocação de blocos de tempo para atividades
- **Atomic Habits:** Construção de hábitos através de rotinas
- **User Control:** Sistema informa, usuário decide

### 1.2. Arquitetura Alvo

```
v1.x.x (CLI)     v2.x.x (API)      v3.x.x (Sync)     v4.x.x (Mobile)
    │                │                  │                  │
    ▼                ▼                  ▼                  ▼
┌────────┐      ┌─────────┐       ┌──────────┐      ┌──────────┐
│ Typer  │      │ FastAPI │       │  Kafka   │      │  Kotlin  │
│ CLI    │ ───▶ │ REST    │ ───▶  │ Events   │ ───▶ │ Android  │
│ SQLite │      │ SQLite  │       │ Postgres │      │ Room DB  │
└────────┘      └─────────┘       └──────────┘      └──────────┘
```

---

## 2. Histórico de Entregas

### v1.0.0 - Foundation (Outubro 2025) [ENTREGUE]

**Escopo:** Estrutura básica do projeto

| Feature              | Status | Descrição                     |
| -------------------- | ------ | ----------------------------- |
| Estrutura de projeto | [DONE] | src/, tests/, docs/           |
| Models básicos       | [DONE] | Routine, Habit, Task, TimeLog |
| SQLModel ORM         | [DONE] | ADR-001                       |
| Typer CLI            | [DONE] | ADR-002                       |
| Service Layer        | [DONE] | ADR-007                       |
| Pytest setup         | [DONE] | Configuração básica           |

**Métricas Finais:**

- Testes: ~50
- Cobertura: ~30%
- ADRs: 7

---

### v1.1.0 - Core Features (Novembro 2025) [ENTREGUE]

**Escopo:** Funcionalidades principais de hábitos e rotinas

| Feature              | Status | Descrição                    |
| -------------------- | ------ | ---------------------------- |
| BR-ROUTINE-001 a 004 | [DONE] | Single active, cascade       |
| BR-HABIT-001 a 005   | [DONE] | CRUD completo                |
| BR-TASK-001 a 006    | [DONE] | Tasks independentes          |
| HabitInstance model  | [DONE] | Separação template/instância |
| Recurrence patterns  | [DONE] | EVERYDAY, WEEKDAYS, etc      |
| Instance generation  | [DONE] | --generate N meses           |
| Timer básico         | [DONE] | Start/stop/pause             |

**Métricas Finais:**

- Testes: ~200
- Cobertura: ~60%
- ADRs: 15
- BRs: 25

---

### v1.2.0 - Status Refactoring (Novembro 2025) [ENTREGUE]

**Escopo:** Refatoração do sistema de status

| Feature                    | Status | Descrição                                       |
| -------------------------- | ------ | ----------------------------------------------- |
| Status enum simplificado   | [DONE] | PENDING, DONE, NOT_DONE                         |
| DoneSubstatus              | [DONE] | FULL, PARTIAL, OVERDONE, EXCESSIVE              |
| NotDoneSubstatus           | [DONE] | SKIPPED_JUSTIFIED, SKIPPED_UNJUSTIFIED, IGNORED |
| SkipReason enum            | [DONE] | 8 categorias                                    |
| Migration script           | [DONE] | migration_001_status_substatus.py               |
| BR-HABITINSTANCE-001 a 005 | [DONE] | Status e substatus                              |
| BR-SKIP-001 a 004          | [DONE] | Sistema de skip                                 |
| BR-STREAK-001 a 004        | [DONE] | Cálculo de streaks                              |

**Breaking Changes:**

- HabitInstanceStatus (5 valores) → Status (3 valores)
- Campos novos: done_substatus, not_done_substatus, skip_reason, skip_note

**Métricas Finais:**

- Testes: ~350
- Cobertura: ~70%
- ADRs: 22
- BRs: 40

---

### v1.3.0 - Event Reordering & Docs (Dezembro 2025) [ENTREGUE]

**Escopo:** Sistema de reordering e consolidação de documentação

| Feature                  | Status    | Descrição              |
| ------------------------ | --------- | ---------------------- |
| EventReorderingService   | [PARTIAL] | Detecção de conflitos  |
| Conflict dataclass       | [DONE]    | Modelo de conflito     |
| ProposedChange dataclass | [DONE]    | Proposta de mudança    |
| ReorderingProposal       | [DONE]    | Container de propostas |
| BR-REORDER-001 a 002     | [PARTIAL] | Detecção básica        |
| Documentação consolidada | [DONE]    | docs/core/             |
| 25 ADRs                  | [DONE]    | Decisões arquiteturais |
| 50 BRs documentadas      | [DONE]    | business-rules.md      |

**Métricas Finais:**

- Testes: 454 passed, 26 skipped
- Cobertura: 61%
- ADRs: 25
- BRs: 50
- Erros mypy: 156 (dívida técnica)

---

## 3. Estado Atual

### 3.1. Métricas (14 Jan 2026)

| Categoria         | Valor | Meta v1.4 |
| ----------------- | ----- | --------- |
| Testes passando   | 454   | 480       |
| Testes skipped    | 26    | 0         |
| Cobertura         | 61%   | 80%       |
| Erros mypy        | 156   | 0         |
| BRs documentadas  | 50    | 50        |
| BRs implementadas | ~40   | 50        |
| ADRs              | 25    | 25        |

### 3.2. Distribuição de Testes

| Tipo        | Quantidade | %   |
| ----------- | ---------- | --- |
| Unit        | 378        | 79% |
| Integration | 64         | 13% |
| E2E         | 5          | 1%  |
| BDD         | 7          | 1%  |
| Skipped     | 26         | 5%  |

### 3.3. Cobertura por Módulo

| Módulo    | Cobertura | Status    |
| --------- | --------- | --------- |
| models/   | 95%       | [OK]      |
| services/ | 70%       | [PARCIAL] |
| commands/ | 25%       | [CRITICO] |
| utils/    | 60%       | [PARCIAL] |
| database/ | 40%       | [PARCIAL] |

### 3.4. Problemas Críticos

1. **156 erros mypy** - Commands desalinhados com Services
2. **26 testes skipped** - Funcionalidades não implementadas
3. **Commands CLI** - ~60% quebrados (timer, schedule, report)
4. **EventReorderingService** - Parcialmente implementado

---

## 4. Roadmap Futuro

### v1.3.1 - Hotfix (Janeiro 2026) [EM PROGRESSO]

**Objetivo:** Corrigir erros críticos sem novas features

| Task                           | Prioridade | Estimativa | Status |
| ------------------------------ | ---------- | ---------- | ------ |
| Corrigir E2E tests (freezegun) | ALTA       | 1h         | [DONE] |
| Eliminar ResourceWarnings      | ALTA       | 3h         | [DONE] |
| Atualizar README métricas      | MEDIA      | 30min      | [DONE] |
| Criar ROADMAP SSOT             | MEDIA      | 2h         | [WIP]  |
| Criar diagnóstico mypy         | MEDIA      | 1h         | [DONE] |

**Critério de Conclusão:**

- 0 testes falhando
- Documentação atualizada

---

### v1.4.0 - MVP Completo (Fevereiro 2026) [PLANEJADO]

**Objetivo:** CLI 100% funcional, 0 erros mypy

#### Sprint 1: Infraestrutura Mypy (2h)

| Task                | Descrição                      |
| ------------------- | ------------------------------ |
| Instalar stubs      | types-python-dateutil          |
| Corrigir migrations | Session.exec → Session.execute |
| Corrigir services   | datetime.is\_() → == None      |

#### Sprint 2: Services Core (4h)

| Task                   | Descrição                                     |
| ---------------------- | --------------------------------------------- |
| HabitInstanceService   | Implementar get_instance, list_instances      |
| TimerService           | Implementar get_timelog, get_timelogs_by_date |
| EventReorderingService | Corrigir datetime.between, unions             |
| TaskService            | Corrigir list_tasks assinatura                |

#### Sprint 3: Commands Alignment (6h)

| Task                 | Descrição                        |
| -------------------- | -------------------------------- |
| commands/timer.py    | Alinhar com TimerService         |
| commands/schedule.py | Alinhar com HabitInstanceService |
| commands/report.py   | Alinhar com todos services       |
| commands/task.py     | Adicionar null checks            |
| commands/habit.py    | Corrigir tipagem                 |

#### Sprint 4: Testes Skipped (4h)

| Task                   | Descrição |
| ---------------------- | --------- |
| Integration reordering | 17 testes |
| Database migrations    | 6 testes  |
| Workflow fixtures      | 1 teste   |
| E2E conflict detection | 1 teste   |
| Task service edge case | 1 teste   |

**Critérios de Conclusão:**

- 0 erros mypy
- 0 testes skipped
- 480+ testes passando
- 80%+ cobertura
- CLI 100% funcional

---

### v1.5.0 - Infrastructure (Março 2026) [PLANEJADO]

**Objetivo:** Preparar para produção

| Feature    | Descrição                    |
| ---------- | ---------------------------- |
| Docker     | Containerização da aplicação |
| CI/CD      | GitHub Actions completo      |
| MkDocs     | Documentação publicada       |
| Pre-commit | Hooks padronizados           |
| Releases   | Automação de releases        |

---

### v2.0.0 - REST API (Q2 2026) [PLANEJADO]

**Objetivo:** Backend para sincronização

| Feature             | Descrição          |
| ------------------- | ------------------ |
| FastAPI             | REST API           |
| SQLite → PostgreSQL | Migração opcional  |
| JWT Auth            | Autenticação       |
| Prometheus          | Métricas           |
| Grafana             | Dashboards         |
| Loki                | Logs centralizados |

---

### v3.0.0 - Sync & Events (Q3 2026) [PLANEJADO]

**Objetivo:** Sincronização distribuída

| Feature             | Descrição                |
| ------------------- | ------------------------ |
| Apache Kafka        | Event streaming          |
| CloudEvents         | Formato padronizado      |
| Conflict Resolution | Last-write-wins + manual |
| Multi-device        | Linux ↔ Android          |

---

### v4.0.0 - Mobile (Q4 2026) [PLANEJADO]

**Objetivo:** App Android nativo

| Feature       | Descrição              |
| ------------- | ---------------------- |
| Kotlin        | Linguagem nativa       |
| Room DB       | SQLite Android         |
| Material 3    | Design system          |
| Offline-first | Sync quando disponível |

---

## 5. Backlog Técnico

### 5.1. Dívida Técnica Atual

| Item                  | Severidade | Esforço |
| --------------------- | ---------- | ------- |
| 156 erros mypy        | CRITICA    | 16h     |
| 26 testes skipped     | ALTA       | 8h      |
| Commands desalinhados | ALTA       | 6h      |
| Cobertura < 80%       | MEDIA      | 8h      |
| Código morto          | BAIXA      | 2h      |

### 5.2. Melhorias Desejadas

| Item              | Prioridade | Versão |
| ----------------- | ---------- | ------ |
| TUI (Textual)     | BAIXA      | v2.x   |
| Plugin system     | BAIXA      | v3.x   |
| Themes CLI        | BAIXA      | v2.x   |
| Export/Import     | MEDIA      | v1.5   |
| Backup automático | MEDIA      | v1.5   |

### 5.3. Investigações Pendentes

| Item                          | Contexto         |
| ----------------------------- | ---------------- |
| Alembic vs migrations manuais | ADR-016 pendente |
| Google Calendar sync          | v2.x feature     |
| iCal export                   | v1.5 feature     |

---

## Changelog do Documento

| Data       | Versão | Mudança                                |
| ---------- | ------ | -------------------------------------- |
| 2026-01-14 | 1.0.0  | Criação inicial com histórico completo |

---

**Mantido por:** Equipe TimeBlock
**Revisão:** Mensal ou após releases
