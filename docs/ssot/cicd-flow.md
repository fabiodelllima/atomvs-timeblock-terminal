# CI/CD Flow

## Visão Geral

O sistema de CI/CD do TimeBlock Organizer implementa uma estratégia de proteção em múltiplas camadas, projetada para detectar problemas de qualidade o mais cedo possível no ciclo de desenvolvimento. Esta abordagem "shift-left" garante que código quebrado seja bloqueado antes de chegar aos repositórios remotos, economizando tempo de desenvolvimento e mantendo os branches principais sempre em estado deployável. A arquitetura dual-repo (GitLab como repositório principal de desenvolvimento e GitHub como showcase público) mantém proteções simétricas, garantindo que ambos os remotes mantenham os mesmos padrões de qualidade.

## Fluxo Completo

O fluxo de CI/CD representa a jornada completa de um commit desde sua criação local até o merge final no branch develop. Cada etapa adiciona uma camada de validação, criando um sistema de defesa em profundidade onde múltiplos checkpoints garantem que apenas código de alta qualidade seja integrado. Este diagrama mostra todas as camadas de proteção, seus pontos de bloqueio e como elas interagem entre si para criar um pipeline robusto e confiável.

```
┌─────────────────────────────────────────────────────────────────┐
│                     DESENVOLVEDOR                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ git commit
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 1: PRE-COMMIT HOOK (Local)                               │
├─────────────────────────────────────────────────────────────────┤
│ [✓] Ruff (linting)                                              │
│ [✓] Ruff format (formatting)                                    │
│ [✓] Mypy (type checking)                                        │
│ [✓] Pytest (unit + integration + bdd + e2e)                     │
├─────────────────────────────────────────────────────────────────┤
│ PASS → Commit criado                                            │
│ FAIL → Commit BLOQUEADO                                         │
│        Mensagem: "Fix errors before committing"                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ git push origin <branch>
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 2: PRE-PUSH HOOK (Local)                                 │
├─────────────────────────────────────────────────────────────────┤
│ [✓] Pytest (unit + integration + bdd + e2e - suite completa)    │
├─────────────────────────────────────────────────────────────────┤
│ PASS → Push permitido                                           │
│ FAIL → Push BLOQUEADO                                           │
│        Mensagem: "Failed tests: N of M"                         │
│        Instruções de correção                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐ ┌───────────────────┐
        │  GITLAB (origin)  │ │  GITHUB (github)  │
        └───────────────────┘ └───────────────────┘
                    │                   │
                    ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 3: CI/CD REMOTO (Parallel)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ GITLAB CI (.gitlab-ci.yml)     │  GITHUB ACTIONS (ci.yml)       │
│ ─────────────────────────────  │  ───────────────────────       │
│ Stage: test                    │  Jobs: lint, typecheck, test   │
│ - test:unit                    │  - lint: ruff check            │
│ - test:integration             │  - typecheck: mypy             │
│ - test:bdd                     │  - test (matrix):              │
│ - test:e2e                     │    * unit                      │
│ - test:lint                    │    * integration               │
│ - test:typecheck               │    * bdd                       │
│                                │    * e2e                       │
│ Stage: build                   │                                │
│ - build:docs                   │  Parallel execution            │
│                                │  Runs on: ubuntu-latest        │
│ Parallel execution             │  Python: 3.13                  │
│ Image: python:3.13             │                                │
├─────────────────────────────────────────────────────────────────┤
│ PASS → Pipeline verde (success)                                 │
│ FAIL → Pipeline vermelha (failed)                               │
│        Email notification enviado                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Criar MR/PR
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 4: BRANCH PROTECTION (Remote)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ GITLAB (develop branch)        │  GITHUB (develop branch)       │
│ ────────────────────────       │  ─────────────────────         │
│ [✓] Push access: No one        │  [✓] Required status checks:   │
│ [✓] Merge access: Maintainers  │     - lint                     │
│ [✓] Pipeline must succeed      │     - test (unit)              │
│ [✓] Force push: Disabled       │     - test (integration)       │
│                                │     - test (bdd)               │
│ Protection level: MAXIMUM      │     - test (e2e)               │
│                                │     - typecheck                │
│                                │                                │
│                                │  [✓] Branch must be up-to-date │
│                                │  [✓] Force push: Disabled      │
│                                │                                │
│                                │  Protection level: MAXIMUM     │
├─────────────────────────────────────────────────────────────────┤
│ PASS → Merge button ENABLED                                     │
│ FAIL → Merge button DISABLED                                    │
│        Status: "Pipeline must succeed"                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Merge (squash)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DEVELOP BRANCH                             │
│                   (Código de qualidade)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Camada 1: Pre-Commit Hook

A primeira linha de defesa é o hook pre-commit, que executa automaticamente antes de cada commit ser criado localmente. Esta camada é crucial porque fornece feedback imediato ao desenvolvedor enquanto o contexto do código ainda está fresco em sua mente. O hook executa quatro verificações essenciais: linting com Ruff para detectar problemas de estilo e anti-patterns, formatação automática para manter consistência visual, type checking com Mypy para validar anotações de tipo, e a suite completa de 873 testes (696 unit + 83 integration + 52 bdd + 42 e2e) para garantir que nenhuma funcionalidade foi quebrada. Se qualquer verificação falhar, o commit é bloqueado completamente e o desenvolvedor recebe mensagens claras sobre o que precisa ser corrigido.

## Camada 2: Pre-Push Hook

O hook pre-push adiciona uma segunda camada de proteção local, executando imediatamente antes do código ser enviado para os repositórios remotos. Esta camada executa novamente a suite completa de 873 testes, garantindo que mudanças incrementais desde o último commit não introduziram regressões. O custo de 13-15 segundos de execução local é insignificante comparado ao tempo que seria perdido se testes falhassem no CI remoto.

## Camada 3: CI/CD Remoto

As pipelines remotas no GitLab CI e GitHub Actions executam os mesmos 873 testes mas separados por tipo para melhor rastreabilidade de falhas. A execução paralela mantém o tempo total em aproximadamente 1m30s: unit tests (~1m10s), integration tests (~1m15s), bdd tests (~1m17s), e2e tests (~1m16s) rodando simultaneamente. Ambas as plataformas executam identicamente mas GitLab CI é a fonte de verdade enquanto GitHub Actions valida o showcase público.

## Camada 4: Branch Protection

A proteção de branch é a camada final implementada nas plataformas Git. GitLab bloqueia push direto e exige pipeline success. GitHub exige todos os checks individuais (lint, typecheck, unit, integration, bdd, e2e) verdes antes de permitir merge. Esta granularidade no GitHub permite ver exatamente qual tipo de teste falhou sem abrir logs.

## Matriz de Bloqueios

| Etapa             | Trigger        | Bloqueia       | Testes Executados  | Bypass Possível |
| ----------------- | -------------- | -------------- | ------------------ | --------------- |
| Pre-commit        | `git commit`   | SIM (local)    | 873 (all)          | `--no-verify`   |
| Pre-push          | `git push`     | SIM (local)    | 873 (all)          | `--no-verify`   |
| GitLab CI         | Push to remote | NÃO (só marca) | 873 (split 4 jobs) | N/A             |
| GitHub Actions    | Push/PR        | NÃO (só marca) | 873 (matrix 4x)    | N/A             |
| Branch Protection | Merge MR/PR    | SIM (remoto)   | N/A                | Admin only      |

## Tempos de Execução

| Etapa                               | Duração Aproximada | Testes             |
| ----------------------------------- | ------------------ | ------------------ |
| Pre-commit                          | 13-15s             | 873 tests (serial) |
| Pre-push                            | 13-15s             | 873 tests (serial) |
| GitLab CI - test:unit               | 1m 10s             | 696 tests          |
| GitLab CI - test:integration        | 1m 15s             | 83 tests           |
| GitLab CI - test:bdd                | 1m 17s             | 52 tests           |
| GitLab CI - test:e2e                | 1m 16s             | 42 tests           |
| GitHub Actions - test (unit)        | 1m 10s             | 696 tests          |
| GitHub Actions - test (integration) | 1m 15s             | 83 tests           |
| GitHub Actions - test (bdd)         | 1m 17s             | 52 tests           |
| GitHub Actions - test (e2e)         | 1m 16s             | 42 tests           |
| **Total (local → merge)**           | ~3min 30s          | 873 tests          |

## Cobertura de Testes

```
test:unit         → 696 tests → 79.7% da suite
test:integration  →  83 tests →  9.5% da suite
test:bdd          →  52 tests →  6.0% da suite
test:e2e          →  42 tests →  4.8% da suite
─────────────────────────────────────────────
TOTAL             → 873 tests → Cobertura: 76%
```

## Mensagens de Erro

### Pre-commit FAIL

```
[BLOCKED] Commit not allowed!
Failed checks: ruff, pytest

