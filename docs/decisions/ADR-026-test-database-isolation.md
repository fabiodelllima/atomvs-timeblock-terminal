# ADR-026: Test Database Isolation Strategy

- **Status:** Accepted
- **Data:** 19/JAN/2026
- **Relacionado:** ADR-007 (Service Layer), ADR-019 (Test Naming Convention)

---

## Contexto

TimeBlock Organizer possui três níveis de teste (Unit, Integration, E2E) que requerem isolamento de banco de dados. A estratégia atual apresenta inconsistências e fragilidades que dificultam manutenção e causam falhas intermitentes.

### Problema Identificado

**Situação encontrada (2025-01-19):**

```python
# tests/integration/commands/test_list.py (ANTES - Problemático)
@pytest.fixture
def isolated_db(monkeypatch):
    engine = create_engine("sqlite:///:memory:", poolclass=StaticPool)

    @contextmanager
    def mock_engine_context():
        yield engine

    # PROBLEMA: Precisa patchar CADA módulo que importa get_engine_context
    monkeypatch.setattr("timeblock.database.get_engine_context", mock_engine_context)
    monkeypatch.setattr("timeblock.commands.list.get_engine_context", mock_engine_context)
    monkeypatch.setattr("timeblock.services.task_service.get_engine_context", mock_engine_context)
    # ... potencialmente dezenas de módulos
```

**Problemas identificados:**

1. **Fragilidade:** Cada novo import de `get_engine_context` requer novo monkeypatch
2. **Manutenção pesada:** Refatorações quebram testes silenciosamente
3. **Violação DRY:** Lista de patches cresce indefinidamente
4. **Acoplamento forte:** Testes dependem da estrutura interna de imports
5. **Duplicação de lógica:** `config.py` e `engine.py` ambos leem `TIMEBLOCK_DB_PATH`

### Duplicação Atual

```
config.py (linha 7-13)              engine.py (linha 12-19)
─────────────────────               ──────────────────────
_db_path_env = os.getenv(...)       def get_db_path():
if _db_path_env:                        db_path = os.getenv(...)
    DATABASE_PATH = Path(...)           ...
                                        return db_path

[!] Lido no IMPORT                  [OK] Lido na CHAMADA
    (valor congelado)                   (valor dinâmico)
```

---

## Decisão

Adotar **estratégia híbrida** de isolamento de banco de dados:

1. **Testes Unitários de Service:** Session injetada diretamente (ADR-007)
2. **Testes de Integração CLI:** Environment variable `TIMEBLOCK_DB_PATH`
3. **Single Source of Truth:** Toda lógica de path em `engine.get_db_path()`

### Princípios

1. **12-Factor App:** Configuração via environment variables
2. **SSOT:** Um único ponto de leitura do path do banco
3. **Zero Monkeypatch de Módulos:** Não patchar funções internas entre módulos
4. **Dependency Injection:** Services recebem session como parâmetro

---

## Implementação

### 1. Fixture Padrão para Testes CLI

```python
# tests/integration/commands/conftest.py

@pytest.fixture
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Banco de dados isolado para testes de integração CLI.

    Configura TIMEBLOCK_DB_PATH via env var, garantindo que todo o sistema
    use o banco temporário sem necessidade de monkeypatch de módulos.

    Args:
        tmp_path: Diretório temporário do pytest (cleanup automático)
        monkeypatch: Fixture para modificar environment

    Returns:
        Path do banco de dados de teste

    Referências:
        - ADR-026: Test Database Isolation Strategy
        - 12-Factor App: Config via environment

    Exemplo:
        def test_task_creation(cli_runner: CliRunner, isolated_db: Path):
            result = cli_runner.invoke(app, ["task", "create", ...])
            assert result.exit_code == 0
    """
    db_path = tmp_path / "test_cli.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))

    # Criar tabelas no banco temporário
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    engine.dispose()

    return db_path
```

### 2. Fixture para Testes Unitários de Service

```python
# tests/conftest.py

@pytest.fixture
def test_engine() -> Generator[Engine, None, None]:
    """
    Engine SQLite em memória para testes unitários isolados.

    Usa banco in-memory para máxima velocidade. Cada teste
    recebe engine limpo com tabelas criadas.

    Referências:
        - ADR-007: Service Layer com session injection
        - ADR-026: Test Database Isolation Strategy
    """
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn: Any, _: Any) -> None:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(test_engine: Engine) -> Generator[Session, None, None]:
    """
    Sessão de banco de dados para testes unitários.

    Fornece session injetável em services conforme ADR-007.
    Rollback automático ao final de cada teste.
    """
    with Session(test_engine) as session:
        yield session
        session.rollback()
```

