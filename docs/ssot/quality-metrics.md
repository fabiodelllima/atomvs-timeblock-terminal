# Quality Metrics - TimeBlock Organizer

**Versão:** 2.2.0

**Relacionado:** roadmap.md, CHANGELOG.md

---

## 1. Métricas Atuais

Este documento consolida as métricas de qualidade do TimeBlock Organizer, servindo como fonte única de verdade para acompanhamento do progresso técnico. As métricas são atualizadas a cada sessão de desenvolvimento e refletem o estado real do código em produção.

- **Data de Referência:** 01 de Fevereiro de 2026
- **Versão:** v1.4.1 (desenvolvimento)

### 1.1. Visão Geral

| Categoria           | Valor Atual | Meta v1.5.0 | Status |
| ------------------- | ----------- | ----------- | ------ |
| Testes Passando     | 618         | 750         | [OK]   |
| Testes Skipped      | 0           | 0           | [OK]   |
| Cobertura Global    | 72%         | 80%         | [OK]   |
| Erros Mypy          | 0           | 0           | [OK]   |
| Commands Funcionais | 85%         | 100%        | [OK]   |

### 1.2. Distribuição de Testes

A pirâmide de testes mostra crescimento significativo nos testes BDD, com 56 cenários automatizados. A cobertura E2E atingiu a faixa alvo. Integration tests permanecem abaixo da meta.

| Tipo        | Quantidade | Percentual | Meta v1.5.0 | Status   |
| ----------- | ---------- | ---------- | ----------- | -------- |
| Unit        | 472        | 76%        | 70-75%      | [OK]     |
| Integration | 60         | 10%        | 20%         | [ABAIXO] |
| E2E         | 30         | 5%         | 5-10%       | [OK]     |
| BDD         | 56         | 9%         | Manter      | [OK]     |
| Skipped     | 0          | 0%         | 0%          | [OK]     |

### 1.3. Cobertura por Módulo

Cobertura calculada por `pytest --cov` em 01/02/2026. Valores baseados em statements cobertos.

| Módulo    | Cobertura | Status    | Ação Requerida               |
| --------- | --------- | --------- | ---------------------------- |
| models/   | ~98%      | [OK]      | Manutenção                   |
| services/ | ~78%      | [OK]      | routine_service, tag_service |
| commands/ | ~35%      | [CRÍTICO] | +45pp (integration + E2E)    |
| utils/    | ~98%      | [OK]      | Manutenção                   |
| database/ | ~60%      | [ATENÇÃO] | migration_001 sem cobertura  |

**Detalhamento services/ (por arquivo):**

| Arquivo                     | Cobertura | Observação              |
| --------------------------- | --------- | ----------------------- |
| habit_service.py            | 100%      | -                       |
| event_reordering_models.py  | 100%      | -                       |
| task_service.py             | 92%       | -                       |
| timer_service.py            | 92%       | -                       |
| habit_instance_service.py   | 88%       | -                       |
| event_reordering_service.py | 61%       | Fluxo principal parcial |
| routine_service.py          | 53%       | Déficit significativo   |
| tag_service.py              | 29%       | Déficit crítico         |

---

## 2. Histórico de Métricas

O histórico permite identificar tendências e avaliar o impacto de cada release na qualidade do código. A versão 1.4.x marca recuperação após o débito técnico acumulado em v1.3.0.

### 2.1. Evolução por Release

| Release  | Data     | Testes | Cobertura | Erros Mypy | Mudança Significativa      |
| -------- | -------- | ------ | --------- | ---------- | -------------------------- |
| v1.0.0   | Out/2025 | 50     | 30%       | 0          | Baseline                   |
| v1.1.0   | Nov/2025 | 200    | 60%       | 12         | +150 testes                |
| v1.2.0   | Nov/2025 | 350    | 70%       | 38         | Status refactoring         |
| v1.3.0   | Dez/2025 | 454    | 61%       | 156        | Acúmulo de débito          |
| v1.3.3   | Jan/2026 | 558    | 67%       | 0          | Recuperação mypy           |
| v1.4.0   | Jan/2026 | 513    | 44%       | 0          | BRs formalizadas           |
| v1.4.1   | Jan/2026 | 685    | 71%       | 0          | E2E expansion              |
| v1.4.1\* | Fev/2026 | 618    | 72%       | 0          | Typecheck bloqueante no CI |

_Nota: A redução de 685 para 618 testes reflete limpeza de testes duplicados e consolidação. Cobertura subiu 1pp apesar da redução._

---

## 3. Metas e Critérios de Qualidade

Os critérios de qualidade definem o padrão mínimo aceitável para releases. Cada release deve passar por todos os gates obrigatórios antes de ser publicada.

### 3.1. Critérios de Release

**Obrigatórios (Gate de Release):**

- [x] Zero erros mypy em modo strict
- [x] Zero testes skipped sem justificativa
- [ ] Cobertura global >= 80%
- [x] Cobertura de módulos críticos >= 85%
- [ ] 100% funcionalidades CLI operacionais

**Desejáveis (Qualidade Superior):**

- [ ] Cobertura >= 90%
- [x] Tempo de execução suite < 60s
- [x] Zero warnings ruff

### 3.2. Pirâmide de Testes

A pirâmide define a distribuição ideal entre os tipos de teste. O objetivo é maximizar cobertura com o menor custo de manutenção.

