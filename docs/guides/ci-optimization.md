# Otimização CI/CD

**Versão:** 1.0.0

**Documentos relacionados:** development.md, quality-metrics.md, sprints.md

---

## Sumário

1. [Contexto do Problema](#1-contexto-do-problema)
2. [Diagnóstico](#2-diagnóstico)
3. [Soluções Implementadas — Fase 1](#3-soluções-implementadas--fase-1)
4. [Resultados Medidos](#4-resultados-medidos)
5. [Soluções Planejadas — Fase 2](#5-soluções-planejadas--fase-2)
6. [Decisões Técnicas](#6-decisões-técnicas)
7. [Referências](#7-referências)

---

## 1. Contexto do Problema

O job `test:integration` no pipeline GitLab CI estourava o timeout de 30 minutos com apenas 52% da suíte executada. A mesma suíte de 116 testes roda em 3,1 segundos localmente, evidenciando que o gargalo não é o ambiente de teste, mas a infraestrutura de execução.

Conforme documentado pela GitLab, "[a]vailability of the runners and the resources they are provisioned with" são fatores determinantes no desempenho de pipelines (GITLAB, 2025a, seção "Identify bottlenecks"). Os shared runners do GitLab.com operam em containers Docker com recursos limitados e I/O de disco lento. A fixture de integração criava e destruía o schema completo do banco SQLite a cada teste (`scope="function"`), amplificando o overhead de I/O no ambiente virtualizado por um fator de aproximadamente 500x em relação ao ambiente local. Humble e Farley alertam que testes interagindo com banco de dados são "dramatically slower to run" e que "the statefulness of the tests can be a handicap when you want to repeat them, or run several similar tests in close succession" (HUMBLE; FARLEY, 2010, p. 179).

---

## 2. Diagnóstico

### 2.1. Métricas de comparação

| Ambiente   | Testes           | Tempo total | Tempo médio/teste |
| ---------- | ---------------- | ----------- | ----------------- |
| Local      | 116              | 3,10s       | ~0,03s            |
| CI (antes) | 60/116 (timeout) | 30min+      | ~17s              |

### 2.2. Identificação dos gargalos

O `pytest --durations=10` local revelou que o teste mais lento leva apenas 0,21s — confirmando que o código de teste não é o problema. A análise do trace do CI mostrou intervalos de 15–20 segundos entre testes consecutivos, atribuíveis ao ciclo `create_all` / `drop_all` por teste no ambiente Docker.

### 2.3. Ferramentas de diagnóstico utilizadas

O diagnóstico seguiu a abordagem recomendada pela literatura de Continuous Delivery: "Ideally, a commit stage should take less than five minutes to run, and certainly no more than ten" (HUMBLE; FARLEY, 2010, p. 169). O job de integração excedia 30 minutos, violando gravemente esse princípio. As ferramentas empregadas foram `pytest --durations=10` para identificar testes lentos, `glab ci trace` para analisar o log do runner, e comparação direta entre execução local e CI para isolar o fator ambiental.

---

## 3. Soluções Implementadas — Fase 1

### 3.1. Aumento de timeout (30min → 60min)

Medida de desbloqueio imediato enquanto otimizações são aplicadas. O timeout é limite de segurança, não de performance — aumentá-lo não mascara o problema, apenas impede falhas espúrias durante o período de transição. Conforme Humble e Farley recomendam: "Constantly work to improve the quality, design, and performance of the scripts in your commit stage as they evolve. An efficient, fast, reliable commit stage is a key enabler of productivity for any development team" (HUMBLE; FARLEY, 2010, p. 173).

```yaml
test:integration:
  timeout: 60m
```

**Commit:** `de69be0`

### 3.2. Paralelização com pytest-xdist

O pytest-xdist distribui testes entre múltiplos workers (um por core de CPU disponível). Humble e Farley enfatizam que "the most important property of unit tests is that they should be very fast to execute" e que a cobertura deve atingir "around 80% [...] giving you a good level of confidence that when they pass, the application is fairly likely to be working" (HUMBLE; FARLEY, 2010, p. 177). A paralelização via xdist complementa essa diretriz ao reduzir o tempo total mesmo quando testes individuais são rápidos mas numerosos. Conforme a documentação oficial: "Tests are grouped by their containing file. [...] This guarantees that all tests in a file run in the same worker" (PYTEST-XDIST, 2024, seção Distribution modes). Essa estratégia preserva o isolamento de fixtures sem exigir refatoração.

```yaml
test:integration:
  before_script:
    - pip install --no-deps -e .
    - pip install pytest-xdist
  script:
    - COVERAGE_FILE=.coverage.integration python -m pytest tests/integration/ tests/bdd/
      -v --tb=short -n auto --dist=loadfile
      --cov=timeblock --no-cov-on-fail --cov-fail-under=0
```

A instalação explícita do `pytest-xdist` no `before_script` é necessária porque o `pip install --no-deps -e .` não traz dependências opcionais. O pacote foi adicionado ao `pyproject.toml` em `[project.optional-dependencies] dev` para uso local e documentação.

**Commits:** `de69be0` (pyproject.toml), `41e23ce` (before_script), `85a3cb4` (fix coverage)

### 3.3. Ajuste de coverage no job integration

O pytest-cov com `--cov` herda `fail_under = 80` do `pyproject.toml`. A cobertura do integration isolado é ~42% (esperado — cobre apenas paths exercitados pelos testes de integração). O threshold de 80% aplica-se exclusivamente no job `coverage:report`, que combina `unit + integration + e2e` via `coverage combine`. Essa abordagem é consistente com a recomendação de Humble e Farley: "We could, for example, fail the commit stage if the unit test coverage drops below 60%, and have it pass but with the status of amber, not green, if it goes below 80%" (HUMBLE; FARLEY, 2010, p. 172) — o threshold deve ser avaliado sobre a cobertura combinada, não sobre subconjuntos isolados.

A solução foi adicionar `--cov-fail-under=0 --no-cov-on-fail` ao job de integração, mantendo a geração do arquivo `.coverage.integration` sem falhar prematuramente.

**Commit:** `85a3cb4`

---

## 4. Resultados Medidos

| Métrica                  | Antes            | Depois         | Melhoria                |
| ------------------------ | ---------------- | -------------- | ----------------------- |
| Tempo do job integration | 30min+ (timeout) | 7min 42s       | -75%                    |
| Testes executados        | 60/116 (52%)     | 172/172 (100%) | Pipeline verde          |
| Pipeline completo        | Falha            | ~10min         | Funcional               |
| Coverage report          | Skipped          | Success        | Fase final desbloqueada |

---

## 5. Soluções Planejadas — Fase 2

### 5.1. Fixture scope="session" com rollback — Prioridade 1

A otimização de maior impacto estimado. O estado atual cria engine e schema a cada teste; a proposta é criar uma vez por sessão e usar rollback entre testes para garantir isolamento.

**Estado atual:**

```python
@pytest.fixture(scope="function")
def integration_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)  # A cada teste
    yield engine
    SQLModel.metadata.drop_all(engine)    # A cada teste
    engine.dispose()
```

**Proposta:**

```python
@pytest.fixture(scope="session")
def integration_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)  # Uma vez
    yield engine
    engine.dispose()

@pytest.fixture(autouse=True)
def _rollback_after_test(integration_session):
    yield
    integration_session.rollback()        # Rollback por teste
```

**Restrições:** testes não podem chamar `session.commit()` — devem usar `session.flush()` para validar constraints sem persistir. A documentação do SQLAlchemy descreve o padrão de framing `begin / commit / rollback` como mecanismo fundamental de isolamento transacional (SQLALCHEMY, 2024). Fowler reforça: "The key thing about Unit of Work is that, when it comes time to commit, the Unit of Work decides what to do. It opens a transaction, does any concurrency checking [...] and writes changes out to the database" (FOWLER, 2002, p. 185). Com xdist, a documentação oficial adverte que "each worker process will perform its own collection and execute a subset of all tests" e que fixtures de escopo alto "will execute the fixture code more than once" (PYTEST-XDIST, 2024, seção How-tos), o que na prática fornece isolamento natural entre workers.

**Impacto estimado:** -80% do tempo por teste. O padrão de rollback por teste implementa o conceito de Unit of Work descrito por Fowler: "A Unit of Work keeps track of everything you do during a business transaction that can affect the database. When you're done, it figures out everything that needs to be done to alter the database as a result of your work" (FOWLER, 2002, p. 184). No contexto de testes, cada teste opera como uma transação isolada cujas mudanças são descartadas via rollback ao final, garantindo que o estado inicial do banco permaneça intacto para o próximo teste.

**Rastreabilidade:** BR-TEST-001, ADR-033

### 5.2. GitLab `parallel` keyword — Prioridade 2

O GitLab CI oferece divisão nativa de um job em N sub-jobs executados em runners separados. O keyword `parallel` cria N instâncias do mesmo job, disponibilizando as variáveis `CI_NODE_INDEX` e `CI_NODE_TOTAL` para distribuição programática dos testes (GITLAB, 2025b). Combinado com `pytest-test-groups`, distribui testes automaticamente.

```yaml
test:integration:
  parallel: 2
  script:
    - pip install pytest-test-groups
    - pytest tests/integration/
      --test-group-count=$CI_NODE_TOTAL
      --test-group=$CI_NODE_INDEX
```

**Impacto estimado:** tempo total dividido por N (número de sub-jobs).

### 5.3. Docker image otimizada — Prioridade 3

Avaliar substituição da imagem base por `python:3.13-slim` ou Alpine. A documentação do GitLab recomenda: "Use a small base image, for example `debian-slim`" e "do not install convenience tools [...] if they aren't strictly needed" (GITLAB, 2025a, seção Docker Images).

**Impacto estimado:** -30% no tempo de startup do job.

### 5.4. pytest-testmon — Prioridade 4

Plugin que rastreia quais testes são afetados por mudanças no código e executa apenas os relevantes. Requer compartilhamento de dados testmon entre pipelines via cache do GitLab. A documentação do GitLab recomenda "use `rules` to skip tests that aren't needed" e "run non-essential scheduled pipelines less frequently" (GITLAB, 2025a, seção Reduce how often jobs run); o testmon automatiza essa seleção a nível de teste individual.

**Impacto estimado:** -70% em PRs incrementais.

---

## 6. Decisões Técnicas

| ID       | Decisão                                   | Justificativa                               |
| -------- | ----------------------------------------- | ------------------------------------------- |
| D-CI-001 | `--dist=loadfile` em vez de `--dist=load` | Preserva isolamento de fixtures por arquivo |
| D-CI-002 | `--cov-fail-under=0` no job integration   | Threshold aplica-se apenas no combine       |
| D-CI-003 | `pip install pytest-xdist` explícito      | `--no-deps` não instala dependências dev    |
| D-CI-004 | `COVERAGE_FILE=.coverage.integration`     | Compatibilidade com `coverage combine`      |
| D-CI-005 | Timeout 60min (temporário)                | Será reduzido após Fase 2                   |

---

## 7. Referências

GITLAB. Pipeline efficiency. _GitLab Docs_, 2025a. Seções: "Identify bottlenecks", "Docker Images". Disponível em: <https://docs.gitlab.com/ee/ci/pipelines/pipeline_efficiency.html>.

GITLAB. Job keywords: `parallel`. _GitLab CI/CD YAML syntax reference_, 2025b. Disponível em: <https://docs.gitlab.com/ee/ci/yaml/#parallel>.

PYTEST-XDIST. Running tests across multiple CPUs — Distribution modes. _pytest-xdist Documentation_, 2024. Seção: `--dist loadfile`. Disponível em: <https://pytest-xdist.readthedocs.io/en/stable/distribution.html>.

PYTEST-XDIST. How-tos — Making session-scoped fixtures execute only once. _pytest-xdist Documentation_, 2024. Disponível em: <https://pytest-xdist.readthedocs.io/en/stable/how-to.html>.

PYTEST. How to use fixtures — Fixture scopes. _pytest Documentation_, 2024. Disponível em: <https://docs.pytest.org/en/stable/how-to/fixtures.html#fixture-scopes>.

SQLALCHEMY. Session basics — Framing out a begin / commit / rollback block. _SQLAlchemy 2.0 Documentation_, 2024. Disponível em: <https://docs.sqlalchemy.org/en/20/orm/session_basics.html>.

FOWLER, M. _Patterns of Enterprise Application Architecture_. Boston: Addison-Wesley, 2002. Cap. 11: Unit of Work, p. 184–194.

HUMBLE, J.; FARLEY, D. _Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation_. Boston: Addison-Wesley, 2010. Cap. 7: The Commit Stage, p. 169–190.

---

**Última atualização:** 05 de Março de 2026