### 3. Uso em Testes

**Teste Unitário (Service com DI):**

```python
# tests/unit/test_services/test_task_service.py

class TestBRTask001Creation:
    """Testes para BR-TASK-001: Criação de Tasks."""

    def test_br_task_001_creates_successfully(self, session: Session) -> None:
        """
        BR-TASK-001: Sistema cria task com dados válidos.

        DADO: Session válida disponível
        QUANDO: Criar task com título e datetime
        ENTÃO: Task persistida com ID gerado
        """
        # ARRANGE
        title = "Reunião Standup"
        scheduled = datetime.now() + timedelta(hours=1)

        # ACT - Session injetada diretamente
        task = TaskService.create_task(
            title=title,
            scheduled_datetime=scheduled,
            session=session,  # DI conforme ADR-007
        )

        # ASSERT
        assert task.id is not None
        assert task.title == title
```

**Teste de Integração CLI (Env Var):**

```python
# tests/integration/commands/test_task_commands.py

class TestBRTaskCmdDelete:
    """Testes de integração para comandos de deleção de task."""

    def test_br_task_cmd_delete_001_with_force(
        self, cli_runner: CliRunner, isolated_db: Path
    ) -> None:
        """
        BR-TASK-CMD-DELETE-001: Sistema deleta task com --force.

        DADO: Task existente no banco isolado
        QUANDO: Usuário executa delete com --force
        ENTÃO: Task removida sem confirmação
        """
        # ARRANGE - Criar task via CLI (usa banco de isolated_db)
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = cli_runner.invoke(
            app, ["task", "create", "-t", "Delete Me", "-D", dt]
        )
        task_id = extract_id_from_output(create_result.stdout)

        # ACT
        result = cli_runner.invoke(app, ["task", "delete", task_id, "--force"])

        # ASSERT
        assert result.exit_code == 0
        assert "Tarefa deletada" in result.stdout
```

---

## Diagrama de Fluxo

```
┌───────────────────────────────────────────────────────────────────────────┐
│                     ESTRATÉGIA DE ISOLAMENTO DE BANCO                     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                    TESTES UNITÁRIOS (Service Layer)                │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │                                                                    │   │
│  │  Fixture: session (in-memory)                                      │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  engine = create_engine("sqlite:///:memory:")              │    │   │
│  │  │  SQLModel.metadata.create_all(engine)                      │    │   │
│  │  │  with Session(engine) as session:                          │    │   │
│  │  │      yield session  ─────────────────────────┐             │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │                                                 │                  │   │
│  │                                                 ▼                  │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Service com Dependency Injection (ADR-007)                │    │   │
│  │  │  TaskService.create_task(..., session=session)             │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │                                                                    │   │
│  │  [+] Velocidade máxima (in-memory)                                 │   │
│  │  [+] Isolamento total (session descartada)                         │   │
│  │  [+] Sem dependência de filesystem                                 │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                    TESTES DE INTEGRAÇÃO (CLI)                      │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │                                                                    │   │
│  │  Fixture: isolated_db (tmp_path file)                              │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  db_path = tmp_path / "test_cli.db"                        │    │   │
│  │  │  monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))     │    │   │
│  │  │  SQLModel.metadata.create_all(engine)                      │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │                                  │                                 │   │
│  │                                  ▼                                 │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  CLI Runner                                                │    │   │
│  │  │  runner.invoke(app, ["task", "create", ...])               │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │                                  │                                 │   │
│  │                                  ▼                                 │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Command Layer => Service Layer => Database Layer          │    │   │
│  │  │  (Todos leem TIMEBLOCK_DB_PATH automaticamente)            │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │                                                                    │   │
│  │  [+] Testa fluxo real end-to-end                                   │   │
│  │  [+] Zero monkeypatch de módulos                                   │   │
│  │  [+] Cleanup automático (tmp_path)                                 │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Refatoração Necessária

### Arquivos a Modificar

| Arquivo                     | Ação                        | Motivo              |
| --------------------------- | --------------------------- | ------------------- |
| `config.py`                 | Remover lógica de DB path   | Eliminar duplicação |
| `migrations.py`             | Usar `engine.get_db_path()` | SSOT                |
| `conftest.py` (integration) | Padronizar fixture          | Consistência        |
| `test_list.py`              | Remover fixture local       | Usar conftest       |
| `test_list_filters.py`      | Remover fixture local       | Usar conftest       |
| `test_init.py`              | Remover fixture local       | Usar conftest       |

### Mudanças em config.py

```python
# ANTES (atual - REMOVER)
_db_path_env = os.getenv("TIMEBLOCK_DB_PATH")
if _db_path_env:
    DATABASE_PATH = Path(_db_path_env)
