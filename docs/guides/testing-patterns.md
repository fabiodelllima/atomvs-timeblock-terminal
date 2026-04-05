# Padrões de Teste

- **Versão:** 1.0.0
- **Status:** SSOT
- **Alinhado com:** development.md v3.0.0, technical-debt.md v2.9.0

---

## 1. Visão Geral

Este documento é a referência única para convenções de fixtures, naming, anti-patterns e padrões por camada de teste do projeto ATOMVS Time Planner Terminal. Complementa o `development.md` (que define a pirâmide e a metodologia) com os detalhes práticos necessários para escrever testes corretos na primeira tentativa — seja por um desenvolvedor humano ou por um agente autônomo.

---

## 2. Arquitetura de Fixtures

### 2.1 Camadas de conftest

O projeto tem 7 arquivos `conftest.py`, cada um com escopo e responsabilidade distintos:

```plaintext
tests/conftest.py                        # Fixtures globais: test_engine, session, test_db
tests/unit/conftest.py                   # mock_session, sample_date, sample_time_*
tests/unit/test_tui/conftest.py          # _isolate_tui_database (session-scoped, autouse)
tests/unit/utils/conftest.py             # now_time, sample_events (usa test_db — desvio)
tests/integration/conftest.py            # integration_engine, integration_session, test_db
tests/integration/commands/conftest.py   # cli_runner, isolated_db (via env var)
tests/integration/workflows/conftest.py  # e2e_db_path, complete_routine_setup
```

### 2.2 Fixture de banco de dados por camada

#### Unit tests de services

Usam `test_engine` (in-memory) com `mock_engine` via monkeypatch. O padrão canônico:

```python
import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session

from timeblock.models import Habit, Recurrence, Routine
from timeblock.services.habit_instance_service import HabitInstanceService


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch: pytest.MonkeyPatch, test_engine: Engine) -> None:
    """Mock get_engine_context para usar banco de teste."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr(
        "timeblock.services.habit_instance_service.get_engine_context",
        mock_get_engine,
    )
```

O `monkeypatch.setattr` deve apontar para o módulo do service sendo testado. Exemplo: para `TimerService`, o path é `"timeblock.services.timer_service.get_engine_context"`.

Fixtures de entidades usam `session` (de `tests/conftest.py`):

```python
@pytest.fixture
def everyday_habit(session: Session) -> Habit:
    routine = Routine(name="Test Routine")  # campo é `name`, NUNCA `title`
    session.add(routine)
    session.commit()
    session.refresh(routine)

    habit = Habit(
        routine_id=routine.id,
        title="Test Habit",
        scheduled_start=time(8, 0),
        scheduled_end=time(9, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit
```

Instâncias geradas via `generate_instances` **não recebem** `session=` nos unit tests — usam o mock_engine internamente. **Nunca** chamar `session.refresh()` em objetos criados por `generate_instances`, porque pertencem a outra sessão interna:

```python
# CORRETO
@pytest.fixture
def pending_instance(everyday_habit: Habit) -> HabitInstance:
    instances = HabitInstanceService.generate_instances(
        everyday_habit.id, date.today(), date.today()
    )
    return instances[0]

# INCORRETO — causa InvalidRequestError
@pytest.fixture
def pending_instance(everyday_habit: Habit, session: Session) -> HabitInstance:
    instances = HabitInstanceService.generate_instances(
        everyday_habit.id, date.today(), date.today()
    )
    session.refresh(instances[0])  # ERRO: instância não pertence a esta sessão
    return instances[0]
```

#### Integration tests

Usam `integration_engine` (scope="session") + `integration_session` com `join_transaction_mode="conditional_savepoint"`. O alias `test_db` é disponível para compatibilidade:

```python
# Em tests/integration/conftest.py
@pytest.fixture
def test_db(integration_session: Session) -> Session:
    return integration_session
```

Services em integration tests recebem `session=test_db` explicitamente, incluindo `generate_instances`:

```python
instances = HabitInstanceService.generate_instances(
    habit.id, date.today(), date.today(), session=test_db
)
```

#### TUI unit tests

O conftest `tests/unit/test_tui/conftest.py` força `TIMEBLOCK_DB_PATH=":memory:"` como autouse session-scoped. Todos os testes TUI rodam contra banco isolado sem fixture explícita.

#### BDD step definitions

Usam `session` (de `tests/conftest.py`) diretamente. Steps criam entidades inline:

```python
@given('a routine "Rotina Matinal" exists', target_fixture="test_routine")
def criar_rotina(session: Session):
    routine = Routine(name="Rotina Matinal")
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine
```

#### E2E tests

Não usam mock_engine. Criam entidades diretamente via app/TUI. Rotinas e hábitos são criados via interação (keypresses) ou inline no corpo do teste.

---

## 3. Naming Convention

### 3.1 Arquivos

| Camada      | Diretório                     | Padrão de nome                  |
| ----------- | ----------------------------- | ------------------------------- |
| Unit        | `tests/unit/test_services/`   | `test_<service_name>.py`        |
| Unit TUI    | `tests/unit/test_tui/`        | `test_<widget_or_module>.py`    |
| Unit Models | `tests/unit/test_models/`     | `test_<model_name>.py`          |
| Integration | `tests/integration/services/` | `test_<service>_integration.py` |
| BDD Feature | `tests/bdd/features/`         | `<domain>_<action>.feature`     |
| BDD Steps   | `tests/bdd/step_defs/`        | `test_<feature_name>_steps.py`  |
| E2E         | `tests/e2e/`                  | `test_<flow_name>.py`           |

Todos os nomes em **inglês**. Nunca nomes em português.

### 3.2 Classes e métodos

