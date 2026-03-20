# Workflow de Desenvolvimento

**Versão:** 3.0.0

**Status:** Consolidado (SSOT)

Para a fundamentação teórica (Engenharia de Requisitos, BDD, TDD, ADRs), consulte [Metodologia de Desenvolvimento](../explanation/development-methodology.md).

---

## 7. Estrutura de Testes

A suite de testes é organizada em quatro categorias com distribuição que segue a pirâmide de testes clássica. Testes unitários formam a base larga (rápidos, isolados, maioria), enquanto testes E2E formam o topo estreito (lentos, integrados, poucos). Testes BDD ocupam posição intermediária como documentação executável e validação de requisitos.

### Pirâmide de Testes

```
tests/
├── bdd/                 # ~9% (validação de requisitos)
│   ├── features/        # .feature (Gherkin)
│   └── step_defs/       # Steps Python
├── unit/                # ~70-75% (verificação isolada)
│   ├── test_models/
│   └── test_services/
├── integration/         # ~15-20% (Service + DB)
│   ├── test_models/
│   └── test_services/
└── e2e/                 # ~5% (CLI/TUI completa)
    └── test_commands/
```

### Características por Tipo

| Tipo        | Velocidade | Isolamento | Dependências     | Propósito                 |
| ----------- | ---------- | ---------- | ---------------- | ------------------------- |
| Unit        | < 1ms      | Total      | Mocks/fixtures   | Verificar BR isoladamente |
| Integration | < 100ms    | Parcial    | SQLite in-memory | Verificar Service + DB    |
| E2E         | < 1s       | Nenhum     | CLI real         | Verificar experiência     |
| BDD         | < 100ms    | Parcial    | Fixtures         | Validar requisitos        |

### Fixtures e Isolamento

Fixtures são organizados em conftest.py hierárquicos, seguindo ADR-026 (Test Database Isolation Strategy). Cada teste recebe uma session isolada com banco in-memory, garantindo que testes não interferem entre si.

```python
# tests/conftest.py (raiz)
@pytest.fixture
def engine():
    """Engine SQLite in-memory para testes."""
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def session(engine):
    """Session isolada por teste."""
    with Session(engine) as session:
        yield session
```

### Markers

Markers pytest permitem execução seletiva por tipo ou domínio:

```bash
# Executar apenas unitários
python -m pytest tests/unit/ -v

# Executar testes de um domínio específico
python -m pytest -k "habit" -v

# Suite completa
python -m pytest tests/ -v --cov
```

---

## 8. Padrões de Qualidade

Os padrões de qualidade definem o mínimo aceitável para que código entre no repositório. As verificações são automatizadas via pre-commit hooks e CI/CD pipeline, tornando violações detectáveis antes do merge. O documento quality-metrics.md mantém métricas detalhadas e histórico de evolução.

### Critérios de Commit (Pre-commit)

Todo commit passa por verificação local automática antes de ser criado:

| Check      | Ferramenta  | Bloqueante | Tempo |
| ---------- | ----------- | ---------- | ----- |
| Linting    | ruff check  | Sim        | ~1s   |
| Formatting | ruff format | Sim        | ~1s   |
| Type check | mypy        | Sim        | ~3s   |
| Test suite | pytest      | Sim        | ~15s  |

**Total:** ~20s por commit. A suíte completa executa em cada commit para garantir que código quebrado nunca entre no repositório.

### Critérios de Release

Além das verificações por commit, releases devem satisfazer critérios cumulativos:

**Obrigatórios:**

- Zero erros mypy em modo strict
- Zero testes skipped sem justificativa documentada
- Cobertura global >= 80%
- Cobertura de módulos críticos (models, services) >= 85%
- Pipeline CI/CD verde em todos os jobs

**Desejáveis:**

- Cobertura >= 90%
- Tempo de execução da suite < 40s
- Zero warnings ruff

### Rastreabilidade BR → Test → Code

Cada business rule deve ter rastreabilidade completa, conforme exigido pela disciplina de Engenharia de Requisitos (SWEBOK v4.0, Ch.1 Requirements Traceability):

