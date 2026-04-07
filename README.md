# ATOMVS Time Planner

> Gerenciador de tempo CLI/TUI baseado em time blocking e hábitos atômicos

```plaintext
╔══════════════════════════════════════════════╗
║                                              ║
║      ◉        ▄▀█ ▀█▀ █▀█ █▀▄▀█ █░█ █▀       ║
║     ╱│╲       █▀█ ░█░ █▄█ █░▀░█ ▀▄▀ ▄█       ║
║    ○─┼─○      ─────────────────────────      ║
║     ╲│╱       Time     ░░░░░░░░░░░░░░░░      ║
║      ◉        Planner  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓      ║
║                                              ║
╚══════════════════════════════════════════════╝
```

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-1345%20passing-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-82%25-green.svg)](tests/)

---

## Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Estados do Sistema](#estados-do-sistema)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Comandos CLI](#comandos-cli)
- [Stack Tecnológica](#stack-tecnológica)
- [Documentação](#documentação)
- [Desenvolvimento](#desenvolvimento)
  - [Engenharia de Requisitos](#engenharia-de-requisitos)
  - [Análise Comportamental](#análise-comportamental)
  - [Implementação](#implementação)
- [Roadmap](#roadmap)

---

## Visão Geral

ATOMVS Time Planner é uma ferramenta de linha de comando e interface terminal para gerenciamento de tempo usando a técnica de time blocking, inspirada no livro "Atomic Habits" de James Clear. O sistema foi projetado com uma filosofia clara: detectar conflitos e fornecer informações, mantendo o usuário no controle total das decisões. Diferente de aplicativos que bloqueiam ações ou tomam decisões automáticas, o ATOMVS informa sobre sobreposições de horários e sugere reorganizações, mas nunca impõe mudanças.

A aplicação organiza o tempo através de três conceitos principais: Rotinas (coleções temáticas de hábitos), Hábitos (templates recorrentes com horários definidos) e Tarefas (eventos pontuais não recorrentes). Cada hábito gera instâncias diárias que podem ser rastreadas com timer, permitindo medir o tempo real dedicado versus o tempo planejado. A TUI (Terminal User Interface) complementa a CLI com navegação visual, dashboard interativo com 6 painéis e grade semanal de rotinas.

**Filosofia:** Conflitos são informados, nunca bloqueados. O sistema sugere, o usuário decide.

---

## Arquitetura

A arquitetura do ATOMVS segue o padrão de camadas com separação clara de responsabilidades. A camada de apresentação (CLI e TUI) comunica-se exclusivamente com a camada de serviços, que encapsula toda a lógica de negócio. Os modelos de dados utilizam SQLModel para mapeamento objeto-relacional, combinando a expressividade do Pydantic com a robustez do SQLAlchemy. A TUI compartilha 100% da camada de services com a CLI — nenhuma lógica de negócio é duplicada.

```plaintext
┌─────────────────────────────────────────────────────────┐
│                   ATOMVS TIME PLANNER                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   ROUTINE   │───>│    HABIT    │───>│   HABIT     │  │
│  │  (coleção)  │    │  (template) │    │  INSTANCE   │  │
│  └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                  │         │
│         │                  │                  v         │
│         │                  │           ┌─────────────┐  │
│         │                  │           │    TIMER    │  │
│         │                  │           │  (tracking) │  │
│         │                  │           └─────────────┘  │
│         │                  │                            │
│         v                  v                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │                      TASK                         │  │
│  │               (evento pontual)                    │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

O fluxo de dados segue uma direção unidirecional clara, desde a entrada do usuário até a persistência. CLI e TUI recebem input, delegam para services que aplicam regras de negócio, e finalmente models persistem no SQLite. Utilitários auxiliam em validações e formatações transversais.

```plaintext
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌────────────┐
│ CLI/TUI  │────>│ COMMANDS │────>│ SERVICES │────>│   MODELS   │
│ (Typer/  │     │          │     │          │     │ (SQLModel) │
│ Textual) │     └──────────┘     └──────────┘     └────────────┘
└──────────┘                            │                │
                                        v                v
                                  ┌──────────┐     ┌──────────┐
                                  │  UTILS   │     │  SQLite  │
                                  │          │     │    DB    │
                                  └──────────┘     └──────────┘
```

### Camadas

```plaintext
╔═══════════════════════════════════════════════════════════════════╗
║ PRESENTATION                                                      ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ commands/  │ routine, habit, task, timer, tag, reschedule,    │ ║
║ │            │ demo, init                                       │ ║
║ │ tui/       │ app, screens (dashboard, routines, habits,       │ ║
║ │            │ tasks, timer), 12+ widgets (Textual)             │ ║
║ └───────────────────────────────────────────────────────────────┘ ║
╠═══════════════════════════════════════════════════════════════════╣
║ BUSINESS LOGIC                                                    ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ services/  │ routine, habit, habit_instance, task, timer,     │ ║
║ │            │ tag, backup, event_reordering                    │ ║
║ └───────────────────────────────────────────────────────────────┘ ║
╠═══════════════════════════════════════════════════════════════════╣
║ DATA ACCESS                                                       ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ models/    │ Routine, Habit, HabitInstance, Task, Event,      │ ║
║ │            │ Tag, TimeLog, PauseLog, ChangeLog                │ ║
║ │ database/  │ engine, migrations                               │ ║
║ └───────────────────────────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## Estados do Sistema

O sistema de estados controla o ciclo de vida de cada entidade. HabitInstances transitam entre estados baseados em ações do usuário e passagem de tempo. O design de estados foi influenciado pela metodologia Atomic Habits, onde o foco está em manter consistência (streaks) e entender padrões de comportamento.

### HabitInstance Status

```plaintext
                    ┌─────────────┐
                    │   PENDING   │
                    │  (aguarda)  │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           v               v               v
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │    DONE     │ │  NOT_DONE   │ │   OVERDUE   │
    │ (completo)  │ │  (pulado)   │ │  (atrasado) │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │
           v               v
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

O timer implementa uma máquina de estados simples que permite rastrear tempo dedicado a cada atividade. Pausas são registradas separadamente, permitindo calcular tempo efetivo versus tempo total da sessão.

```plaintext
       ┌──────────────┐
       │     IDLE     │
       └───────┬──────┘
               │ start (t)
               v
       ┌──────────────┐
       │   RUNNING    │<───────────┐
       └───────┬──────┘            │
               │                   │
       ┌───────┼──────┐       resume
       │       │      │       (space)
       v       │      v            │
┌──────────┐   │  ┌───────────┐    │
│ stop (s) │   │  │  pause    │────┘
└───┬──────┘   │  │  (space)  │
    │          │  └───────────┘
    v          v
┌──────────┐ ┌────────────────┐
│   DONE   │ │ CANCELLED (c)  │
└──────────┘ └────────────────┘
```

---

## Estrutura do Projeto

O projeto segue uma estrutura modular que facilita navegação e manutenção. O código fonte reside em `src/timeblock/`, testes em `tests/`, e documentação em `docs/`. Esta separação permite desenvolvimento independente de cada camada.

```plaintext
atomvs-timeblock-terminal/
├── src/timeblock/
│   ├── commands/       # Comandos CLI (routine, habit, task, timer, tag, reschedule, demo, init)
│   │
│   ├── services/       # Lógica de negócio (8 services)
│   ├── models/         # Modelos SQLModel (9 entidades + enums)
│   ├── database/       # Engine SQLite e migrations
│   ├── tui/            # Interface terminal (Textual)
│   │   ├── screens/    # Dashboard, Routines, Habits, Tasks, Timer
│   │   └── widgets/    # 12+ widgets: panels, nav, modais, overlays
│   └── utils/          # Helpers: validators, date_parser, logger
│
├── tests/              # 1345 testes   (116 arquivos)
│   ├── unit/           #   79 arquivos (~75%)
│   ├── integration/    #   17 arquivos (~11%)
│   ├── bdd/            #   11 arquivos (~10%)
│   └── e2e/            #    9 arquivos  (~4%)
│
├── docs/               # Documentação (framework Diataxis + arc42)
│   ├── tutorials/      #   Ponto de entrada para novos contribuidores
│   ├── guides/         #   How-to: CI, testing, snapshots, refactoring
│   ├── reference/      #   BRs (114), technical-debt, roadmap, sprints
│   ├── explanation/    #   Arquitetura, metodologia, domínio
│   ├── decisions/      #   46 ADRs (Architecture Decision Records)
│   └── diagrams/       #   14 diagramas Mermaid (ER, C4, states, sequences)
│
└── scripts/            # Automação
```

---

## Instalação

A instalação requer Python 3.13 ou superior. O projeto utiliza um ambiente virtual isolado para gerenciar dependências, evitando conflitos com outras aplicações Python no sistema.

```bash
git clone https://github.com/fabiodelllima/atomvs-timeblock-terminal.git
cd atomvs-timeblock-terminal

python -m venv venv
source venv/bin/activate

pip install -e ".[tui]"
```

---

## Comandos CLI

A interface de linha de comando foi projetada para ser intuitiva e consistente. Cada recurso (routine, habit, task, timer, tag) possui um conjunto padronizado de subcomandos que seguem convenções POSIX. O comando `atomvs` sem argumentos abre a TUI.

### Visão Geral

| Recurso    | Descrição                                   |
| ---------- | ------------------------------------------- |
| routine    | Gerencia rotinas (coleções de hábitos)      |
| habit      | Gerencia hábitos (templates recorrentes)    |
| habit atom | Gerencia instâncias (list, generate, done)  |
| task       | Gerencia tarefas (eventos únicos)           |
| timer      | Controla cronômetro (start, pause, stop)    |
| tag        | Gerencia categorias (cor + nome)            |
| reschedule | Detecta conflitos de horários               |
| demo       | Popula/limpa banco com dados demonstrativos |
| init       | Inicializa banco de dados                   |

### Exemplos

```bash
# TUI (interface visual)
atomvs                      # Sem argumentos abre a TUI

# Rotinas
atomvs routine create "Rotina Matinal"
atomvs routine activate 1
atomvs routine list

# Hábitos
atomvs habit create --title "Academia" --start 07:00 --end 08:30 --repeat WEEKDAYS
atomvs habit list
atomvs habit atom list --today

# Timer
atomvs timer start --schedule 1
atomvs timer pause
atomvs timer resume
atomvs timer stop

# Tarefas
atomvs task create --title "Dentista" --datetime "2026-03-15 14:30"
atomvs task list --pending
atomvs task check 1

# Conflitos
atomvs reschedule conflicts --date 2026-04-10

# Demo (dados demo)
atomvs demo create          # 3 rotinas + 8 tasks
atomvs demo clear           # Remove dados demo
```

---

## Stack Tecnológica

A stack foi escolhida priorizando produtividade do desenvolvedor, type safety e facilidade de manutenção. SQLModel combina validação Pydantic com ORM SQLAlchemy em uma única definição de modelo. Textual fornece a TUI com widgets ricos e CSS-like styling.

| Componente    | Tecnologia          | Versão   |
| ------------- | ------------------- | -------- |
| Runtime       | Python              | 3.13+    |
| ORM           | SQLModel            | 0.0.24+  |
| CLI Framework | Typer               | 0.19.0+  |
| TUI Framework | Textual             | 0.89.0+  |
| Terminal UI   | Rich                | 14.0.0+  |
| Database      | SQLite              | 3.x      |
| Testing       | pytest + pytest-cov | 8.0+     |
| Linting       | ruff                | 0.14.0+  |
| Type Checking | basedpyright        | standard |
| Type Checking | mypy (CI)           | 1.18.0+  |

---

## Documentação

A documentação técnica segue o framework Diataxis, organizando conteúdo por função: tutorials (aprendizado), guides (how-to), reference (consulta) e explanation (compreensão). Em complemento, a estrutura dos diretórios transversais decisions/ (ADRs) e diagrams/ (diagramas arquiteturais), seguem convenções arc42.

```plaintext
docs/
├── tutorials/                        # Ponto de entrada para contribuidores
│   └── developer-reference.md
│
├── guides/                           # How-to prático
│   ├── development-workflow.md
│   ├── testing-patterns.md
│   ├── snapshot-testing.md
│   ├── ci-optimization.md
│   ├── cicd-flow.md
│   ├── refactoring-catalog.md
│   └── manual-testing-checklist.md
│
├── reference/                        # Consulta factual
│   ├── business-rules/               # 114 BRs formalizadas (15 domínios)
│   ├── tui/                          # Mockups e specs de telas TUI
│   ├── roadmap.md
│   ├── sprints.md
│   ├── technical-debt.md
│   ├── quality-metrics.md
│   ├── cli-reference.md
│   └── workflows.md
│
├── explanation/                      # Contexto e raciocínio
│   ├── architecture.md
│   ├── development-methodology.md
│   ├── domain-concepts.md
│   └── agenda-overlap-rendering.md
│
├── decisions/                        # 46 ADRs (formato Nygard adaptado)
│
└── diagrams/                         # 14 diagramas Mermaid
    ├── data/                         # ER diagram, class diagram
    ├── states/                       # HabitInstance, Task, Timer
    ├── sequences/                    # Timer flow, event reordering, habit generation
    ├── activity/                     # Habit execution, user daily flow
    ├── c4-model/                     # L1 context, L2 containers, L3 components
    └── infrastructure/               # Deployment
```

---

## Desenvolvimento

O projeto segue uma metodologia de desenvolvimento orientada por especificação, integrando práticas de engenharia de requisitos com técnicas modernas de validação automatizada.

### Engenharia de Requisitos

Requisitos funcionais são formalizados como Business Rules (BRs) antes da implementação. Cada BR recebe identificador único (BR-DOMAIN-XXX) e documenta comportamento esperado, restrições e casos de borda. Este artefato estabelece o contrato entre especificação e código, servindo como base para rastreabilidade.

Referências:

- ISO/IEC/IEEE 29148:2018: Systems and Software Engineering - Life Cycle Processes - Requirements Engineering
- SWEBOK v4.0, Chapter 1: Software Requirements. IEEE Computer Society, 2024
- Sommerville, I. Software Engineering, 10th ed. Pearson, 2016
- Wiegers, K.; Beatty, J. Software Requirements, 3rd ed. Microsoft Press, 2013

### Análise Comportamental

BRs são decompostas em cenários executáveis usando Gherkin (Given/When/Then). Os cenários descrevem fluxos concretos em linguagem de domínio, funcionando simultaneamente como especificação e teste de aceitação.

Referências:

- North, D. Introducing BDD. Better Software, 2006
- Adzic, G. Specification by Example. Manning, 2011
- Cucumber Documentation. cucumber.io
- ISO/IEC/IEEE 29119-5:2016: Software Testing - Keyword-Driven Testing

### Implementação

Código é desenvolvido seguindo Test-Driven Development. Testes referenciam BRs pela nomenclatura (test_br_xxx), mantendo rastreabilidade bidirecional entre requisitos, testes e implementação. A pirâmide de testes distribui validações em quatro níveis: unitário (~75%), integração (~11%), BDD (~10%) e end-to-end (~4%).

Referências:

- Beck, K. Test-Driven Development: By Example. Addison-Wesley, 2002
- Meszaros, G. xUnit Test Patterns. Addison-Wesley, 2007
- Fowler, M. TestPyramid. martinfowler.com, 2012
- ISO/IEC/IEEE 29119-1:2022: Software and Systems Engineering - Software Testing

### Comandos

```bash
# Testes
python -m pytest tests/ -v
python -m pytest tests/e2e/ -v
python -m pytest tests/ --cov=src/timeblock

# Qualidade
ruff check .
ruff format .
basedpyright src/
```

---

## Roadmap

O roadmap está organizado em releases incrementais, cada uma construindo sobre a anterior. A versão v1.7.0 consolidou a TUI com dashboard CRUD completo, MetricsPanel e semântica de streak alinhada com Atomic Habits. A versão v1.7.1 (em desenvolvimento) foca em polish: auditoria de diagramas, atualização do README e responsividade.

| Versão | Status    | Features                                 |
| ------ | --------- | ---------------------------------------- |
| v1.0.0 | [DONE]    | CLI básica, CRUD eventos                 |
| v1.1.0 | [DONE]    | Event reordering                         |
| v1.2.x | [DONE]    | Logging, docs consolidados               |
| v1.3.x | [DONE]    | Date parser, BDD tests, DI refactor      |
| v1.4.0 | [DONE]    | Business rules formalizadas, 32 ADRs     |
| v1.5.0 | [DONE]    | CI/CD dual-repo, i18n, 873 testes        |
| v1.6.0 | [DONE]    | Docker, DevSecOps, 87% cobertura         |
| v1.7.0 | [DONE]    | TUI Textual, dashboard CRUD, 1345 testes |
| v1.7.1 | [CURRENT] | Polish: diagramas, README, docs          |
| v1.8.0 | [PLANNED] | AgendaPanel redesign, sidebar compacta   |
| v2.0.0 | [PLANNED] | FastAPI REST API + Observabilidade       |
| v3.0.0 | [FUTURE]  | Microservices Ecosystem (Kafka)          |
| v4.0.0 | [FUTURE]  | Android App (Kotlin)                     |

---

```plaintext
┌────────────┐
│ ▓▓▓▓░░░░▓▓ │
│ ░░▓▓▓▓▓░░░ │   A T O M V S
│ ▓▓░░░░▓▓▓▓ │
└────────────┘
```