```python
class TestBRHabitinstance002DoneSetsSubstatus:
    """mark_completed seta done_substatus corretamente (BR-HABITINSTANCE-002)."""

    def test_br_habitinstance_002_done_sets_substatus_full(self, ...) -> None:
        """FULL substatus é gravado corretamente."""
```

Formato da classe: `TestBR<Domain><Number><Descrição>`
Formato do método: `test_br_<domain>_<number>_<cenário>`

Cada classe referencia uma BR no docstring. Cada método descreve o cenário testado.

---

## 4. Model Reference para Testes

### 4.1 Routine

Campo obrigatório: `name` (str). **Nunca** `title`.

```python
Routine(name="Test Routine")               # unit/integration
Routine(name="Test Routine", is_active=True)  # quando is_active importa
```

### 4.2 Habit

Campos obrigatórios: `routine_id`, `title`, `scheduled_start`, `scheduled_end`, `recurrence`.

```python
Habit(
    routine_id=routine.id,
    title="Test Habit",
    scheduled_start=time(8, 0),
    scheduled_end=time(9, 0),
    recurrence=Recurrence.EVERYDAY,
)
```

`target_minutes` não existe no model. O target é derivado do intervalo `scheduled_end - scheduled_start`.

### 4.3 Enums — Acesso correto

`SkipReason` tem valores em **português** (`"saude"`, `"trabalho"`, etc.). Acesso seguro:

```python
# CORRETO — acesso por nome do membro
SkipReason["HEALTH"]          # retorna SkipReason.HEALTH
SkipReason[reason.upper()]    # dinâmico

# CORRETO — acesso por valor (português)
SkipReason("saude")           # retorna SkipReason.HEALTH

# INCORRETO — valor em inglês
SkipReason("health")          # ValueError!
```

`DoneSubstatus` tem valores em inglês — acesso por nome ou valor funciona:

```python
DoneSubstatus["FULL"]    # OK
DoneSubstatus("full")    # OK
```

### 4.4 TimeLog

Criação manual para testes (sem usar TimerService):

```python
from datetime import datetime
from timeblock.models.time_log import TimeLog
from timeblock.models.enums import TimerStatus

timelog = TimeLog(
    habit_instance_id=instance.id,
    status=TimerStatus.DONE,
    start_time=datetime.combine(instance.date, time(8, 0)),
    end_time=datetime.combine(instance.date, time(8, 57)),
    duration_seconds=3420,
)
session.add(timelog)
session.commit()
```

---

## 5. Anti-patterns Documentados

### 5.1 session.refresh em instância de outra sessão

**Sintoma:** `InvalidRequestError: Instance is not persistent within this Session`

**Causa:** `generate_instances` (sem `session=`) usa o mock_engine internamente e cria instâncias numa sessão própria. Chamar `session.refresh(instance)` na sessão da fixture falha porque o objeto pertence à sessão interna.

**Correção:** Não chamar `session.refresh()` em objetos retornados por `generate_instances` sem `session=`. O objeto já está populado — use-o diretamente.

### 5.2 Routine(title=...) em vez de Routine(name=...)

**Sintoma:** `IntegrityError: NOT NULL constraint failed: routines.name`

**Causa:** O model `Routine` usa `name` como campo (mapped para coluna `name` na tabela `routines`). `title` não existe — é ignorado silenciosamente pelo SQLModel, deixando `name` como NULL.

**Correção:** Sempre usar `Routine(name="...")`.

### 5.3 SkipReason("health") em vez de SkipReason["HEALTH"]

**Sintoma:** `ValueError: 'health' is not a valid SkipReason`

**Causa:** Os valores do enum são em português (`"saude"`, não `"health"`). Acesso por valor com string em inglês falha.

**Correção:** Usar acesso por nome: `SkipReason["HEALTH"]` ou `SkipReason[reason.upper()]`.

### 5.4 test_db em unit tests

**Sintoma:** Funciona mas viola a convenção.

**Causa:** `test_db` é alias de `session` no conftest global, mas semanticamente pertence à camada de integration (onde é alias de `integration_session`).

**Status:** Desvio existente em `tests/unit/utils/conftest.py` (usa `test_db` em vez de `session`). Aceito como legacy — novos unit tests devem usar `session`.

---

## 6. Checklist para Novos Testes

Antes de escrever um teste, verificar:

1. Camada correta (unit/integration/bdd/e2e)?
2. Fixture de banco correta (`session` para unit, `test_db` para integration)?
3. `mock_engine` com monkeypatch presente (se unit test de service)?
4. `Routine(name="...")` (não `title`)?
5. `generate_instances` sem `session=` em unit tests?
6. Enums acessados por nome (`SkipReason["HEALTH"]`)?
7. Classe e método seguem naming convention (`TestBR...`, `test_br_...`)?
8. Docstring referencia BR?
9. `ruff check` + `mypy` + `pytest` passam antes de commit?

---

## 7. Desvios Conhecidos

| Arquivo                        | Desvio                            | Status        |
| ------------------------------ | --------------------------------- | ------------- |
| `tests/unit/utils/conftest.py` | Usa `test_db` em vez de `session` | Aceito/legacy |

Nenhum desvio de `Routine(title=...)` encontrado na varredura de 16/03/2026.

---

**Referências:**

- BECK, K. **Test-Driven Development: By Example.** Boston: Addison-Wesley, 2003.
- SQLAlchemy 2.0 Documentation: "Joining a Session into an External Transaction."
- pytest-bdd 8.x Documentation.
- ADR-026: Test Database Isolation Strategy.
- ADR-033: Fixture scope="session" com rollback transacional.
- BR-TEST-001: Isolamento de testes.

---

**Data:** 16 de Março de 2026