```
Distribuição Atual vs Alvo:

E2E (5%)          ████████░░░░░░░░  5-10%  [OK]
BDD (9%)          ██████████████░░  Manter [OK]
Integration (10%) ████████████░░░░  20%    [ABAIXO]
Unit (76%)        ████████████████  70-75% [OK]
```

---

## 4. Análise de Performance

O tempo de execução da suite é crítico para manter produtividade. Suites rápidas incentivam execução frequente e feedback imediato.

### 4.1. Tempo de Execução

| Fase           | Tempo Atual | Meta  | Status |
| -------------- | ----------- | ----- | ------ |
| Suite completa | 14.5s       | < 40s | [OK]   |

**Medição:** `pytest tests/ -v --tb=no --cov` em 01/02/2026.

---

## 5. Cobertura de Business Rules

A rastreabilidade entre regras de negócio e testes garante que cada funcionalidade documentada está validada por testes automatizados.

### 5.1. Status por Domínio

| Domínio       | Total BRs | Com Testes | Cobertura | BRs Faltantes        |
| ------------- | --------- | ---------- | --------- | -------------------- |
| Routine       | 6         | 5          | 83%       | BR-ROUTINE-006       |
| Habit         | 5         | 5          | 100%      | -                    |
| HabitInstance | 6         | 6          | 100%      | -                    |
| Skip          | 4         | 1          | 25%       | BR-SKIP-002/003/004  |
| Streak        | 4         | 4          | 100%      | -                    |
| Task          | 6         | 5          | 83%       | BR-TASK-006          |
| Timer         | 8         | 8          | 100%      | -                    |
| Reorder       | 6         | 6          | 100%      | -                    |
| Validation    | 3         | 3          | 100%      | -                    |
| CLI           | 3         | 1          | 33%       | BR-CLI-001/003       |
| Tag           | 2         | 0          | 0%        | BR-TAG-001/002       |
| **TOTAL**     | **53**    | **44**     | **83%**   | **9 BRs sem testes** |

### 5.2. Prioridade de Cobertura Pendente

| Prioridade | BRs                         | Justificativa                 |
| ---------- | --------------------------- | ----------------------------- |
| Alta       | BR-SKIP-002/003/004         | Domínio com 25% de cobertura  |
| Alta       | BR-TAG-001/002              | Domínio com 0% de cobertura   |
| Média      | BR-CLI-001/003              | Interface com usuário         |
| Baixa      | BR-ROUTINE-006, BR-TASK-006 | Domínios já com boa cobertura |

---

## 6. Automação e CI/CD

A automação de qualidade opera em dois níveis: pre-commit hooks para feedback local imediato e pipeline CI/CD para validação completa no servidor.

### 6.1. Pre-commit Hooks

Executados localmente em cada `git commit`, garantindo que código problemático não entre no repositório.

| Hook        | Status  | Tempo | Bloqueante |
| ----------- | ------- | ----- | ---------- |
| ruff format | [ATIVO] | 1.2s  | Sim        |
| ruff check  | [ATIVO] | 0.8s  | Sim        |
| mypy        | [ATIVO] | 3.5s  | Não        |
| pytest-all  | [ATIVO] | ~15s  | Sim        |

**Total:** ~20s por commit

**Nota:** `pytest-all` executa a suite completa (unit + integration + BDD + e2e). Mypy local ainda não bloqueante no pre-commit; considerar tornar bloqueante agora que erros estão zerados.

### 6.2. GitLab CI/CD Pipeline

Pipeline executado em cada push e merge request, com jobs paralelos no stage `test`.

```
stages: test -> build -> deploy

test:unit          pytest tests/unit/ -v --cov        [branches, MRs]
test:integration   pytest tests/integration/ -v       [branches, MRs]
test:bdd           pytest tests/bdd/ -v               [branches, MRs]
test:e2e           pytest tests/e2e/ -v               [branches, MRs]
test:lint          ruff check src/timeblock           [branches, MRs]
test:typecheck     mypy --check-untyped-defs          [branches, MRs]
build:docs         mkdocs build                       [develop, main]
pages              mkdocs build + deploy              [main]
```

| Job              | Bloqueante | Artefatos    |
| ---------------- | ---------- | ------------ |
| test:unit        | Sim        | coverage.xml |
| test:integration | Sim        | -            |
| test:bdd         | Sim        | -            |
| test:e2e         | Sim        | -            |
| test:lint        | Sim        | -            |
| test:typecheck   | Sim        | -            |
| build:docs       | Sim        | site/        |
| pages            | Sim        | public/      |

**Imagem base:** `python:3.13`

**Referência:** `.gitlab-ci.yml`, `.github/workflows/ci.yml`

### 6.3. GitHub Actions (Dual-Repo)

Pipeline espelho no GitHub para validação no repositório de showcase.

| Job       | Descrição                           | Bloqueante |
| --------- | ----------------------------------- | ---------- |
| lint      | ruff check                          | Sim        |
| typecheck | mypy --check-untyped-defs           | Sim        |
| test      | Matrix: unit, integration, bdd, e2e | Sim        |

---

## 7. Referências

- **ROADMAP:** `docs/ssot/roadmap.md`
- **CHANGELOG:** `CHANGELOG.md`
- **ADR-007:** Service Layer com Dependency Injection
- **ADR-019:** Test Naming Convention
- **ADR-026:** Test Database Isolation Strategy

---

**Versão do documento:** 2.2.0

**Última atualização:** 01 de Fevereiro de 2026
