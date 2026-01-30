# TimeBlock Organizer

> Gerenciador de tempo CLI baseado em time blocking e hábitos atômicos

```
╔══════════════════════════════════════════════╗
║                                              ║
║      ◉        ▄▀█ ▀█▀ █▀█ █▀▄▀█ █░█ █▀       ║
║     ╱│╲       █▀█ ░█░ █▄█ █░▀░█ ▀▄▀ ▄█       ║
║    ○─┼─○      ─────────────────────────      ║
║     ╲│╱       TimeBlock  ░░░░░░░░░░░░░░      ║
║      ◉        Organizer  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓      ║
║                                              ║
╚══════════════════════════════════════════════╝
```

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-685%20passing-success.svg)](cli/tests/)
[![Coverage](https://img.shields.io/badge/coverage-71%25-green.svg)](cli/tests/)

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

TimeBlock Organizer é uma ferramenta de linha de comando para gerenciamento de tempo usando a técnica de time blocking, inspirada no livro "Atomic Habits" de James Clear. O sistema foi projetado com uma filosofia clara: detectar conflitos e fornecer informações, mantendo o usuário no controle total das decisões. Diferente de aplicativos que bloqueiam ações ou tomam decisões automáticas, o TimeBlock informa sobre sobreposições de horários e sugere reorganizações, mas nunca impõe mudanças.

A aplicação organiza o tempo através de três conceitos principais: Rotinas (coleções temáticas de hábitos), Hábitos (templates recorrentes com horários definidos) e Tarefas (eventos pontuais não recorrentes). Cada hábito gera instâncias diárias que podem ser rastreadas com timer, permitindo medir o tempo real dedicado versus o tempo planejado.

**Filosofia:** Conflitos são informados, nunca bloqueados. O sistema sugere, o usuário decide.

---

## Arquitetura

A arquitetura do TimeBlock segue o padrão de camadas com separação clara de responsabilidades. A camada de apresentação (CLI) comunica-se exclusivamente com a camada de serviços, que encapsula toda a lógica de negócio. Os modelos de dados utilizam SQLModel para mapeamento objeto-relacional, combinando a expressividade do Pydantic com a robustez do SQLAlchemy.

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

O fluxo de dados segue uma direção unidirecional clara, desde a entrada do usuário até a persistência. Comandos CLI recebem input, delegam para services que aplicam regras de negócio, e finalmente models persistem no SQLite. Utilitários auxiliam em validações e formatações transversais.

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌────────────┐
│   CLI    │────>│ COMMANDS │────>│ SERVICES │────>│   MODELS   │
│  (Typer) │     │          │     │          │     │ (SQLModel) │
└──────────┘     └──────────┘     └──────────┘     └────────────┘
                                        │                │
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

O projeto segue uma estrutura modular que facilita navegação e manutenção. O código fonte reside em `cli/src/timeblock/`, testes em `cli/tests/`, e documentação em `docs/`. Esta separação permite desenvolvimento independente de cada camada.

```
timeblock-organizer/
├── cli/
│   ├── src/timeblock/
│   │   ├── commands/          # Comandos CLI (routine, habit, task, timer)
│   │   ├── services/          # Lógica de negócio
│   │   ├── models/            # Modelos SQLModel
│   │   ├── database/          # Engine e migrations
│   │   └── utils/             # Helpers e validadores
│   │
│   └── tests/                 # 685 testes
│       ├── unit/              #   513 (75%)
│       ├── integration/       #   83  (12%)
│       ├── e2e/               #   42  (6%)
│       └── bdd/               #   7   (1%)
│
├── docs/
│   ├── core/                  # Documentação principal
│   └── decisions/             # 27 ADRs
│
└── scripts/                   # Automação
```

---

## Instalação

A instalação é simples e requer apenas Python 3.13 ou superior. O projeto utiliza um ambiente virtual isolado para gerenciar dependências, evitando conflitos com outras aplicações Python no sistema.

```bash
git clone https://github.com/fabiodelllima/timeblock-organizer.git
cd timeblock-organizer/cli

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
```

---

## Stack Tecnológica

A stack foi escolhida priorizando produtividade do desenvolvedor, type safety e facilidade de manutenção. Python 3.13+ permite uso de features modernas como pattern matching e improved generics. SQLModel combina validação Pydantic com ORM SQLAlchemy em uma única definição de modelo.

| Componente    | Tecnologia          | Versão   |
| ------------- | ------------------- | -------- |
| Runtime       | Python              | 3.13+    |
| ORM           | SQLModel            | 0.0.31+  |
| CLI Framework | Typer               | 0.21.1+  |
| Terminal UI   | Rich                | 14.3.1+  |
| Database      | SQLite              | 3.x      |
| Testing       | pytest + pytest-cov | 9.0.2+   |
| Linting       | ruff                | 0.14.14+ |
| Type Checking | mypy                | 1.19.1+  |

---

## Documentação

A documentação técnica está organizada em níveis de detalhe. O diretório `core/` contém documentos de referência essenciais, enquanto `decisions/` preserva o histórico de decisões arquiteturais através de ADRs (Architecture Decision Records).

```
docs/
├── core/
│   ├── architecture.md     # Design e princípios
│   ├── business-rules.md   # 67 BRs formalizadas
│   ├── cli-reference.md    # Referência completa CLI
│   ├── quality-metrics.md  # Métricas de qualidade
│   └── workflows.md        # Fluxos e estados
│
└── decisions/              # 27 ADRs documentadas
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

Código é desenvolvido seguindo Test-Driven Development. Testes referenciam BRs pela nomenclatura (test_br_xxx), mantendo rastreabilidade bidirecional entre requisitos, testes e implementação. A pirâmide de testes distribui validações em três níveis: unitário (75%), integração (12%) e end-to-end (6%).

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

O roadmap está organizado em releases incrementais, cada uma construindo sobre a anterior. A versão atual (v1.4.x) consolidou a formalização de business rules e expandiu significativamente a cobertura de testes E2E. Versões futuras expandirão para API REST, microservices e aplicativo móvel.

| Versão | Status    | Features                             |
| ------ | --------- | ------------------------------------ |
| v1.0.0 | [DONE]    | CLI básica, CRUD eventos             |
| v1.1.0 | [DONE]    | Event reordering                     |
| v1.2.x | [DONE]    | Logging, docs consolidados           |
| v1.3.x | [DONE]    | Date parser, BDD tests, DI refactor  |
| v1.4.0 | [DONE]    | Business rules formalizadas, 27 ADRs |
| v1.4.1 | [CURRENT] | E2E tests expansion (685 tests, 71%) |
| v1.5.0 | [PLANNED] | Infra Foundation (Docker, CI/CD)     |
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
