# Quality Metrics - TimeBlock Organizer

**Versão:** 2.1.0

**Relacionado:** roadmap.md, CHANGELOG.md

---

## 1. Métricas Atuais

Este documento consolida as métricas de qualidade do TimeBlock Organizer, servindo como fonte única de verdade para acompanhamento do progresso técnico. As métricas são atualizadas a cada sessão de desenvolvimento e refletem o estado real do código em produção.

- **Data de Referência:** 30 de Janeiro de 2026
- **Versão:** v1.4.1 (desenvolvimento)
- **Branch:** `develop`

### 1.1. Visão Geral

A tabela abaixo apresenta os indicadores principais de qualidade do projeto. O foco atual está em expandir a cobertura de testes E2E e integration, mantendo a qualidade do código com zero erros de tipagem.

| Categoria           | Valor Atual | Meta v1.5.0 | Status    |
| ------------------- | ----------- | ----------- | --------- |
| Testes Passando     | 685         | 750         | [OK]      |
| Testes Skipped      | 8           | 0           | [ATENÇÃO] |
| Cobertura Global    | 71%         | 80%         | [OK]      |
| Erros Mypy          | 0           | 0           | [OK]      |
| Commands Funcionais | 85%         | 100%        | [OK]      |

### 1.2. Distribuição de Testes

A pirâmide de testes está convergindo para o formato ideal. O aumento significativo de testes E2E na sessão atual (+28 testes) demonstra progresso na validação de fluxos completos do sistema.

| Tipo        | Quantidade | Percentual | Meta v1.5.0 | Status    |
| ----------- | ---------- | ---------- | ----------- | --------- |
| Unit        | 513        | 75%        | 70-75%      | [OK]      |
| Integration | 83         | 12%        | 20%         | [ABAIXO]  |
| E2E         | 42         | 6%         | 5-10%       | [OK]      |
| BDD         | 7          | 1%         | Manter      | [OK]      |
| Skipped     | 8          | 1%         | 0%          | [ATENÇÃO] |

### 1.3. Cobertura por Módulo

A cobertura de código reflete a qualidade dos testes em cada camada da aplicação. Módulos de serviço atingiram excelente cobertura após a implementação dos testes E2E de timer e task.

| Módulo    | Cobertura | Status    | Ação Requerida    |
| --------- | --------- | --------- | ----------------- |
| models/   | 95%       | [OK]      | Manutenção        |
| services/ | 85%       | [OK]      | Manutenção        |
| commands/ | 48%       | [ATENÇÃO] | +32pp (E2E tests) |
| utils/    | 90%       | [OK]      | Manutenção        |
| database/ | 91%       | [OK]      | Manutenção        |

---

## 2. Histórico de Métricas

O histórico de métricas permite identificar tendências e avaliar o impacto de cada release na qualidade do código. A versão 1.4.x marca uma recuperação significativa na cobertura após o débito técnico acumulado em v1.3.0.

### 2.1. Evolução por Release

| Release | Data     | Testes | Cobertura | Erros Mypy | Mudança Significativa |
| ------- | -------- | ------ | --------- | ---------- | --------------------- |
| v1.0.0  | Out/2025 | 50     | 30%       | 0          | Baseline              |
| v1.1.0  | Nov/2025 | 200    | 60%       | 12         | +150 testes           |
| v1.2.0  | Nov/2025 | 350    | 70%       | 38         | Status refactoring    |
| v1.3.0  | Dez/2025 | 454    | 61%       | 156        | Acúmulo de débito     |
| v1.3.3  | Jan/2026 | 558    | 67%       | 0          | Recuperação mypy      |
| v1.4.0  | Jan/2026 | 513    | 44%       | 0          | BRs formalizadas      |
| v1.4.1  | Jan/2026 | 685    | 71%       | 0          | E2E expansion (+172)  |

---

## 3. Metas e Critérios de Qualidade

Os critérios de qualidade definem o padrão mínimo aceitável para releases. Cada release deve passar por todos os gates obrigatórios antes de ser publicada.

### 3.1. Critérios de Release

**Obrigatórios (Gate de Release):**

- [x] Zero erros mypy em modo strict
- [ ] Zero testes skipped sem justificativa
- [ ] Cobertura global >= 80%
- [x] Cobertura de módulos críticos >= 85%
- [ ] 100% funcionalidades CLI operacionais