Fix errors and try again:
  1. Run: pytest tests/ -v
  2. Fix failing tests
  3. Try commit again
```

### Pre-push FAIL

```
========================================
[BLOCKED] Push not allowed!
========================================

Failed tests: 2 of 873

Fix errors and try again:
  1. Run: pytest tests/ -v
  2. Fix failing tests
  3. Commit fixes
  4. Try push again

To bypass (NOT recommended):
  git push --no-verify
```

### GitLab Pipeline FAIL

```
Email: "Pipeline #XXXXXX failed"

Merge Request UI:
┌──────────────────────────────────────┐
│ [!] Merge blocked: 1 check failed    │
│                                      │
│ [×] Pipeline must succeed            │
│                                      │
│ [ Merge ] (button disabled)          │
└──────────────────────────────────────┘
```

### GitHub Actions FAIL

```
Pull Request UI:
┌──────────────────────────────────────┐
│ Some checks were not successful      │
│                                      │
│ [×] test (unit) - Required           │
│ [✓] test (integration) - Required    │
│ [✓] test (bdd) - Required            │
│ [✓] test (e2e) - Required            │
│ [✓] lint - Required                  │
│ [✓] typecheck - Required             │
│                                      │
│ [ Merge pull request ] (disabled)    │
└──────────────────────────────────────┘
```

## Estratégia de Bypass

### Local (Pre-commit/Pre-push)

```bash
# NÃO RECOMENDADO - Apenas para emergências
git commit --no-verify
git push --no-verify
```

### Remoto (CI/CD)

- Impossível bypassar
- Pipeline DEVE passar
- Único caminho: corrigir código

### Branch Protection

- Apenas admin pode desabilitar
- Requer acesso de Maintainer mínimo
- Log de auditoria registra mudanças

## Filosofia

1. **Falhar cedo, falhar localmente** → Pre-commit/Pre-push (13-15s)
2. **Validação redundante** → CI/CD remoto confirma (~1m30s)
3. **Proteção final** → Branch protection impede merge
4. **Custo zero no remoto** → 99% problemas detectados localmente

## Configuração Dual-Repo

GitLab (Primary) e GitHub (Showcase) mantêm MESMA proteção:

- Ambos exigem pipeline verde para merge
- Ambos bloqueiam push direto para develop
- GitHub requer 6 status checks separados (lint, typecheck, 4x test)
- GitLab agrupa em 7 jobs mas valida mesmos 873 testes
- Simetria garante qualidade em ambos

## Manutenção

### Arquivos de Configuração

```
.pre-commit-config.yaml       → Hooks locais
.gitlab-ci.yml                → Pipeline GitLab (7 jobs)
.github/workflows/ci.yml      → GitHub Actions (6 checks)
scripts/pre-push-tests.sh     → Script de teste pre-push
.git/hooks/pre-commit         → Hook gerado por pre-commit
.git/hooks/pre-push           → Hook gerado por pre-commit
.git/hooks/post-commit        → Lembrete pós-commit
.git/hooks/pre-push.legacy    → Lembrete pré-push (legado)
```

### Atualizar Configurações

```bash
# Reinstalar hooks após mudanças
pre-commit install --hook-type pre-commit --hook-type pre-push

# Testar localmente
pre-commit run --all-files

# Validar CI/CD
./scripts/test-cicd.sh
```

---

**Versão:** 1.0

**Última atualização:** 2026-02-02
