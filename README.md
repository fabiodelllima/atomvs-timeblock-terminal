# ATOMVS TimeBlock Terminal

> Gerenciador de tempo CLI/TUI baseado em time blocking e hábitos atômicos

```
╔══════════════════════════════════════════════╗
║                                              ║
║      ◉        ▄▀█ ▀█▀ █▀█ █▀▄▀█ █░█ █▀       ║
║     ╱│╲       █▀█ ░█░ █▄█ █░▀░█ ▀▄▀ ▄█       ║
║    ○─┼─○      ─────────────────────────      ║
║     ╲│╱       TimeBlock  ░░░░░░░░░░░░░░      ║
║      ◉          Terminal ▓▓▓▓▓▓▓▓▓▓▓▓▓▓      ║
║                                              ║
╚══════════════════════════════════════════════╝
```

[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-797%20passing-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-87%25-green.svg)](tests/)

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

ATOMVS TimeBlock Terminal é uma ferramenta de linha de comando e interface terminal para gerenciamento de tempo usando a técnica de time blocking, inspirada no livro "Atomic Habits" de James Clear. O sistema foi projetado com uma filosofia clara: detectar conflitos e fornecer informações, mantendo o usuário no controle total das decisões. Diferente de aplicativos que bloqueiam ações ou tomam decisões automáticas, o TimeBlock informa sobre sobreposições de horários e sugere reorganizações, mas nunca impõe mudanças.

A aplicação organiza o tempo através de três conceitos principais: Rotinas (coleções temáticas de hábitos), Hábitos (templates recorrentes com horários definidos) e Tarefas (eventos pontuais não recorrentes). Cada hábito gera instâncias diárias que podem ser rastreadas com timer, permitindo medir o tempo real dedicado versus o tempo planejado. A partir da v1.7.0, uma TUI (Terminal User Interface) complementa a CLI com navegação visual, dashboard interativo e grade semanal de rotinas.

**Filosofia:** Conflitos são informados, nunca bloqueados. O sistema sugere, o usuário decide.

---

## Arquitetura

A arquitetura do TimeBlock segue o padrão de camadas com separação clara de responsabilidades. A camada de apresentação (CLI e TUI) comunica-se exclusivamente com a camada de serviços, que encapsula toda a lógica de negócio. Os modelos de dados utilizam SQLModel para mapeamento objeto-relacional, combinando a expressividade do Pydantic com a robustez do SQLAlchemy. A TUI compartilha 100% da camada de services com a CLI — nenhuma lógica de negócio é duplicada.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ATOMVS TIMEBLOCK TERMINAL                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │   ROUTINE   │───>│    HABIT    │───>│   HABIT     │              │
│  │  (coleção)  │    │  (template) │    │  INSTANCE   │              │
│  └─────────────┘    └─────────────┘    └─────────────┘              │
│         │                  │                  │                     │
│         │                  │                  v                     │
│         │                  │           ┌─────────────┐              │
│         │                  │           │    TIMER    │              │
│         │                  │           │  (tracking) │              │
│         │                  │           └─────────────┘              │
│         │                  │                                        │
│         v                  v                                        │
│  ┌─────────────────────────────────────────────────────┐            │
│  │                      TASK                           │            │
│  │               (evento pontual)                      │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

O fluxo de dados segue uma direção unidirecional clara, desde a entrada do usuário até a persistência. CLI e TUI recebem input, delegam para services que aplicam regras de negócio, e finalmente models persistem no SQLite. Utilitários auxiliam em validações e formatações transversais.

```
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

```
╔═══════════════════════════════════════════════════════════════════╗
║ PRESENTATION                                                      ║
║ ┌───────────────────────────────────────────────────────────────┐ ║
║ │ commands/  │ routine, habit, task, timer, tag, list           │ ║
║ │ tui/       │ app, screens, widgets (Textual)                  │ ║
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

O sistema de estados controla o ciclo de vida de cada entidade. HabitInstances transitam entre estados baseados em ações do usuário e passagem de tempo. O design de estados foi influenciado pela metodologia Atomic Habits, onde o foco está em manter consistência (streaks) e entender padrões de comportamento.