| Artefato           | Localização                 | Formato                     |
| ------------------ | --------------------------- | --------------------------- |
| Requisito (BR)     | docs/reference/business-rules/index.md | BR-DOMAIN-XXX               |
| Validação (BDD)    | tests/bdd/features/         | Gherkin (Given/When/Then)   |
| Verificação (Unit) | tests/unit/test_services/   | TestBRDomainXXX             |
| Implementação      | src/timeblock/services/     | Método no service           |

**Verificação rápida:**

```bash
# BR especificada?
grep -r "BR-HABIT-003" docs/reference/business-rules/index.md

# Teste existe?
grep -rn "BR-HABIT-003\|br_habit_003" tests/

# Naming correto? (deve retornar vazio - sem RN-*)
grep -rn "RN-EVENT-\|RN-HABIT-\|TestRN\|test_rn_" tests/ --include="*.py"
```

---

## 9. Git Workflow

O projeto adota gitflow com commits atômicos em português brasileiro. Cada commit representa uma mudança lógica única, facilitando bisect, revert e code review. A estratégia dual-repo sincroniza GitLab (desenvolvimento) com GitHub (showcase público).

### Branch Strategy

```
main          ───────────────────────────────── produção
                    ↑ merge --no-ff
develop       ───────────────────────────────── integração
               ↗ ↑ merge --no-ff
feat/xxx     ── feature branch ──────────────── desenvolvimento
fix/xxx      ── bugfix branch
docs/xxx     ── documentação
refactor/xxx ── refatoração
```

### Formato de Commit

```
type(scope): Descrição em português com primeira maiúscula

- Detalhes quantitativos quando aplicável
- Referência a BRs ou ADRs quando relevante

Fixes #123 (se aplicável)
```

**Types:** feat, fix, refactor, test, docs, chore, perf

**Exemplo:**

```
feat(models): Adiciona campo user_override ao HabitInstance

- Campo booleano com padrão False
- Service atualizado para setar flag
- 2 novos testes unitários
- Ref: BR-HABITINSTANCE-004
```

### Merge Strategy

O projeto preserva commits atômicos ao integrar feature branches em develop, usando merge --no-ff para manter a topologia de branches visível no histórico. Squash merge nunca é usado — cada commit atômico carrega uma mudança lógica única com mensagem descritiva, facilitando bisect, revert e auditoria. O comando padrão é `glab mr merge <number> --yes` no GitLab, sem flag --squash.

### Tags e Releases

Tags anotadas marcam releases no branch main:

```bash
git tag -a v1.7.0 -m "v1.7.0: TUI com Textual"
git push origin main --tags
```

### Dual-Repo

O GitLab é fonte de verdade para desenvolvimento. O GitHub é showcase público sincronizado automaticamente via CI/CD. Detalhes completos em `docs/guides/cicd-flow.md`.

---

## 10. Gestão de Sprints

Sprints organizam o trabalho em iterações de 1-2 semanas com escopo definido e critérios de aceitação claros. O planejamento ativo reside em `docs/reference/sprints.md` enquanto sprints concluídos são arquivados em `docs/reference/sprints-archive.md`.

### Estrutura de Sprint

Cada sprint define:

- **Objetivo:** Descrição concisa do que será entregue
- **BRs incluídas:** Lista de business rules no escopo
- **Critérios de aceitação:** Condições verificáveis de conclusão
- **Checklist de tarefas:** Itens atômicos com checkbox

### Cerimônias

| Cerimônia    | Momento | Propósito                         |
| ------------ | ------- | --------------------------------- |
| Planejamento | Início  | Selecionar BRs, definir escopo    |
| Daily        | Diário  | Check-in, identificar bloqueios   |
| Review       | Fim     | Validar entregas contra critérios |
| Retro        | Fim     | Identificar melhorias de processo |

### Versionamento

Sprints são agrupados por versão (v1.7.0, v1.8.0, etc.). Cada versão pode conter múltiplos sprints, cada um com escopo auto-contido. O número do sprint é sequencial dentro da versão (Sprint 0, Sprint 1, etc.), onde Sprint 0 é reservado para setup e preparação de infraestrutura.

---
