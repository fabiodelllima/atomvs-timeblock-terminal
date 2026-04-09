# ADR-033: Fixture scope="session" com Rollback Transacional

- **Status:** Aceito
- **Data:** 2026-03-05
- **Relacionado:** ADR-026 (Test Database Isolation), ADR-031 (TUI Implementation)

## Contexto

Os testes de integração usam `scope="function"` para a fixture `integration_engine`, o que significa que cada teste cria e destrói o schema SQLite completo. Em ambiente local (NVMe, CPU dedicada) a suíte roda em ~3s. No shared runner do GitLab.com (recursos compartilhados, I/O virtualizado) o mesmo conjunto ultrapassa 30 minutos — já exigiu aumento de timeout de 30m para 60m e adição de `pytest-xdist`.

Com a Sprint 4 introduzindo CRUD via dashboard, o número de testes de integração vai crescer substancialmente (estimativa: +40-60 testes para cobrir fluxos de rotinas, hábitos e tarefas via TUI). Se cada teste continuar criando/destruindo schema, o tempo de pipeline se torna insustentável.

Humble e Farley (2010, p. 185) estabelecem 10 minutos como limite para o commit stage: "We generally aim to keep our commit stage at under ten minutes. When this limit is broken, developers start doing two things: They start checking in less frequently and they stop caring about whether or not the commit test suite passes." O pipeline já está na borda desse limite.

## Decisão

### 1. Engine e Schema com scope="session"

Engine e `create_all` executados uma única vez por sessão de testes. O custo de criação de schema (~200ms) passa de O(N) para O(1).

```python
@pytest.fixture(scope="session")
def integration_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()
```

### 2. Isolamento por Rollback Transacional

Cada teste roda dentro de uma transação que é revertida ao final. Técnica documentada por Humble e Farley (2010, p. 375): "For database-related tests, we create a transaction at the beginning of the test and at the conclusion of the test we roll back the transaction."

```python
@pytest.fixture
def integration_session(integration_engine):
    connection = integration_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

### 3. Restrição: flush em vez de commit

Testes **não podem** chamar `session.commit()` — devem usar `session.flush()` para materializar dados sem finalizar a transação. Isso garante que o rollback final reverta tudo.

Para testes que validam comportamento de commit (ex: constraints de unicidade), usar `session.begin_nested()` (savepoint) seguido de rollback do savepoint.

### 4. Compatibilidade com pytest-xdist

Quando rodando com `-n auto`, cada worker recebe sua própria engine (o `scope="session"` é por-worker no xdist). Não há compartilhamento de estado entre workers — cada um tem banco in-memory independente.

## Consequências

**Positivas:**

- Redução estimada de 80% no tempo por teste de integração
- Pipeline mantém-se abaixo de 10 minutos mesmo com crescimento da suíte
- Testes continuam isolados (rollback garante estado limpo)
- Compatível com infraestrutura existente (xdist, SQLite in-memory)

**Negativas:**

- Testes não podem testar comportamento pós-commit (ex: autoincrement reset)
- Desenvolvedores precisam lembrar de usar `flush()` em vez de `commit()`
- Bugs que só se manifestam com commit real não serão capturados por testes de integração (devem ser cobertos em E2E)

**Riscos mitigados:**

- Linter customizado ou grep no CI para detectar `session.commit()` em arquivos de teste
- Documentação clara no conftest sobre a restrição

## Alternativas Consideradas

### pytest-xdist sozinho

Já implementado (Sprint 3.2). Complementar, mas não substitui a otimização de fixture. Com 4 workers e schema por teste, o tempo cai para ~8min — ainda na borda do limite. Com session fixture + xdist, cai para ~2min.

### Docker image slim

Reduz tempo de pull (~30%), mas não afeta tempo de execução dos testes.

### pytest-testmon

Roda apenas testes afetados por mudanças. Útil para PRs incrementais, mas não resolve o problema de suíte completa (main/develop).

## Referências

HUMBLE, J.; FARLEY, D. _Continuous Delivery_. Boston: Addison-Wesley, 2010, p. 185, 375, 378.

SQLALCHEMY. Session Basics — Using SAVEPOINT. _SQLAlchemy 2.0 Documentation_, 2024.

PYTEST. How to use fixtures — Scope. _pytest Documentation_, 2024.