else:
    data_dir = Path(__file__).parent.parent / "data"
    DATABASE_PATH = data_dir / "timeblock.db"

# DEPOIS (proposto)
# Arquivo config.py não deve conter lógica de database path.
# Usar engine.get_db_path() como Single Source of Truth.
```

### Mudanças em migrations.py

```python
# ANTES
from timeblock.config import DATABASE_PATH

# DEPOIS
from timeblock.database.engine import get_db_path

def migrate():
    db_path = get_db_path()  # Leitura dinâmica
    ...
```

---

## Consequências

### Positivas

1. **Manutenibilidade:** Refatorações não quebram testes
2. **Simplicidade:** Uma única env var controla todo o sistema
3. **Robustez:** Zero dependência de estrutura de imports
4. **Testabilidade:** Fluxo CLI testado de ponta a ponta
5. **12-Factor Compliance:** Configuração externalizada
6. **CI/CD Friendly:** Fácil configurar em pipelines

### Negativas

1. **Velocidade:** Testes CLI usam arquivo (vs in-memory)
2. **Refatoração inicial:** Ajustar fixtures existentes

### Mitigações

- Testes unitários continuam in-memory (maioria dos testes)
- tmp_path do pytest limpa arquivos automaticamente
- Paralelização com pytest-xdist usa diretórios separados

---

## Alternativas Consideradas

### Alternativa 1: Monkeypatch de Múltiplos Módulos

```python
monkeypatch.setattr("timeblock.database.get_engine_context", mock)
monkeypatch.setattr("timeblock.commands.list.get_engine_context", mock)
monkeypatch.setattr("timeblock.services.task_service.get_engine_context", mock)
# ... N módulos
```

**Rejeitada:** Frágil, não escala, viola DRY.

### Alternativa 2: Singleton Global Mutável

```python
# database/engine.py
_current_engine = None

def set_engine(engine):
    global _current_engine
    _current_engine = engine
```

**Rejeitada:** Estado global, difícil de debugar, race conditions.

### Alternativa 3: Dependency Injection Container

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(create_engine, ...)
```

**Rejeitada:** Overengineering para CLI simples, adiciona dependência.

---

## Validação

### Critérios de Sucesso

1. Zero testes usando monkeypatch de `get_engine_context` entre módulos
2. Todos testes CLI usando fixture `isolated_db` do conftest
3. `config.py` sem lógica de database path
4. 100% testes passando após refatoração

### Comandos de Verificação

```bash
# Verificar que não há monkeypatch de get_engine_context
grep -rn "setattr.*get_engine_context" tests/ | grep -v conftest

# Deve retornar vazio (apenas conftest pode ter)

# Verificar fixtures locais de isolated_db (devem ser removidas)
grep -rn "def isolated_db" tests/ --include="*.py"

# Deve retornar apenas conftest.py
```

---

## Integração com Outros ADRs

- **ADR-007:** Service Layer com session injection (complementar)
- **ADR-019:** Test Naming Convention (nomenclatura de testes)
- **ADR-025:** Development Methodology (hierarquia DOCS => TDD)

---

## Referências

### Externas

- [12-Factor App: Config](https://12factor.net/config)
- [pytest: Monkeypatch Documentation](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [SQLModel: Testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/)
- [pytest-with-eric: Database Testing](https://pytest-with-eric.com/database-testing/pytest-sql-database-testing/)

### Internas

- ADR-007: Service Layer Pattern
- ADR-019: Test Naming Convention
- `docs/ssot/architecture.md` seção 4.4 (Database Layer)

---

## Histórico

- **2025-01-19:** Criado (versão 1.0)
- **Próximo:** Implementar refatoração de fixtures