### HabitInstance Status

```
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

```
    ┌─────────────┐
    │    IDLE     │
    └──────┬──────┘
           │ start
           v
    ┌─────────────┐
    │   RUNNING   │<────────┐
    └──────┬──────┘         │
           │                │
     ┌─────┴─────┐      resume
     │           │          │
     v           v          │
┌────────┐  ┌────────┐      │
│  stop  │  │ pause  │──────┘
└────┬───┘  └────────┘
     │
     v
┌─────────────┐
│    DONE     │
└─────────────┘
```

---

## Estrutura do Projeto

O projeto segue uma estrutura modular que facilita navegação e manutenção. O código fonte reside em `src/timeblock/`, testes em `tests/`, e documentação em `docs/`. Esta separação permite desenvolvimento independente de cada camada.

```
atomvs-timeblock-terminal/
├── src/timeblock/
│   ├── commands/          # Comandos CLI (routine, habit, task, timer)
│   ├── services/          # Lógica de negócio
│   ├── models/            # Modelos SQLModel
│   ├── database/          # Engine e migrations
│   ├── tui/               # Interface terminal (Textual)
│   │   ├── screens/       # Dashboard, Routines, Habits, Tasks, Timer
│   │   └── widgets/       # NavBar, Grid, CommandBar, HelpOverlay
│   └── utils/             # Helpers e validadores
│
├── tests/                 # 797 testes
│   ├── unit/              #   595 (74.7%)
│   ├── integration/       #   116 (14.6%)
│   ├── bdd/               #    56 (7.0%)
│   └── e2e/               #    30 (3.8%)
│
├── docs/
│   ├── core/              # Documentação principal
│   ├── decisions/         # 32 ADRs
│   └── tui/               # Mockups de telas TUI
│
└── scripts/               # Automação
```

---

## Instalação

A instalação é simples e requer apenas Python 3.14 ou superior. O projeto utiliza um ambiente virtual isolado para gerenciar dependências, evitando conflitos com outras aplicações Python no sistema.

```bash
git clone https://github.com/fabiodelllima/atomvs-timeblock-terminal.git
cd atomvs-timeblock-terminal

python -m venv venv
source venv/bin/activate

pip install -e .
```

---

## Comandos CLI

A interface de linha de comando foi projetada para ser intuitiva e consistente. Cada recurso (routine, habit, task, timer) possui um conjunto padronizado de subcomandos que seguem convenções POSIX. Flags curtas (-t, -D) estão disponíveis para comandos frequentes.

### Visão Geral

| Recurso | Descrição                                |
| ------- | ---------------------------------------- |
| routine | Gerencia rotinas (coleções de hábitos)   |
| habit   | Gerencia hábitos (templates recorrentes) |
| task    | Gerencia tarefas (eventos únicos)        |
| timer   | Controla cronômetro                      |
| list    | Lista eventos com filtros temporais      |
| tag     | Gerencia categorias (cor + título)       |

### Exemplos

```bash
# Rotinas
timeblock routine create "Rotina Matinal"
timeblock routine activate 1
timeblock routine list

# Hábitos
timeblock habit create --title "Academia" --start 07:00 --end 08:30 --repeat weekdays
timeblock habit list

# Timer
timeblock timer start --schedule 1
timeblock timer pause
timeblock timer resume
timeblock timer stop

# Tarefas
timeblock task create --title "Dentista" --datetime "2025-12-01 14:30"
timeblock task list --pending
timeblock task check 1

# Listagem com filtros
timeblock list --day 0        # Hoje
timeblock list --week 0       # Esta semana
timeblock list --month +1     # Próximo mês
timeblock list --all          # Todos os eventos