**Desejáveis (Qualidade Superior):**

- [ ] Cobertura >= 90%
- [x] Tempo de execução suite < 60s
- [x] Zero warnings ruff

### 3.2. Pirâmide de Testes

A pirâmide de testes define a distribuição ideal entre os diferentes tipos de teste. O objetivo é maximizar a cobertura com o menor custo de manutenção.

```
Distribuição Atual vs Alvo:

E2E (6%)          ████████░░░░░░░░  5-10%  [OK]
Integration (12%) ████████████░░░░  20%    [ABAIXO]
Unit (75%)        ████████████████  70-75% [OK]
```

---

## 4. Análise de Performance

O tempo de execução da suite de testes é crítico para manter a produtividade do desenvolvedor. Suites rápidas incentivam execução frequente e feedback imediato.

### 4.1. Tempo de Execução

| Fase              | Tempo Atual | Meta      | Status |
| ----------------- | ----------- | --------- | ------ |
| Unit tests        | 10s         | < 15s     | [OK]   |
| Integration tests | 5s          | < 10s     | [OK]   |
| E2E tests         | 7s          | < 15s     | [OK]   |
| **TOTAL**         | **22s**     | **< 40s** | [OK]   |

---

## 5. Cobertura de Business Rules

A rastreabilidade entre regras de negócio e testes garante que cada funcionalidade documentada está validada por testes automatizados.

### 5.1. Status por Domínio

| Domínio       | Total BRs | Com Testes | Cobertura |
| ------------- | --------- | ---------- | --------- |
| Routine       | 6         | 5          | 83%       |
| Habit         | 5         | 5          | 100%      |
| HabitInstance | 6         | 4          | 67%       |
| Skip          | 4         | 1          | 25%       |
| Streak        | 4         | 4          | 100%      |
| Task          | 6         | 5          | 83%       |
| Timer         | 8         | 7          | 88%       |
| Validation    | 3         | 3          | 100%      |
| **TOTAL**     | **67**    | **52**     | **78%**   |

---

## 6. Automação e CI/CD

A automação de qualidade opera em dois níveis: pre-commit hooks para feedback local imediato e pipeline GitLab CI/CD para validação completa no servidor.

### 6.1. Pre-commit Hooks

Executados localmente em cada `git commit`, garantindo que código problemático não entre no repositório.

| Hook        | Status  | Tempo | Bloqueante |
| ----------- | ------- | ----- | ---------- |
| ruff format | [ATIVO] | 1.2s  | Sim        |
| ruff check  | [ATIVO] | 0.8s  | Sim        |
| mypy        | [ATIVO] | 3.5s  | Não        |
| pytest-all  | [ATIVO] | ~30s  | Sim        |

**Total:** ~35s por commit

**Nota:** `pytest-all` executa a suite completa (unit + integration + BDD + e2e), substituindo o antigo `pytest-unit` que rodava apenas testes unitários.

### 6.2. GitLab CI/CD Pipeline

Pipeline executado em cada push e merge request, com jobs paralelos no stage `test`.

```
stages: test -> build -> deploy

test:unit          pytest tests/unit/ -v --cov        [branches, MRs]
test:integration   pytest tests/integration/ -v       [branches, MRs]
test:bdd           pytest tests/bdd/ -v               [branches, MRs]
test:e2e           pytest tests/e2e/ -v               [branches, MRs]
test:lint          ruff check src/timeblock           [branches, MRs]
test:typecheck     mypy (allow_failure: true)         [branches, MRs]
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
| test:typecheck   | Não        | -            |
| build:docs       | Sim        | site/        |
| pages            | Sim        | public/      |

**Imagem base:** `python:3.13`

**Referência:** `.gitlab-ci.yml`

---

## 7. Referências

- **ROADMAP:** `docs/core/roadmap.md`
- **CHANGELOG:** `CHANGELOG.md`
- **ADR-007:** Service Layer com Dependency Injection
- **ADR-019:** Test Naming Convention
- **ADR-026:** Test Database Isolation Strategy

---

**Versão do documento:** 2.1.0

**Última atualização:** 01 de Fevereiro de 2026
