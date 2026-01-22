# TimeBlock Organizer

> Gerenciador de tempo CLI baseado em time blocking e hábitos atômicos

```
╔═══════════════════════════════════════════════════════════════╗
║  TimeBlock Organizer v1.3.3                                   ║
║  ───────────────────────────────────────────────────────────  ║
║  [x] 558 testes  [x] 67% cobertura  [x] 26 ADRs  [x] 52 BRs   ║
╚═══════════════════════════════════════════════════════════════╝
```

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-558%20passing-success.svg)](cli/tests/)
[![Coverage](https://img.shields.io/badge/coverage-67%25-yellow.svg)](cli/tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Visão Geral

TimeBlock Organizer é uma ferramenta CLI para gerenciamento de tempo usando time blocking, inspirada em "Atomic Habits" de James Clear. O sistema detecta conflitos e fornece informações, mantendo o usuário no controle das decisões.

**Filosofia:** Conflitos são informados, nunca bloqueados. O sistema sugere, o usuário decide.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TIMEBLOCK ORGANIZER                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │   ROUTINE   │───>│    HABIT    │───>│   HABIT     │              │
│  │  (coleção)  │    │  (template) │    │  INSTANCE   │              │
│  └─────────────┘    └─────────────┘    └─────────────┘              │
│         │                  │                  │                     │
│         │                  │                  ▼                     │
│         │                  │           ┌─────────────┐              │
│         │                  │           │    TIMER    │              │
│         │                  │           │  (tracking) │              │
│         │                  │           └─────────────┘              │
│         │                  │                                        │
│         ▼                  ▼                                        │
│  ┌─────────────────────────────────────────────────────┐            │
│  │                      TASK                           │            │
│  │               (evento pontual)                      │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌────────────┐
│   CLI    │────>│ COMMANDS │────>│ SERVICES │────>│   MODELS   │
│  (Typer) │     │          │     │          │     │ (SQLModel) │
└──────────┘     └──────────┘     └──────────┘     └────────────┘
                                        │                │
                                        ▼                ▼
                                  ┌──────────┐     ┌──────────┐
                                  │  UTILS   │     │  SQLite  │
                                  │          │     │    DB    │
                                  └──────────┘     └──────────┘
```

### Camadas

```
╔═══════════════════════════════════════════════════════════════════╗
║ PRESENTATION                                                      ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ commands/  │ routine, habit, task, timer, tag, report         │ ║
║ └───────────────────────────────────────────────────────────────┘ ║
╠═══════════════════════════════════════════════════════════════════╣
║ BUSINESS LOGIC                                                    ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ services/  │ routine, habit, habit_instance, task, timer...   │ ║
║ └───────────────────────────────────────────────────────────────┘ ║
╠═══════════════════════════════════════════════════════════════════╣
║ DATA ACCESS                                                       ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ models/    │ Routine, Habit, HabitInstance, Task, TimeLog     │ ║
║ │ database/  │ engine, migrations                               │ ║
║ └───────────────────────────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## Estados do Sistema

### HabitInstance Status

```
                    ┌─────────────┐
                    │   PENDING   │
                    │  (aguarda)  │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │    DONE     │ │  NOT_DONE   │ │   OVERDUE   │
    │ (completo)  │ │  (pulado)   │ │  (atrasado) │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │
           ▼               ▼
    ┌─────────────┐ ┌─────────────────────┐
    │  Substatus  │ │  Substatus          │
    ├─────────────┤ ├─────────────────────┤
    │ FULL        │ │ SKIPPED_JUSTIFIED   │
    │ PARTIAL     │ │ SKIPPED_UNJUSTIFIED │
    │ OVERDONE    │ │ IGNORED             │
    │ EXCESSIVE   │ └─────────────────────┘
    └─────────────┘
```

### Timer Flow

```
    ┌─────────┐
    │  IDLE   │
    └────┬────┘
         │ start
         ▼
    ┌─────────┐
    │ RUNNING │<─────────┐
    └────┬────┘          │
         │               │
    ┌────┴────┐     resume
    │         │          │
    ▼         ▼          │
┌───────┐ ┌───────┐      │
│ stop  │ │ pause │──────┘
└───┬───┘ └───────┘
    │
    ▼
┌─────────┐
│  DONE   │
└─────────┘
```

---

## Estrutura do Projeto

```
timeblock-organizer/
├── cli/
│   ├── src/timeblock/
│   │   ├── commands/          # Comandos CLI
│   │   │   ├── routine.py
│   │   │   ├── habit.py
│   │   │   ├── task.py
│   │   │   ├── timer.py
│   │   │   ├── tag.py
│   │   │   └── report.py
│   │   │
│   │   ├── services/          # Camada de negócio
│   │   │   ├── routine_service.py
│   │   │   ├── habit_service.py
│   │   │   ├── habit_instance_service.py
│   │   │   ├── task_service.py
│   │   │   ├── timer_service.py
│   │   │   └── tag_service.py
│   │   │
│   │   ├── models/            # Modelos de dados
│   │   │   ├── routine.py
│   │   │   ├── habit.py
│   │   │   ├── habit_instance.py
│   │   │   ├── task.py
│   │   │   ├── time_log.py
│   │   │   ├── tag.py
│   │   │   └── enums.py
│   │   │
│   │   ├── database/          # Persistência
│   │   │   ├── engine.py
│   │   │   └── migrations/
│   │   │
│   │   └── utils/             # Helpers
│   │
│   └── tests/                 # 466 testes
│       ├── unit/              #   377 (85%)
│       ├── integration/       #   64  (15%)
│       ├── e2e/
│       └── bdd/
│
├── docs/
│   ├── core/                  # Documentação principal
│   │   ├── architecture.md
│   │   ├── business-rules.md
│   │   ├── cli-reference.md
│   │   └── workflows.md
│   │
│   └── decisions/             # 26 ADRs
│
└── scripts/                   # Automação
```

---

## Instalação

```bash
git clone https://github.com/fabiodelllima/timeblock-organizer.git
cd timeblock-organizer/cli

python -m venv venv
source venv/bin/activate

pip install -e .
```

---

## Comandos

### Visão Geral

```
┌────────────────────────────────────────────────────────────────────┐
│ RECURSO      │ DESCRIÇÃO                                           │
├────────────────────────────────────────────────────────────────────┤
│ routine      │ Gerencia rotinas (coleções de hábitos)              │
│ habit        │ Gerencia hábitos (templates recorrentes)            │
│ habit atom   │ Gerencia instâncias de hábitos (ocorrências)        │
│ task         │ Gerencia tarefas (eventos únicos)                   │
│ timer        │ Controla cronômetro                                 │
│ tag          │ Gerencia categorias (cor + título)                  │
│ report       │ Gera relatórios de produtividade                    │
└────────────────────────────────────────────────────────────────────┘
```

### Comandos por Recurso

```
routine
├── create     Cria nova rotina
├── edit       Edita rotina existente
├── delete     Remove rotina
├── list       Lista rotinas
├── activate   Ativa rotina
└── deactivate Desativa rotina

habit
├── create     Cria novo hábito
├── edit       Edita hábito existente
├── delete     Remove hábito
├── list       Lista hábitos
├── renew      Renova instâncias
├── details    Mostra detalhes
└── skip       Wizard para pular instância

habit atom
├── create     Cria instância avulsa
├── edit       Edita instância
├── delete     Remove instância
├── list       Lista instâncias
├── skip       Pula instância
└── log        Registra tempo manualmente

task
├── create     Cria nova tarefa
├── edit       Edita tarefa
├── delete     Remove tarefa
├── list       Lista tarefas
├── complete   Marca como concluída
└── uncheck    Reverte para pendente

timer
├── start      Inicia cronômetro
├── pause      Pausa cronômetro
├── resume     Retoma cronômetro
├── stop       Para e salva
├── reset      Cancela sem salvar
└── status     Mostra status atual
```

### Exemplos

```bash
# Rotinas
timeblock routine create "Rotina Matinal"
timeblock routine activate 1
timeblock routine list

# Hábitos
timeblock habit create --title "Academia" --start 07:00 --end 08:30 --repeat weekdays
timeblock habit renew 1 month 3
timeblock habit list

# Instâncias (habit atom)
timeblock habit atom list
timeblock habit atom list -w
timeblock habit atom skip 42

# Timer
timeblock timer start 42
timeblock timer pause
timeblock timer resume
timeblock timer stop

# Tarefas
timeblock task create -l "Dentista" -D "2025-12-01 14:30"
timeblock task list
timeblock task complete 1
```

---

## Stack Tecnológica

```
┌────────────────────────────────────────────────────────────────────┐
│ COMPONENTE      │ TECNOLOGIA           │ VERSÃO                    │
├────────────────────────────────────────────────────────────────────┤
│ Runtime         │ Python               │ 3.13+                     │
│ ORM             │ SQLModel             │ 0.0.14+                   │
│ CLI Framework   │ Typer                │ 0.9.0+                    │
│ Terminal UI     │ Rich                 │ 13.7.0+                   │
│ Database        │ SQLite               │ 3.x                       │
│ Testing         │ pytest + pytest-cov  │ 8.0.0+                    │
│ Linting         │ ruff                 │ 0.1.0+                    │
│ Type Checking   │ mypy                 │ 1.8.0+                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Métricas

```
╔════════════════════════════════════════════════════════════════════╗
║                         MÉTRICAS v1.3.3                            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║   Testes          466        ████████████████████████████  100%    ║
║   Cobertura       65%        ████████████████░░░░░░░░░░░░   61%    ║
║   Modelos         8          ████████░░░░░░░░░░░░░░░░░░░░   27%    ║
║   Services        9          █████████░░░░░░░░░░░░░░░░░░░   30%    ║
║   ADRs            26         █████████████████████████░░░   83%    ║
║   Business Rules  52         ██████████████████████████░░   87%    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## Documentação

```
docs/
├── core/
│   ├── architecture.md     # Design e princípios
│   ├── business-rules.md   # 52 BRs formalizadas
│   ├── cli-reference.md    # Referência completa CLI
│   └── workflows.md        # Fluxos e estados
│
└── decisions/              # 26 ADRs documentadas
```

---

## Desenvolvimento

### Metodologia

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   DOCS   │────>│   BDD    │────>│   TDD    │────>│   CODE   │
│          │     │          │     │          │     │          │
│ BR-XXX   │     │ Gherkin  │     │ test_*   │     │ impl     │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

### Comandos

```bash
# Testes
python -m pytest tests/ -v
python -m pytest tests/unit/ -v --cov=src/timeblock

# Qualidade
ruff check .
ruff format .
mypy src/
```

### Commits

```
type(scope): Descrição em português

Tipos: feat, fix, refactor, test, docs, chore
```

---

## Roadmap

```
┌────────────────────────────────────────────────────────────────────┐
│ VERSÃO │ STATUS    │ FEATURES                                      │
├────────────────────────────────────────────────────────────────────┤
│ v1.0.0 │ [DONE]    │ CLI básica, CRUD eventos                      │
│ v1.1.0 │ [DONE]    │ Event reordering                              │
│ v1.2.x │ [DONE]    │ Logging, docs consolidados                    │
│ v1.3.3 │ [CURRENT] │ Business rules formalizadas                   │
│ v1.4.0 │ [WIP]     │ MVP Event Reordering, E2E tests               │
├────────────────────────────────────────────────────────────────────┤
│ v1.5.0 │ [PLANNED] │ Infra Foundation (Docker, CI/CD)              │
│ v2.0.0 │ [PLANNED] │ FastAPI REST API + Observabilidade            │
│ v3.0.0 │ [FUTURE]  │ Microservices Ecosystem (Kafka)               │
│ v4.0.0 │ [FUTURE]  │ Android App (Kotlin)                          │
└────────────────────────────────────────────────────────────────────┘
```