# TUI (interface visual)
timeblock                     # Sem argumentos abre a TUI
```

---

## Stack Tecnológica

A stack foi escolhida priorizando produtividade do desenvolvedor, type safety e facilidade de manutenção. Python 3.14 permite uso de features modernas como pattern matching e improved generics. SQLModel combina validação Pydantic com ORM SQLAlchemy em uma única definição de modelo. Textual fornece a TUI com widgets ricos e CSS-like styling.

| Componente    | Tecnologia          | Versão   |
| ------------- | ------------------- | -------- |
| Runtime       | Python              | 3.14+    |
| ORM           | SQLModel            | 0.0.31+  |
| CLI Framework | Typer               | 0.21.1+  |
| TUI Framework | Textual             | 1.0.0+   |
| Terminal UI   | Rich                | 14.3.1+  |
| Database      | SQLite              | 3.x      |
| Testing       | pytest + pytest-cov | 9.0.2+   |
| Linting       | ruff                | 0.14.14+ |
| Type Checking | mypy                | 1.19.1+  |

---

## Documentação

A documentação técnica está organizada em níveis de detalhe. O diretório `core/` contém documentos de referência essenciais, `decisions/` preserva o histórico de decisões arquiteturais através de ADRs (Architecture Decision Records), e `tui/` contém mockups de design das telas da interface terminal.

```
docs/
├── core/
│   ├── architecture.md     # Design e princípios
│   ├── business-rules.md   # 51 BRs formalizadas
│   ├── cli-reference.md    # Referência completa CLI
│   ├── quality-metrics.md  # Métricas de qualidade
│   ├── roadmap.md          # Estado e planejamento
│   └── workflows.md        # Fluxos e estados
│
├── decisions/              # 32 ADRs documentadas
│
└── tui/                    # Mockups de telas TUI
    ├── dashboard-mockup-v3.md
    └── routines-weekly-mockup.md
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

BRs são decompostas em cenários executáveis usando Gherkin (DADO/QUANDO/ENTÃO). Os cenários descrevem fluxos concretos em linguagem de domínio, funcionando simultaneamente como especificação e teste de aceitação.

Referências:

- North, D. Introducing BDD. Better Software, 2006
- Adzic, G. Specification by Example. Manning, 2011
- Cucumber Documentation. cucumber.io
- ISO/IEC/IEEE 29119-5:2016: Software Testing - Keyword-Driven Testing

### Implementação

Código é desenvolvido seguindo Test-Driven Development. Testes referenciam BRs pela nomenclatura (test_br_xxx), mantendo rastreabilidade bidirecional entre requisitos, testes e implementação. A pirâmide de testes distribui validações em quatro níveis: unitário (74.7%), integração (14.6%), BDD (7.0%) e end-to-end (3.8%).

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
mypy src/
```

---

## Roadmap

O roadmap está organizado em releases incrementais, cada uma construindo sobre a anterior. A versão v1.6.0 consolidou a infraestrutura com Docker, DevSecOps e cobertura a 87%. A versão atual (v1.7.0) introduz a TUI com Textual como interface visual complementar à CLI.

| Versão | Status    | Features                             |
| ------ | --------- | ------------------------------------ |
| v1.0.0 | [DONE]    | CLI básica, CRUD eventos             |
| v1.1.0 | [DONE]    | Event reordering                     |
| v1.2.x | [DONE]    | Logging, docs consolidados           |
| v1.3.x | [DONE]    | Date parser, BDD tests, DI refactor  |
| v1.4.0 | [DONE]    | Business rules formalizadas, 32 ADRs |
| v1.5.0 | [DONE]    | CI/CD dual-repo, i18n, 873 testes    |
| v1.6.0 | [DONE]    | Docker, DevSecOps, 87% cobertura     |
| v1.7.0 | [CURRENT] | TUI com Textual (ADR-031)            |
| v2.0.0 | [PLANNED] | FastAPI REST API + Observabilidade   |
| v3.0.0 | [FUTURE]  | Microservices Ecosystem (Kafka)      |
| v4.0.0 | [FUTURE]  | Android App (Kotlin)                 |

---

```
┌────────────┐
│ ▓▓▓▓░░░░▓▓ │
│ ░░▓▓▓▓▓░░░ │   A T O M V S
│ ▓▓░░░░▓▓▓▓ │
└────────────┘
```
