# Arquitetura TimeBlock Organizer

**Versão:** 2.2.0

**Data:** 28 de Novembro de 2025

**Status:** Consolidado (SSOT)

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Filosofia de Controle do Usuário](#2-filosofia-de-controle-do-usuário)
3. [Stack Tecnológica](#3-stack-tecnológica)
4. [Camadas da Aplicação](#4-camadas-da-aplicação)
5. [Modelos de Dados](#5-modelos-de-dados)
6. [Fluxos Principais](#6-fluxos-principais)
7. [Decisões Arquiteturais](#7-decisões-arquiteturais)
8. [Padrões e Convenções](#8-padrões-e-convenções)
9. [Evolução Futura](#9-evolução-futura)
10. [Deployment Options](#10-deployment-options)
11. [Processo de Desenvolvimento](#11-processo-de-desenvolvimento)
12. [CI/CD e Branch Protection](#12-cicd-e-branch-protection)
13. [Arquitetura Multi-Plataforma](#13-arquitetura-multi-plataforma-v20)

---

## 1. Visão Geral

TimeBlock Organizer é uma aplicação CLI para gerenciamento de tempo baseada nos princípios de "Atomic Habits" de James Clear.

### 1.1. Princípios Arquiteturais

1. **Simplicidade** - Arquitetura direta sem over-engineering
2. **Separação de Responsabilidades** - Service pattern claro
3. **Testabilidade** - Design orientado a testes
4. **Stateless** - Operações sem estado persistente em memória
5. **Database-First** - SQLite como fonte de verdade
6. **User Control** - Sistema informa, usuário decide

### 1.2. Características Principais

- **CLI-First**: Interface de linha de comando como cidadão de primeira classe
- **Embedded Database**: SQLite sem servidor externo
- **Offline-First**: Funciona perfeitamente sem conexão
- **Sync-Ready**: Arquitetura preparada para sincronização futura
- **Logging Estruturado**: Observabilidade desde o início

### 1.3. Diagrama de Alto Nível

O diagrama abaixo representa a arquitetura em camadas do sistema, desde a interface de usuário (CLI/TUI) até a persistência (SQLite), com a service layer como barreira que isola lógica de negócio das camadas de apresentação e dados.

```
┌─────────────────────────────────────────────────────────────┐
│                      Usuário (CLI)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────┐
│                   Commands Layer                            │
│              (Typer/Click, parsing, output)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────┐
│                   Services Layer                            │
│           (Business logic, orchestration)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────┐
│                    Models Layer                             │
│              (SQLModel, relationships)                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer                            │
│              (SQLite, engine management)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Filosofia de Controle do Usuário

A filosofia de controle do usuário permeia todas as decisões de design do sistema. O TimeBlock existe para informar e facilitar, não para restringir ou decidir. Esta seção formaliza os princípios que guiam como o sistema interage com a agenda do usuário, desde detecção de conflitos até sugestões de reorganização.

### 2.1. Princípio Fundamental

O TimeBlock é construído sobre o princípio de que sua função é **informar, sugerir e facilitar, mas NUNCA decidir**. Cada alteração na agenda do usuário requer aprovação explícita.

### 2.2. O Problema que Evitamos

Muitos sistemas de produtividade tentam ser "inteligentes" tomando decisões automáticas. Eles reordenam tarefas, ajustam prioridades e movem eventos baseados em algoritmos que presumem entender o contexto completo da vida do usuário.

**Exemplo do problema:**

- Sistema detecta que usuário executa "Academia" às 18h em vez do horário planejado às 7h
- Sistema "inteligente" move automaticamente futuras instâncias para 18h
- **Problema:** Usuário está temporariamente ajustando devido a projeto com deadline, mas seu objetivo real continua sendo ir a academia de manhã
- Sistema reforçou comportamento não desejado

### 2.3. Nossa Solução: Informação sem Imposição

**Detecção de Conflitos:**

- Sistema detecta sobreposição temporal
- Apresenta informações claras
- NÃO propõe solução automaticamente

**Ajuste de Horários:**

- Ajuste em um dia afeta apenas aquele dia
- Plano ideal (Routine) permanece intocado
- Cada dia é nova oportunidade de seguir a Routine

**Priorização:**

- Sistema NÃO aplica regras de priorização automática
- Apresenta eventos e permite usuário escolher

### 2.4. Routine como Norte Verdadeiro

A Routine funciona como norte verdadeiro do sistema: define a intenção do usuário para a semana e serve como referência contra a qual o dia real é comparado. Desvios são detectados e informados, mas nunca corrigidos automaticamente.

```
┌─────────────────────────────────────────────────────┐
│                    ROUTINE                          │
│              (Plano Ideal - Imutável)               │
│                                                     │
│   Academia: 07:00-08:00 WEEKDAYS                    │
│   Meditação: 06:30-07:00 EVERYDAY                   │
└─────────────────────────────────────────────────────┘
                          │
                          │ Gera instancias
                          v
┌─────────────────────────────────────────────────────┐
│               HABIT INSTANCES                       │
│            (Realidade - Flexível)                   │
│                                                     │
│   Seg 25/11: Academia 07:00 [DONE]                  │
│   Ter 26/11: Academia 18:00 [DONE] (ajustado)       │
│   Qua 27/11: Academia 07:00 [PENDING]               │
└─────────────────────────────────────────────────────┘
```

**Separação:**

- **Routine:** Intenções e objetivos (o que usuário aspira)
- **HabitInstance:** O que realmente acontece (ajustes, atrasos)

### 2.5. Implicações no Código

#### **Princípio 1: Detecção sem Ação**

```python
# CORRETO: Detecta e retorna informações
def detect_conflicts(event_id: int) -> list[Conflict]:
    conflicts = query_overlapping_events(event_id)
    return conflicts  # Apenas retorna, NAO modifica

# CORRETO: Ação separada que requer confirmação
def apply_user_resolution(conflict_id: int, user_choice: Resolution):
    if user_choice.confirmed:
        apply_changes(user_choice.changes)
```

```python
# INCORRETO: Detecção e ação misturadas
def detect_and_resolve_conflicts(event_id: int):
    conflicts = query_overlapping_events(event_id)
    for conflict in conflicts:
        auto_resolve(conflict)  # NUNCA fazer isso
```

#### **Princípio 2: Preservação de Template**

```python
# CORRETO: Ajuste afeta apenas instancia
def adjust_instance(instance_id: int, new_start: time):
    instance = get_instance(instance_id)
    instance.scheduled_start = new_start
    # Habit (template) permanece inalterado
    save(instance)
```

#### **Princípio 3: Confirmação Explicita**

```python
# CORRETO: Requer confirmação
if conflicts_detected:
    print("Conflitos encontrados:")
    for c in conflicts:
        print(f"  - {c.description}")

    if typer.confirm("Continuar mesmo assim?"):
        proceed()
```

---

## 3. Stack Tecnológica

A stack tecnológica foi selecionada priorizando produtividade do desenvolvedor, type safety e facilidade de manutenção. Python 3.13+ como runtime permite uso de features modernas, SQLModel unifica validação e ORM em definições únicas, e Rich/Textual fornecem capacidades de terminal avançadas para CLI e TUI respectivamente.

### 3.1. Core

| Componente | Tecnologia | Versão | Razão                     |
| ---------- | ---------- | ------ | ------------------------- |
| Linguagem  | Python     | 3.13+  | Produtividade, ecosystem  |
| CLI        | Typer      | 0.x    | Type hints, auto-complete |
| ORM        | SQLModel   | 0.0.x  | Pydantic + SQLAlchemy     |
| Database   | SQLite     | 3.x    | Zero-config, portável     |
| Output     | Rich       | 13.x   | Terminal formatting       |

### 3.2. Desenvolvimento

| Componente | Tecnologia | Razão                  |
| ---------- | ---------- | ---------------------- |
| Testes     | pytest     | Padrão de facto Python |
| Coverage   | pytest-cov | Métricas de cobertura  |
| Linting    | ruff       | Rápido, moderno        |
| Type Check | mypy       | Segurança de tipos     |
| VCS        | Git        | Gitflow workflow       |

### 3.3. Dependências Principais

As dependências são declaradas no pyproject.toml com versões mínimas pinadas. O core mantém apenas três dependências diretas (SQLModel, Typer, Rich), enquanto ferramentas de desenvolvimento e a TUI são gerenciadas como dependency groups opcionais.

```
sqlmodel>=0.0.14
typer>=0.9.0
rich>=13.0.0
python-dateutil>=2.8.0
```

**Filosofia:** Mínimas dependências, máxima estabilidade.

---

## 4. Camadas da Aplicação

A aplicação segue o padrão de camadas com separação rigorosa de responsabilidades. A camada de apresentação (CLI e TUI) comunica-se exclusivamente com a camada de services, que encapsula toda a lógica de negócio. Models gerenciam persistência via SQLModel, e utils fornecem funções transversais de validação e formatação. Nenhuma camada acessa diretamente camadas não adjacentes.

### 4.1. CLI Commands Layer

**Localização:** `src/timeblock/commands/`

**Responsabilidade:** Interface com usuário, parsing de argumentos.

**Estrutura:**

```
commands/
├── habit.py       # Comandos de hábitos
├── task.py        # Comandos de tarefas
├── routine.py     # Comandos de rotinas
├── timer.py       # Comandos de timer
├── report.py      # Relatórios
└── ...
```

**Princípios:**

- Commands são thin wrappers
- Validação básica de input
- Delegam para Services
- Formatam output para usuário

**Exemplo:**

```python
@app.command()
def create(
    title: str = typer.Argument(...),
    start: str = typer.Option(..., "--start"),
):
    """Cria novo hábito."""
    # 1. Valida input básico
    if not title:
        console.print("[ERROR] Titulo obrigatório")
        raise typer.Exit(1)

    # 2. Delega para service
    habit = HabitService.create_habit(
        title=title,
        scheduled_start=parse_time(start)
    )

    # 3. Formata output
    console.print(f"[OK] Hábito criado: {habit.title}")
```

### 4.2. Services Layer

**Localização:** `src/timeblock/services/`

**Responsabilidade:** Lógica de negócio, orquestração.

**Estrutura:**

```
services/
├── habit_service.py             # CRUD hábitos
├── habit_instance_service.py    # Gestão de instancias
├── event_reordering_service.py  # Detecção de conflitos
├── task_service.py              # Gestão de tarefas
├── routine_service.py           # Gestão de rotinas
├── timer_service.py             # Timer tracking
└── ...
```

**Princípios:**

- Stateless (sem estado interno)
- Métodos estáticos ou de classe
- Transações DB isoladas
- Business rules centralizadas

**Exemplo:**

```python
class HabitInstanceService:
    """Service para gestão de instancias de hábitos."""

    @staticmethod
    def generate_instances(
        habit_id: int,
        start_date: date,
        end_date: date
    ) -> list[HabitInstance]:
        """Gera instancias baseadas em recorrência.

        Args:
            habit_id: ID do hábito template
            start_date: Data inicial
            end_date: Data final

        Returns:
            Lista de instancias criadas
        """
        with get_session() as session:
            habit = session.get(Habit, habit_id)
            instances = []

            for day in date_range(start_date, end_date):
                if matches_recurrence(day, habit.recurrence):
                    instance = HabitInstance(
                        habit_id=habit_id,
                        date=day,
                        scheduled_start=habit.scheduled_start,
                        scheduled_end=habit.scheduled_end
                    )
                    session.add(instance)
                    instances.append(instance)

            session.commit()
            return instances
```

**Por que Stateless:**

- Testabilidade (sem setup/teardown complexo)
- Concorrência (sem race conditions)
- Simplicidade (fácil entender fluxo)

#### 4.2.1. Service API Contract

Todo service implementa métodos CRUD seguindo padrões consistentes.

**Pattern: get_by_id**

```python
def get_{entity}(
    self,
    entity_id: int,
    session: Session | None = None
) -> Entity | None:
    """Recupera entidade por ID.

    Returns:
        Entity se encontrada, None caso contrário.
    """
```

**Pattern: list**

```python
def list_{entities}(
    self,
    filters: dict | None = None,
    session: Session | None = None
) -> list[Entity]:
    """Lista entidades com filtros opcionais.

    Returns:
        Lista de entidades (vazia se nenhuma corresponder).
    """
```

**TimerService**

```python
class TimerService:
    # CRUD
    def get_timelog(self, timelog_id: int, session: Session | None = None) -> TimeLog | None
    def get_active_timer(self, session: Session | None = None) -> TimeLog | None
    def list_timelogs(self, filters: dict | None = None, session: Session | None = None) -> list[TimeLog]

    # Operations
    def start_timer(self, habit_instance_id: int | None = None, task_id: int | None = None, session: Session | None = None) -> tuple[TimeLog, list[Conflict] | None]
    def stop_timer(self, timelog_id: int, session: Session | None = None) -> TimeLog
    def pause_timer(self, timelog_id: int, session: Session | None = None) -> TimeLog
    def resume_timer(self, timelog_id: int, session: Session | None = None) -> TimeLog
    def cancel_timer(self, timelog_id: int, session: Session | None = None) -> None
```

**HabitInstanceService**

```python
class HabitInstanceService:
    # CRUD
    def get_instance(self, instance_id: int, session: Session | None = None) -> HabitInstance | None
    def list_instances(self, habit_id: int | None = None, date_start: date | None = None, date_end: date | None = None, session: Session | None = None) -> list[HabitInstance]

    # Operations
    def generate_instances(self, habit_id: int, start_date: date, end_date: date, session: Session | None = None) -> list[HabitInstance]
    def adjust_instance_time(self, instance_id: int, new_start: time | None = None, new_end: time | None = None, session: Session | None = None) -> tuple[HabitInstance, list[Conflict] | None]
    def skip_habit_instance(self, instance_id: int, reason: SkipReason, note: str | None = None, session: Session | None = None) -> HabitInstance
    def mark_completed(self, instance_id: int, session: Session | None = None) -> HabitInstance
```

**Regras de Retorno**

| Tipo       | Comportamento                                                    |
| ---------- | ---------------------------------------------------------------- |
| get\_\*    | Retorna `None` para ID inexistente, nunca lança exception        |
| list\_\*   | Retorna `[]` se nenhum resultado, nunca retorna `None`           |
| operations | Lança `ValueError` para inputs inválidos ou estado inconsistente |

### 4.3. Models Layer

**Localização:** `src/timeblock/models/`

**Responsabilidade:** Estrutura de dados, relacionamentos.

**Estrutura:**

```
models/
├── __init__.py           # Exports
├── enums.py              # Status, Recurrence, etc
├── routine.py            # Modelo Routine
├── habit.py              # Modelo Habit
├── habit_instance.py     # Modelo HabitInstance
├── task.py               # Modelo Task
├── tag.py                # Modelo Tag
├── time_log.py           # Modelo TimeLog
└── event.py              # Union type Event
```

**Princípios:**

- SQLModel (Pydantic + SQLAlchemy)
- Type hints completos
- Validação automática
- Relationships explícitos

**Exemplo:**

```python
class HabitInstance(SQLModel, table=True):
    """Instancia de habito em data específica."""

    __tablename__ = "habit_instances"

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habits.id")
    date: date = Field(index=True)
    scheduled_start: time
    scheduled_end: time
    status: Status = Field(default=Status.PENDING)
    done_substatus: DoneSubstatus | None = None
    not_done_substatus: NotDoneSubstatus | None = None

    # Relationships
    habit: "Habit" = Relationship(back_populates="instances")

    @property
    def is_overdue(self) -> bool:
        """Verifica se instância está atrasada."""
        if self.status != Status.PENDING:
            return False
        now = datetime.now()
        scheduled = datetime.combine(self.date, self.scheduled_start)
        return now > scheduled
```

### 4.4. Database Layer

**Localização:** `src/timeblock/database/`

**Responsabilidade:** Gerenciamento de conexões, configuração e migrations.

**Estrutura:**

```
database/
├── __init__.py     # Exports (get_engine_context)
├── engine.py       # Engine management e configuração
└── migrations/     # Schema migrations
```

#### 4.4.1. Configuração via Environment Variable

O path do banco de dados é configurado via environment variable `TIMEBLOCK_DB_PATH`, seguindo princípios do 12-Factor App. Isso permite:

- Configuração diferente por ambiente (dev, test, prod)
- Isolamento de testes sem monkeypatch de módulos
- Flexibilidade em CI/CD pipelines

**Hierarquia de resolução:**

```
1. TIMEBLOCK_DB_PATH (environment variable) - se definida
2. data/timeblock.db (default relativo ao código)
```

**Implementação (Single Source of Truth):**

```python
# src/timeblock/database/engine.py

import os
from pathlib import Path
from contextlib import contextmanager
from sqlalchemy import event
from sqlmodel import SQLModel, create_engine

def get_db_path() -> str:
    """
    Retorna caminho do banco de dados.

    Ordem de precedência:
    1. Environment variable TIMEBLOCK_DB_PATH
    2. Default: data/timeblock.db

    Returns:
        Caminho absoluto do arquivo SQLite

    Referências:
        - ADR-026: Test Database Isolation Strategy
        - 12-Factor App: Config via environment
    """
    db_path = os.getenv("TIMEBLOCK_DB_PATH")
    if db_path is None:
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        db_path = str(data_dir / "timeblock.db")
    return db_path


def get_engine():
    """
    Retorna engine SQLite com foreign keys habilitadas.

    Configurações:
        - Foreign keys ON (integridade referencial)
        - Echo OFF (sem logging SQL em produção)
    """
    db_path = get_db_path()
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Habilita foreign keys no SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


@contextmanager
def get_engine_context():
    """
    Context manager para engine SQLite com cleanup automático.

    Garante:
        - Conexão única por operação
        - Dispose automático do engine
        - Thread-safety via SQLite config

    Uso:
        with get_engine_context() as engine:
            with Session(engine) as session:
                # operações de banco
    """
    engine = get_engine()
    try:
        yield engine
    finally:
        engine.dispose()
```

#### 4.4.2. Uso em Testes

A estratégia de isolamento de banco em testes é documentada em ADR-026. Resumo:

**Testes Unitários (Service Layer):**

```python
# Fixture injeta session in-memory diretamente
@pytest.fixture
def session(test_engine: Engine) -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session
        session.rollback()

# Service recebe session via DI (ADR-007)
def test_create_task(session: Session):
    task = TaskService.create_task("Test", datetime.now(), session=session)
    assert task.id is not None
```

**Testes de Integração CLI:**

```python
# Fixture configura env var para banco temporário
@pytest.fixture
def isolated_db(tmp_path: Path, monkeypatch) -> Path:
    db_path = tmp_path / "test_cli.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))

    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    engine.dispose()

    return db_path

# CLI usa banco temporário automaticamente
def test_task_create_cli(cli_runner: CliRunner, isolated_db: Path):
    result = cli_runner.invoke(app, ["task", "create", "-t", "Test", ...])
    assert result.exit_code == 0
```

#### 4.4.3. Princípios de Design

1. **SSOT (Single Source of Truth):** Toda lógica de path em `get_db_path()`
2. **12-Factor App:** Configuração via environment, não hardcoded
3. **Zero Monkeypatch de Módulos:** Testes CLI usam env var, não patches
4. **Dependency Injection:** Services recebem session como parâmetro (ADR-007)

**Referências:**

- ADR-007: Service Layer Pattern
- ADR-026: Test Database Isolation Strategy

### 4.5. Utils Layer

**Localização:** `src/timeblock/utils/`

**Responsabilidade:** Funcionalidades transversais.

**Estrutura:**

```
utils/
├── logger.py               # Logging estruturado
├── formatters.py           # Output formatters
├── date_helpers.py         # Date utilities
├── validators.py           # Input validation
├── queries.py              # Query helpers
└── event_date_filters.py   # Filtros de eventos
```

**Princípios:**

- Pure functions quando possível
- Sem side effects
- Altamente testáveis
- Reutilizáveis

---

## 5. Modelos de Dados

Os modelos de dados representam as entidades do domínio e seus relacionamentos usando SQLModel, que combina definições Pydantic (validação) com mapeamento SQLAlchemy (persistência) em classes únicas. O diagrama ER e as definições de entidade refletem o modelo conceitual descrito nas Business Rules, mantendo rastreabilidade direta entre especificação e implementação.

### 5.1. Diagrama ER

```
┌─────────────┐
│   Routine   │
│─────────────│
│ id          │
│ name        │
│ is_active   │
└──────┬──────┘
       │ 1:N
       v
┌─────────────┐      1:N     ┌──────────────────┐
│    Habit    │─────────────>│  HabitInstance   │
│─────────────│              │──────────────────│
│ id          │              │ id               │
│ routine_id  │              │ habit_id         │
│ title       │              │ date             │
│ start/end   │              │ start/end        │
│ recurrence  │              │ status           │
└─────────────┘              │ substatus        │
                             └──────────────────┘

┌─────────────┐
│    Task     │
│─────────────│
│ id          │
│ title       │
│ datetime    │
│ completed   │
└─────────────┘

┌─────────────┐
│     Tag     │
│─────────────│
│ id          │
│ name        │
│ color       │
└─────────────┘

┌─────────────┐
│   TimeLog   │
│─────────────│
│ id          │
│ event_id    │
│ task_id     │
│ instance_id │
│ start_time  │
│ end_time    │
│ duration    │
└─────────────┘
```

### 5.2. Entidades Core

**Routine (Agrupamento):**

```python
# models/routine.py
class Routine(SQLModel, table=True):
    __tablename__ = "routines"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    is_active: bool = Field(default=False)

    habits: list["Habit"] = Relationship(back_populates="routine")
```

**Habit (Template):**

```python
# models/habit.py
class Habit(SQLModel, table=True):
    __tablename__ = "habits"

    id: int | None = Field(default=None, primary_key=True)
    routine_id: int = Field(foreign_key="routines.id", ondelete="RESTRICT")
    title: str = Field(max_length=200)
    scheduled_start: time
    scheduled_end: time
    recurrence: Recurrence  # Enum definido em habit.py
    color: str | None = Field(default=None, max_length=7)
    tag_id: int | None = Field(default=None, foreign_key="tags.id")

    routine: Routine | None = Relationship(back_populates="habits")
    instances: list[HabitInstance] = Relationship(back_populates="habit", cascade_delete=True)
    tag: Tag | None = Relationship(back_populates="habits")
```

**HabitInstance (Ocorrência):**

```python
# models/habit_instance.py
class HabitInstance(SQLModel, table=True):
    __tablename__ = "habitinstance"

    id: int | None = Field(default=None, primary_key=True)
    habit_id: int = Field(foreign_key="habits.id")
    date: date = Field(index=True)
    scheduled_start: time
    scheduled_end: time
    status: Status = Field(default=Status.PENDING)
    done_substatus: DoneSubstatus | None = Field(default=None)
    not_done_substatus: NotDoneSubstatus | None = Field(default=None)
    skip_reason: SkipReason | None = Field(default=None)
    skip_note: str | None = Field(default=None)
    completion_percentage: int | None = Field(default=None)

    habit: Habit | None = Relationship(back_populates="instances")
```

**Task (Evento Único):**

```python
# models/task.py
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    scheduled_datetime: datetime
    completed_datetime: datetime | None = None
    description: str | None = None
    color: str | None = None
    tag_id: int | None = Field(default=None, foreign_key="tags.id")
```

**Event (Evento Genérico):**

```python
# models/event.py
class Event(SQLModel, table=True):
    __tablename__ = "event"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    description: str | None = Field(default=None, max_length=1000)
    color: str | None = Field(default=None, max_length=7)
    status: EventStatus = Field(default=EventStatus.PLANNED)
    scheduled_start: datetime = Field(index=True)
    scheduled_end: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

**Tag (Categorização):**

```python
# models/tag.py
class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True)
    color: str | None = Field(default=None, max_length=7)

    habits: list["Habit"] = Relationship(back_populates="tag")
```

**TimeLog (Rastreamento de Tempo):**

```python
# models/time_log.py
class TimeLog(SQLModel, table=True):
    __tablename__ = "time_log"

    id: int | None = Field(default=None, primary_key=True)

    # Foreign keys (apenas um preenchido por registro)
    event_id: int | None = Field(foreign_key="event.id", default=None, index=True)
    task_id: int | None = Field(foreign_key="tasks.id", default=None, index=True)
    habit_instance_id: int | None = Field(foreign_key="habitinstance.id", default=None, index=True)

    # Estado do timer (BR-TIMER-002)
    status: TimerStatus | None = Field(default=TimerStatus.RUNNING, index=True)
    pause_start: datetime | None = Field(default=None)

    # Timestamps
    start_time: datetime
    end_time: datetime | None = None

    # Durações
    duration_seconds: int | None = None
    paused_duration: int | None = Field(default=0)

    # Anotações
    notes: str | None = Field(default=None, max_length=500)
    cancel_reason: str | None = Field(default=None, max_length=500)
```

**PauseLog (Intervalos de Pausa):**

```python
# models/event.py
class PauseLog(SQLModel, table=True):
    __tablename__ = "pauselog"

    id: int | None = Field(default=None, primary_key=True)
    timelog_id: int = Field(foreign_key="time_log.id", index=True)
    pause_start: datetime
    pause_end: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

**ChangeLog (Auditoria):**

```python
# models/event.py
class ChangeLog(SQLModel, table=True):
    __tablename__ = "changelog"

    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", index=True)
    change_type: ChangeType
    field_name: str | None = Field(default=None, max_length=50)
    old_value: str | None = Field(default=None, max_length=500)
    new_value: str | None = Field(default=None, max_length=500)
    changed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
```

### 5.3. Enums

**Status e Substatus (models/enums.py):**

```python
class Status(str, Enum):
    """Status principal de HabitInstance."""
    PENDING = "pending"
    DONE = "done"
    NOT_DONE = "not_done"

class DoneSubstatus(str, Enum):
    """Substatus para eventos DONE."""
    FULL = "full"           # 90-110%
    PARTIAL = "partial"     # <90%
    OVERDONE = "overdone"   # 110-150%
    EXCESSIVE = "excessive" # >150%

class NotDoneSubstatus(str, Enum):
    """Substatus para eventos NOT_DONE."""
    SKIPPED_JUSTIFIED = "skipped_justified"
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"
    IGNORED = "ignored"

class SkipReason(str, Enum):
    """Categorias de justificativa para skip."""
    HEALTH = "saude"
    WORK = "trabalho"
    FAMILY = "familia"
    TRAVEL = "viagem"
    WEATHER = "clima"
    LACK_RESOURCES = "falta_recursos"
    EMERGENCY = "emergencia"
    OTHER = "outro"

class TimerStatus(str, Enum):
    """Status do timer (BR-TIMER-002)."""
    RUNNING = "running"
    PAUSED = "paused"
    DONE = "done"
    CANCELLED = "cancelled"
```

**Recurrence (models/habit.py):**

```python
class Recurrence(Enum):
    """Padrões de recorrência para Habit."""
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    WEEKDAYS = "WEEKDAYS"
    WEEKENDS = "WEEKENDS"
    EVERYDAY = "EVERYDAY"
```

**EventStatus e ChangeType (models/event.py):**

```python
class EventStatus(str, Enum):
    """Status do ciclo de vida de Event."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class ChangeType(str, Enum):
    """Tipos de alteração para auditoria."""
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    RESCHEDULED = "rescheduled"
    DELETED = "deleted"
```

---

## 6. Fluxos Principais

Os fluxos principais documentam as interações mais críticas do sistema: criação de hábitos com geração de instâncias, detecção de conflitos entre eventos, e operação completa do timer. Cada fluxo atravessa todas as camadas da aplicação e é validado por testes de integração e E2E.

### 6.1. Criação e Geração de Instâncias

```
Usuário CLI
    │
    │ timeblock habit create "Academia" --start 07:00 --generate 3
    v
┌──────────────────┐
│  habit.py (CLI)  │  1. Parse argumentos
└────────┬─────────┘  2. Valida input
         │
         v
┌──────────────────────┐
│    HabitService      │  3. Cria Habit
└────────┬─────────────┘  4. Persiste
         │
         v
┌──────────────────────────┐
│ HabitInstanceService     │  5. Gera instancias
└────────┬─────────────────┘  6. Para próximos 3 meses
         │
         v
┌──────────────────────┐
│     Database         │  7. Persiste instancias
└──────────────────────┘
```

### 6.2. Detecção de Conflitos

```
Usuário ajusta horário
    │
    │ timeblock habit edit <id> --start 09:00
    v
┌────────────────────────────┐
│ HabitInstanceService       │  1. Atualiza horário
└──────────┬─────────────────┘
           │
           v
┌────────────────────────────┐
│ EventReorderingService     │  2. Detecta conflitos
└──────────┬─────────────────┘  3. Lista sobreposições
           │
           v
      Conflitos?
       /      \
    Sim       Não
     │         │
     v         └──> [OK] Atualizado
┌──────────────────────┐
│ Apresenta conflitos  │  4. Mostra ao usuário
└──────────┬───────────┘  5. Pede confirmação
           │
           v
    Usuário confirma?
       /      \
    Sim       Não
     │         │
     v         └──> Cancelado
   Salva
```

### 6.3. Timer Workflow

```
┌──────────┐     start     ┌─────────┐
│ NO TIMER │──────────────>│ RUNNING │
└──────────┘               └────┬────┘
     ^                          │
     │                     ┌────┴────┐
     │                     │         │
     │                   pause     stop
     │                     │         │
     │                     v         v
     │               ┌─────────┐  ┌──────┐
     │               │ PAUSED  │  │ DONE │
     │               └────┬────┘  └──────┘
     │                    │
     │                 resume
     │                    │
     │                    v
     │               ┌─────────┐
     └───────────────│ RUNNING │
          reset      └─────────┘
```

---

## 7. Decisões Arquiteturais

As decisões arquiteturais são documentadas como ADRs (Architecture Decision Records) em `docs/decisions/`. Esta seção apresenta um resumo categorizado; os detalhes completos estão nos arquivos individuais.

**Índice completo:** [docs/decisions/README.md](../decisions/README.md) (27 ADRs)

### 7.1. ADRs Fundacionais

| ADR                                                    | Título              | Decisão                              |
| ------------------------------------------------------ | ------------------- | ------------------------------------ |
| [ADR-001](../decisions/ADR-001-sqlmodel-orm.md)        | SQLModel ORM        | SQLModel ao invés de SQLAlchemy puro |
| [ADR-002](../decisions/ADR-002-typer-cli.md)           | Typer CLI           | Typer ao invés de Click puro         |
| [ADR-005](../decisions/ADR-005-resource-first-cli.md)  | Resource-First CLI  | Padrão `resource action` na CLI      |
| [ADR-006](../decisions/ADR-006-textual-tui.md)         | Textual TUI         | Textual para interface TUI futura    |
| [ADR-031](../decisions/ADR-031-tui-implementation.md)  | TUI Implementation  | Detalhes de implementação TUI v1.7.0 |
| [ADR-011](../decisions/ADR-011-conflict-philosophy.md) | Conflict Philosophy | Sistema informa, usuário decide      |

### 7.2. ADRs de Arquitetura e Dados

| ADR                                                              | Título               | Decisão                          |
| ---------------------------------------------------------------- | -------------------- | -------------------------------- |
| [ADR-003](../decisions/ADR-003-event-reordering.md)              | Event Reordering     | Algoritmo de detecção e proposta |
| [ADR-004](../decisions/ADR-004-habit-vs-instance.md)             | Habit vs Instance    | Separação template/ocorrência    |
| [ADR-007](../decisions/ADR-007-service-layer.md)                 | Service Layer        | Stateless services com DI        |
| [ADR-008](../decisions/ADR-008-tuple-returns.md)                 | Tuple Returns        | Retorno (entity, conflicts)      |
| [ADR-010](../decisions/ADR-010-recurrence-model.md)              | Recurrence Model     | Enum simples para recorrência    |
| [ADR-015](../decisions/ADR-015-habitinstance-naming.md)          | HabitInstance Naming | Nomenclatura padronizada         |
| [ADR-021](../decisions/ADR-021-status-substatus-refactoring.md)  | Status/Substatus     | Refatoração de estados           |
| [ADR-022](../decisions/ADR-022-pause-tracking-simplification.md) | Pause Tracking       | Simplificação de pausas          |

### 7.3. ADRs de Sincronização (v2.0+)

| ADR                                                     | Título               | Decisão                  |
| ------------------------------------------------------- | -------------------- | ------------------------ |
| [ADR-012](../decisions/ADR-012-sync-strategy.md)        | Sync Strategy        | Queue-based com Kafka    |
| [ADR-013](../decisions/ADR-013-offline-first-schema.md) | Offline-First Schema | Schema para sync offline |
| [ADR-014](../decisions/ADR-014-sync-ux-flow.md)         | Sync UX Flow         | Fluxo de UX para sync    |

### 7.4. ADRs de Infraestrutura

| ADR                                                           | Título                  | Decisão                      |
| ------------------------------------------------------------- | ----------------------- | ---------------------------- |
| [ADR-016](../decisions/ADR-016-alembic-timing.md)             | Alembic Timing          | Quando introduzir migrations |
| [ADR-017](../decisions/ADR-017-environment-strategy.md)       | Environment Strategy    | Estratégia de ambientes      |
| [ADR-023](../decisions/ADR-023-microservices-ecosystem.md)    | Microservices Ecosystem | Arquitetura de microserviços |
| [ADR-024](../decisions/ADR-024-homelab-infrastructure.md)     | Homelab Infrastructure  | Raspberry Pi como servidor   |
| [ADR-032](../decisions/ADR-032-branding-repository-naming.md) | Branding & Repos        | ATOMVS + atomvs-timeblock-\* |

### 7.5. ADRs de Padrões e Qualidade

| ADR                                                            | Título                   | Decisão                       |
| -------------------------------------------------------------- | ------------------------ | ----------------------------- |
| [ADR-009](../decisions/ADR-009-flags-consolidation.md)         | Flags Consolidation      | Consolidação de flags CLI     |
| [ADR-018](../decisions/ADR-018-language-standards.md)          | Language Standards       | Português agora, inglês v2.0+ |
| [ADR-019](../decisions/ADR-019-test-naming-convention.md)      | Test Naming              | Padrão test*br*\*             |
| [ADR-020](../decisions/ADR-020-business-rules-nomenclature.md) | BR Nomenclature          | Formato BR-DOMAIN-XXX         |
| [ADR-025](../decisions/ADR-025-development-methodology.md)     | Engenharia de Requisitos | ISO/IEC/IEEE 29148:2018       |
| [ADR-026](../decisions/ADR-026-test-database-isolation.md)     | Test DB Isolation        | Isolamento via env var        |
| [ADR-027](../decisions/ADR-027-documentation-tooling.md)       | Documentation Tooling    | MkDocs + mkdocstrings         |
| [ADR-028](../decisions/ADR-028-remove-legacy-commands.md)      | Remove Legacy Commands   | Remoção de add/list legados   |
| [ADR-029](../decisions/ADR-029-package-by-feature.md)          | Package by Feature       | Organização por domínio       |
| [ADR-030](../decisions/ADR-030-multiplatform-architecture.md)  | Multiplatform Arch       | BFF, multi-repo, IaC          |

---

## 8. Padrões e Convenções

Esta seção define os padrões de codificação e convenções que mantêm consistência no projeto. Cobre estrutura de diretórios, naming conventions para código e testes, organização de imports, uso de type hints, formato de docstrings e workflow Git. Todos os padrões são verificados automaticamente via ruff, mypy e hooks de pre-commit.

### 8.1. Estrutura de Diretórios

```
````
src/timeblock/
├── commands/          # CLI commands
├── services/          # Business logic
├── models/            # Data models
├── database/          # DB management
└── utils/             # Helpers

tests/
├── unit/              # Testes unitários
├── integration/       # Testes integração
├── bdd/               # Cenários Gherkin
├── e2e/               # Fluxos completos
└── factories/         # Test factories
```

**Arquivos:**

- `snake_case.py` para módulos
- `test_<module>.py` para testes

**Classes:**

- `PascalCase` para classes
- `Test<Feature>` para classes de teste

**Funções/Métodos:**

- `snake_case` para funções
- `test_<behavior>` para métodos de teste

**Constantes:**

- `UPPER_SNAKE_CASE`

### 8.3. Imports

```python
# 1. Standard library
from datetime import date, time, datetime
from pathlib import Path

# 2. Third-party
from sqlmodel import SQLModel, Field, Session

# 3. Local
from timeblock.services import HabitService
from timeblock.models import Habit, HabitInstance
```

### 8.4. Type Hints

```python
def generate_instances(
    habit_id: int,
    start_date: date,
    end_date: date
) -> list[HabitInstance]:
    """Sempre type hints completos."""
    pass
```

### 8.5. Docstrings

```python
def calculate_streak(habit_id: int) -> int:
    """Calcula streak atual do hábito.

    Conta dias consecutivos com status DONE,
    do mais recente para trás.

    Args:
        habit_id: ID do hábito

    Returns:
        Número de dias consecutivos

    Raises:
        ValueError: Se habit_id inválido
    """
    pass
```

### 8.6. Padrões de Teste

**Estrutura:**

````
tests/
├── unit/              # Testes unitários por módulo
├── integration/       # Testes de integração
├── bdd/               # Cenários Gherkin
├── e2e/               # Fluxos completos CLI
└── factories/         # Test factories
```
```

**Naming:**

- Classes: `TestBR<Domain><Number>`
- Métodos: `test_br_<domain>_<number>_<scenario>`

**Padrão BDD:**

```python
def test_br_streak_001_counts_done(self):
    """Streak conta dias consecutivos DONE.

    DADO: Hábito com 5 instancias DONE consecutivas
    QUANDO: Calcular streak
    ENTÃO: Deve retornar 5

    BR: BR-STREAK-001
    """
    # Arrange
    # Act
    # Assert
```

### 8.7. Git Workflow

**Branches:**

- `main` - produção
- `develop` - desenvolvimento
- `feat/*` - features
- `fix/*` - bugfixes
- `refactor/*` - refatorações

**Commits:**

```
type(scope): Descrição em Português

Corpo opcional

Footer opcional
```

**Types:** feat, fix, refactor, test, docs, chore

---

## 9. Evolução Futura

O roadmap técnico organiza a evolução do sistema em releases incrementais, cada uma construindo sobre a anterior. A v1.x consolida a CLI local e introduz a TUI, a v2.0 expande para API REST com observabilidade, a v3.0 evolui para microserviços com event sourcing, e a v4.0 adiciona o cliente Android nativo.

### v1.4.0 - MVP Event Reordering (Atual)

- Event Reordering completo
- E2E tests críticos
- Documentação consolidada
- Release MVP

### v1.5.0 - Infra Foundation

**Objetivo:** Base de infraestrutura para evolução do projeto.

**Entregáveis:**

| Item               | Descrição                   |
| ------------------ | --------------------------- |
| Dockerfile         | Multi-stage build otimizado |
| docker-compose.yml | App + Redis + PostgreSQL    |
| .gitlab-ci.yml     | Pipeline CI/CD completo     |
| Makefile           | Comandos padronizados       |

**Pipeline CI/CD:**

```
┌─────────┐    ┌──────────┐    ┌──────────┐
│  TEST   │───►│  BUILD   │───►│ SECURITY │
│         │    │          │    │          │
│ - unit  │    │ - docker │    │ - bandit │
│ - integ │    │ - push   │    │ - trivy  │
│ - lint  │    │          │    │ - safety │
└─────────┘    └──────────┘    └──────────┘
```

### v2.0.0 - FastAPI REST API

**Objetivo:** Expor funcionalidade via API REST + observabilidade.

**Stack:**

| Componente | Tecnologia      |
| ---------- | --------------- |
| Framework  | FastAPI         |
| Docs       | OpenAPI/Swagger |
| Auth       | JWT             |
| Metrics    | Prometheus      |
| Dashboards | Grafana         |
| Logs       | Loki            |

**Endpoints Planejados:**

```
/health                     # Health check
/api/v1/routines/*          # CRUD rotinas
/api/v1/habits/*            # CRUD hábitos
/api/v1/tasks/*             # CRUD tasks
/api/v1/timer/*             # Controle timer
```

**Observabilidade:**

```
┌─────────────┐     ┌────────────┐     ┌─────────┐
│  FastAPI    │────►│ Prometheus │────►│ Grafana │
│  /metrics   │     │            │     │         │
└─────────────┘     └────────────┘     └─────────┘
```

### v3.0.0 - Microservices Ecosystem

**Objetivo:** Ecossistema de serviços independentes via event streaming.

**Arquitetura Event-Driven:**

```
                    ┌─────────────────┐
                    │   Apache Kafka  │
                    └────────┬────────┘
                             │
       ┌─────────────────────┼─────────────────────┐
       │                     │                     │
       v                     v                     v
┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│  TimeBlock  │       │   MedBlock   │       │ EventBlock   │
│    Core     │       │              │       │              │
│             │       │ Medicamentos │       │ Compromissos │
│ - Hábitos   │       │ - Doses      │       │ - Eventos    │
│ - Rotinas   │       │ - Estoque    │       │ - Bloqueios  │
│ - Timer     │       │ - Lembretes  │       │              │
└─────────────┘       └──────────────┘       └──────────────┘

┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│  ListBlock  │       │   (Futuro)   │       │   (Futuro)   │
│             │       │              │       │              │
│ - Listas    │       │              │       │              │
│ - Compras   │       │              │       │              │
└─────────────┘       └──────────────┘       └──────────────┘
```

**Princípio:** Cada serviço é **100% standalone**. Integrações são **opt-in**.

**Serviços Planejados:**

| Serviço        | Função                       | Eventos Publicados |
| -------------- | ---------------------------- | ------------------ |
| TimeBlock Core | Hábitos, rotinas, timer      | `timeblock.*`      |
| MedBlock       | Medicamentos, doses, estoque | `medblock.*`       |
| EventBlock     | Compromissos únicos          | `eventblock.*`     |
| ListBlock      | Listas de compras            | `listblock.*`      |

**Integrações Opt-in:**

| Evento                     | Consumer (opcional) | Ação               |
| -------------------------- | ------------------- | ------------------ |
| `medblock.dose.scheduled`  | TimeBlock Core      | Cria HabitInstance |
| `eventblock.event.created` | TimeBlock Core      | Bloqueia slot      |
| `listblock.list.created`   | TimeBlock Core      | Gera Task          |

**Stack:**

- **Broker:** Apache Kafka
- **Protocolo:** CloudEvents
- **Serialização:** JSON (v3.0), Avro (v3.1+)

**Decisão:** Ver [ADR-023](../decisions/ADR-023-microservices-ecosystem.md)

### v4.0.0 - Android App

**Objetivo:** Mobile-first experience.

**Stack:**

| Componente  | Tecnologia      |
| ----------- | --------------- |
| Linguagem   | Kotlin          |
| UI          | Jetpack Compose |
| Arquitetura | MVVM            |
| DB Local    | Room            |
| Network     | Retrofit        |
| DI          | Hilt            |

**Integração:**

```
Android App (Kotlin)
    │
    v
REST API (FastAPI v2.0)
    │
    v
Event Bus (Kafka v3.0)
    │
    v
Microservices
```

---

## 10. Deployment Options

### 10.1. Visão Geral

O TimeBlock suporta múltiplas estratégias de deployment, desde desenvolvimento local até servidor dedicado 24/7.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT PROGRESSION                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  v1.x           v2.0-alpha        v2.0-stable          v3.0+        │
│  ─────          ──────────        ───────────          ─────        │
│  CLI Local  =>  Desktop Server => Raspberry Pi     =>  Cloud/Hybrid │
│  SQLite         FastAPI+SQLite    Docker+PostgreSQL    Kafka+K8s    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.2. Opções de Servidor

| Opção               | Disponibilidade | Consumo  | Complexidade |
| ------------------- | --------------- | -------- | ------------ |
| Desktop Linux       | Quando ligado   | ~50-100W | Baixa        |
| Raspberry Pi 4      | 24/7            | ~5W      | Média        |
| VPS Cloud           | 24/7            | N/A      | Média        |
| Hybrid (Pi + Cloud) | 24/7 + Backup   | ~5W      | Alta         |

### 10.3. Raspberry Pi Homelab

**Arquitetura:**

```
┌────────────────────────────────────────────────────────────────┐
│                     RASPBERRY PI HOMELAB                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Raspberry Pi 4                        │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │   │
│  │  │  Docker     │  │  Docker     │  │  Docker     │      │   │
│  │  │  ─────────  │  │  ─────────  │  │  ─────────  │      │   │
│  │  │  FastAPI    │  │  PostgreSQL │  │  Prometheus │      │   │
│  │  │  TimeBlock  │  │             │  │  + Grafana  │      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                 │
│                              v                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Rede Local                           │   │
│  │   Desktop ◄────► Pi Server ◄────► Android/Termux        │   │
│  │   (cliente)      (24/7)           (cliente)             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Stack v2.0-stable:**

```yaml
# docker-compose.yml (simplificado)
services:
  timeblock-api:
    image: timeblock/api:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://timeblock:pass@db/timeblock
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=timeblock
      - POSTGRES_USER=timeblock
      - POSTGRES_PASSWORD=pass

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

### 10.4. Princípios de Sync (ADR-012)

**IMPORTANTE:** Independente da opção de deployment:

- Sync SEMPRE manual via `timeblock connect`
- Sem daemon no cliente
- Usuário decide quando sincronizar
- Raspberry Pi = servidor disponível 24/7, NÃO auto-sync

```bash
# Sem Pi: precisa iniciar servidor antes
$ timeblock server start  # No desktop
$ timeblock connect       # No Android

# Com Pi: servidor já disponível
$ timeblock connect       # Funciona direto (Pi rodando 24/7)
```

## 11. Processo de Desenvolvimento

### 11.1. Visão Geral

O projeto adota técnicas de **Engenharia de Requisitos** (ISO/IEC/IEEE 29148:2018, SWEBOK v4.0) com **Vertical Slicing**, BDD e Strict TDD. O ciclo mapeia para o ciclo clássico da disciplina: especificação, validação, verificação e implementação.

**Ciclo de Engenharia de Requisitos:**

```
Especificação --> Validação (BDD) --> Verificação (TDD) --> Implementação
```

### 11.2. Práticas Adotadas

| Prática           | Origem                  | Aplicação               |
| ----------------- | ----------------------- | ----------------------- |
| Vertical Slicing  | Agile                   | Uma BR completa por vez |
| Especificação     | ISO/IEC/IEEE 29148:2018 | BRs formalizadas        |
| Validação (BDD)   | Dan North (2006)        | pytest-bdd com Gherkin  |
| Verificação (TDD) | Robert Martin (2003)    | 3 Leis rigorosas        |
| Sprints           | Scrum                   | Iterações 1-2 semanas   |
| WIP Limits        | Kanban/Lean             | Max 2 itens In Progress |

### 11.3. Fluxo por Business Rule

```
┌─────────────────────────────────────────────────────────────┐
│                  VERTICAL SLICE (1 BR)                      │
├─────────────────────────────────────────────────────────────┤
│  1. Especificar BR (docs/core/business-rules.md)            │
│  2. Escrever cenário de validação (.feature)                │
│  3. Implementar steps (step_defs/)                          │
│  4. Criar teste de verificação (RED)                        │
│  5. Implementar código (GREEN)                              │
│  6. Refatorar                                               │
│  7. Commit                                                  │
├─────────────────────────────────────────────────────────────┤
│  [OK] BR completa ──> Próxima BR                            │
└─────────────────────────────────────────────────────────────┘
```

### 11.4. As 3 Leis do Strict TDD

1. Não escreva código de produção exceto para passar um teste que falha
2. Não escreva mais de um teste que seja suficiente para falhar
3. Não escreva mais código do que o suficiente para passar o teste

### 11.5. Estrutura de Testes

```
tests/
├── bdd/
│   ├── features/        # .feature (Gherkin)
│   └── step_defs/       # Steps Python
├── unit/                # ~70% (verificação isolada)
├── integration/         # ~20% (Service + DB)
└── e2e/                 # ~5% (CLI/TUI completa)
```

**Status BDD:** 8 testes passando com pytest-bdd.

### 11.6. WIP Limits

| Coluna         | Limite     |
| -------------- | ---------- |
| Backlog        | Sem limite |
| Sprint Backlog | 5-10       |
| In Progress    | 1-2        |
| Code Review    | 2-3        |
| Done           | Sem limite |

### 11.7. Sprints

- **Duração:** 1-2 semanas
- **Planejamento:** Início (selecionar BRs)
- **Daily:** Check-in diário
- **Review:** Fim (validar entregas)
- **Retro:** Fim (identificar melhorias)

**SSOT de Processo:** [development.md](development.md)

Ver também: [ADR-025: Engenharia de Requisitos](../decisions/ADR-025-development-methodology.md)

---

## 12. CI/CD e Branch Protection

### 12.1. Visão Geral

A automação de qualidade opera em três camadas complementares, garantindo que código problemático não entre no repositório nem nas branches protegidas.

```
┌───────────────────────────────────────────────────────────────┐
│                    CAMADAS DE PROTEÇÃO                        │
├───────────────────────────────────────────────────────────────┤
│  1. Pre-commit Hooks (LOCAL)                                  │
│     git commit ──> ruff + mypy + pytest-all                   │
│     Bloqueia: commit local se falhar                          │
│                                                               │
│  2. CI/CD Pipeline (SERVIDOR)                                 │
│     git push ──> GitLab CI / GitHub Actions                   │
│     Marca: commit como passed/failed                          │
│                                                               │
│  3. Branch Protection (SERVIDOR)                              │
│     merge request ──> status checks obrigatórios              │
│     Bloqueia: merge em develop/main se CI falhar              │
└───────────────────────────────────────────────────────────────┘
```

### 12.2. Pre-commit Hooks

Executados localmente em cada `git commit` via `pre-commit` framework.

| Hook        | Ferramenta | Tempo | Bloqueante |
| ----------- | ---------- | ----- | ---------- |
| ruff format | ruff       | 1.2s  | Sim        |
| ruff check  | ruff       | 0.8s  | Sim        |
| mypy        | mypy       | 3.5s  | Não        |
| pytest-all  | pytest     | ~30s  | Sim        |

**Total:** ~35s por commit.

**Referência:** `.pre-commit-config.yaml`

`pytest-all` executa a suite completa (unit + integration + BDD + e2e), garantindo que cada commit é funcional.

### 12.3. GitLab CI/CD Pipeline

Pipeline declarado em `.gitlab-ci.yml`, executado em cada push e merge request.

**Imagem base:** `python:3.13`

**Jobs paralelos no stage `test`:**

| Job              | Comando                    | Bloqueante | Artefatos    |
| ---------------- | -------------------------- | ---------- | ------------ |
| test:unit        | pytest tests/unit/ --cov   | Sim        | coverage.xml |
| test:integration | pytest tests/integration/  | Sim        | -            |
| test:bdd         | pytest tests/bdd/          | Sim        | -            |
| test:e2e         | pytest tests/e2e/          | Sim        | -            |
| test:lint        | ruff check src/timeblock   | Sim        | -            |
| test:typecheck   | mypy (allow_failure: true) | Não        | -            |

**Stages:**

```
test ──> build ──> deploy

test:     6 jobs paralelos (acima)
build:    mkdocs build [develop, main]
deploy:   GitLab Pages [main]
```

### 12.4. GitHub Actions

Pipeline declarado em `.github/workflows/ci.yml`, executado em push e pull requests.

**Matrix strategy para testes:**

| Job       | Matrix                      | Bloqueante |
| --------- | --------------------------- | ---------- |
| lint      | ruff check                  | Sim        |
| typecheck | mypy (continue-on-error)    | Não        |
| test      | unit, integration, bdd, e2e | Sim        |

### 12.5. Branch Protection Rules

Configuradas via CLI (`gh api` e `glab api`) para garantir que merges em branches protegidas exigem CI verde.

**GitHub:**

| Branch  | Status Checks Obrigatórios                                    | Enforce Admins |
| ------- | ------------------------------------------------------------- | -------------- |
| develop | test (unit), test (integration), test (bdd), test (e2e), lint | Sim            |
| main    | test (unit), test (integration), test (bdd), test (e2e), lint | Sim            |

**GitLab:**

| Branch  | Push Access | Merge Access | Pipeline Must Succeed |
| ------- | ----------- | ------------ | --------------------- |
| develop | Maintainers | Maintainers  | Sim                   |
| main    | Maintainers | Maintainers  | Sim                   |

**Configuração `only_allow_merge_if_pipeline_succeeds: true`** ativada a nível de projeto.

### 12.6. Fluxo Completo

```
developer
    │
    ├── git commit
    │   └── pre-commit hooks (ruff, mypy, pytest-all)
    │       ├── [FAIL] ──> commit bloqueado
    │       └── [PASS] ──> commit local criado
    │
    ├── git push origin develop
    │   └── CI/CD pipeline (GitLab CI + GitHub Actions)
    │       ├── [FAIL] ──> commit marcado como failed
    │       └── [PASS] ──> commit marcado como passed
    │
    └── merge request (develop ──> main)
        └── branch protection rules
            ├── [CI FAIL] ──> merge bloqueado
            └── [CI PASS] ──> merge permitido
```

---

## 13. Arquitetura Multi-Plataforma (v2.0+)

A partir da v2.0, o TimeBlock evolui de CLI local para ecossistema multi-plataforma com Terminal (Python), Web (Angular), Mobile (Kotlin) e Desktop (Tauri/Rust). Cada plataforma tem requisitos específicos de UX, performance e stack tecnológica, exigindo backends especializados.

### 13.1. Organização de Repositórios

O projeto adota GitHub Organization com um repositório por serviço, seguindo padrões de microsserviços. Essa estrutura permite ciclos de deploy independentes e evolução paralela de componentes.

```
atomvs-timeblock/               # GitHub Organization
│
├── atomvs-timeblock-contracts       # OpenAPI, Protobuf, AsyncAPI
│
├── # ─── BACKEND CORE ────────────────────────────
├── atomvs-timeblock-api             # Spring Boot (BRs, auth, CRUD)
├── atomvs-timeblock-gateway         # Spring Cloud Gateway
├── atomvs-timeblock-sync            # Go + Kafka
├── atomvs-timeblock-notifications   # Spring Boot (email, push)
│
├── # ─── BFFs ────────────────────────────────────
├── atomvs-timeblock-bff-web         # Spring Boot
├── atomvs-timeblock-bff-terminal    # Go ou Python
│
├── # ─── CLIENTS ─────────────────────────────────
├── atomvs-timeblock-terminal        # Python (CLI + TUI)
├── atomvs-timeblock-web             # Angular + TypeScript
├── atomvs-timeblock-mobile          # Kotlin Full-Stack
├── atomvs-timeblock-desktop         # Tauri (Rust + Svelte/Angular)
│
└── # ─── INFRA ───────────────────────────────────
    └── atomvs-timeblock-infra       # Docker, K8s, Terraform, Ansible
```

### 13.2. Padrão BFF (Backend For Frontend)

O padrão BFF cria backends dedicados por plataforma, otimizando payloads e comportamentos para cada tipo de cliente. Netflix, Uber e Spotify utilizam essa arquitetura.

```
┌────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                │
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│   Web    │  Mobile  │   CLI    │   TUI    │      Desktop       │
└────┬─────┴────┬─────┴────┬─────┴──────┬───┴──────────┬─────────┘
     │          │          └──────┬─────┘              │
     ↓          ↓                 ↓                    ↓
┌──────────┐ ┌────────────┐ ┌──────────────┐     ┌─────────────┐
│ BFF Web  │ │ BFF Mobile │ │ BFF Terminal │     │ BFF Desktop │
│ Spring   │ │   Kotlin   │ │   Go/Python  │     │    Go       │
└────┬─────┘ └────┬───────┘ └─────┬────────┘     └─────┬───────┘
     └────────────┴───────────────┴────────────────────┘
                          │
                          ↓
              ┌─────────────────────────┐
              │      API GATEWAY        │
              │  Spring Cloud Gateway   │
              └───────────┬─────────────┘
                          │
     ┌────────────────────┼────────────────────┐
     ↓                    ↓                    ↓
┌──────────┐         ┌──────────┐        ┌──────────┐
│ API Core │         │   Sync   │        │  Notif   │
│  Spring  │         │   Go     │        │  Spring  │
└──────────┘         └──────────┘        └──────────┘
```

### 13.3. Stacks por Componente

| Componente        | Stack                    | Justificativa                                   |
| ----------------- | ------------------------ | ----------------------------------------------- |
| **API Core**      | Java/Spring Boot         | Regras complexas, ecossistema enterprise maduro |
| **Gateway**       | Spring Cloud Gateway     | Consistência com API, features enterprise       |
| **Sync**          | Go + Kafka               | Performance, concorrência, padrão cloud-native  |
| **Notifications** | Spring Boot              | Compartilha libs com API                        |
| **BFF Web**       | Spring Boot              | Alinha com backend Java                         |
| **BFF Terminal**  | Go ou Python             | Leve, alinha com clients                        |
| **Terminal**      | Python (Typer + Textual) | Projeto atual                                   |
| **Web**           | Angular + TypeScript     | Framework enterprise                            |
| **Mobile**        | Kotlin Full-Stack        | Kotlin Multiplatform (app + backend)            |
| **Desktop**       | Tauri + Rust             | Binário nativo, baixo consumo de recursos       |

### 13.4. Infrastructure as Code

O repositório `timeblock-infra` centraliza configuração de infraestrutura como código, garantindo ambientes reproduzíveis e versionados.

```
timeblock-infra/
├── terraform/                # Provisioning cloud
│   ├── modules/
│   └── environments/
├── ansible/                  # Configuration management
│   ├── playbooks/
│   └── roles/
├── kubernetes/               # Orquestração (v3.0+)
│   ├── base/
│   └── overlays/
├── docker/                   # Compose para dev/homelab
└── scripts/                  # Automação
```

**Progressão IaC:**

| Versão | Ferramenta               | Uso                            |
| ------ | ------------------------ | ------------------------------ |
| v1.5.0 | Docker Compose           | Dev local, CI/CD               |
| v2.0.0 | Docker Compose + Ansible | Raspberry Pi homelab           |
| v3.0.0 | Kubernetes + Helm        | Orquestração de microsserviços |

### 13.5. Contratos Compartilhados

O repositório `atomvs-timeblock-contracts` define interfaces entre serviços usando OpenAPI (REST), Protobuf (gRPC), AsyncAPI (Kafka) e JSON Schema (validação). Essa abordagem contract-first garante compatibilidade antes do deploy.

Ver também: [ADR-030: Arquitetura Multi-Plataforma](../decisions/ADR-030-multiplatform-architecture.md)

## Referências

- **SQLModel:** <https://sqlmodel.tiangolo.com/>
- **Typer:** <https://typer.tiangolo.com/>
- **Rich:** <https://rich.readthedocs.io/>
- **FastAPI:** <https://fastapi.tiangolo.com/>
- **Apache Kafka:** <https://kafka.apache.org/>
- **Business Rules:** `docs/core/business-rules.md`

---

**Última atualização:** 13 de Fevereiro de 2026
