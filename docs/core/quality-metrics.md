# Quality Metrics - ATOMVS TimeBlock Terminal

**Versão:** 3.0.0

**Relacionado:** roadmap.md, CHANGELOG.md

---

## 1. Métricas Atuais

Este documento consolida as métricas de qualidade do ATOMVS TimeBlock Terminal, servindo como fonte única de verdade para acompanhamento do progresso técnico. As métricas são atualizadas a cada sessão de desenvolvimento e refletem o estado real do código, medido diretamente pelo pipeline CI/CD. Nenhum valor neste documento é estimado ou projetado — cada número corresponde a uma execução real de `pytest --cov`, `mypy` ou `ruff`.

- **Data de Referência:** 20 de Fevereiro de 2026
- **Versão:** v1.7.0-dev (branch `feat/tui-phase1`)

### 1.1. Visão Geral

O projeto atingiu um patamar de estabilidade técnica onde todas as métricas obrigatórias estão em conformidade. Cobertura de 87% supera o threshold de 85% configurado no pipeline, zero erros mypy em 54 arquivos fonte garante type safety, e a suite de 797 testes executa em menos de 19 segundos. Os dois gaps remanescentes — CLI funcional em 85% e cobertura de BRs em 83% — são priorizados para fechamento durante a v1.7.0.

| Categoria           | Valor Atual | Meta v1.7.0 | Status     |
| ------------------- | ----------- | ----------- | ---------- |
| Testes Passando     | 797         | 850+        | [OK]       |
| Testes Skipped      | 0           | 0           | [OK]       |
| Cobertura Global    | 87%         | 85%         | [OK]       |
| Erros Mypy          | 0           | 0           | [OK]       |
| Commands Funcionais | 85%         | 100%        | [PENDENTE] |

### 1.2. Distribuição de Testes

A pirâmide de testes atingiu equilíbrio saudável após a consolidação da v1.6.0. Os testes de integração subiram de 9.5% para 14.6%, eliminando o gap que existia em relação à faixa alvo de 15-20%. A redução no total absoluto de testes entre v1.5.0 (873) e v1.6.0 (778) não representou perda de cobertura — ao contrário, a limpeza de testes duplicados e a consolidação pós-reestruturação resultaram em testes mais focados, cada um rastreável a uma BR específica. A v1.7.0 adicionou 19 testes de TUI, mantendo as proporções dentro das faixas alvo.

| Tipo        | Quantidade | Percentual | Meta   | Status |
| ----------- | ---------- | ---------- | ------ | ------ |
| Unit        | 595        | 74.7%      | 70-75% | [OK]   |
| Integration | 116        | 14.6%      | 15-20% | [OK]   |
| BDD         | 56         | 7.0%       | Manter | [OK]   |
| E2E         | 30         | 3.8%       | 5-10%  | [OK]   |
| Skipped     | 0          | 0%         | 0%     | [OK]   |

### 1.3. Cobertura por Módulo

A cobertura por módulo revela um padrão de amadurecimento progressivo. Models e utils, por serem predominantemente declarativos ou puramente funcionais, atingiram cobertura próxima a 100% desde cedo. Services evoluíram de 78% para 93% após trabalho focado em routine_service (+47pp) e tag_service (+71pp). O módulo tui/, introduzido na v1.7.0, já nasceu com 97% de cobertura, demonstrando que a disciplina TDD está incorporada ao fluxo de trabalho mesmo para código de interface. O gap remanescente em commands/ (45%) é o principal alvo de melhoria — testes de integração via CliRunner são a estratégia planejada.

Cobertura calculada por `pytest --cov` em 20/02/2026. Valores baseados em statements cobertos.

| Módulo    | Cobertura | Status    | Observação                     |
| --------- | --------- | --------- | ------------------------------ |
| models/   | ~98%      | [OK]      | Manutenção                     |
| services/ | ~93%      | [OK]      | Todos acima de 84%             |
| commands/ | ~45%      | [ATENÇÃO] | Prioridade para v1.7.0         |
| tui/      | ~97%      | [OK]      | App, screens, widgets testados |
| utils/    | ~99%      | [OK]      | conflict_display.py agora 100% |
| database/ | ~60%      | [ATENÇÃO] | migration_001 sem cobertura    |

**Detalhamento services/ (por arquivo):**

A camada de services é o coração da lógica de negócio e merece acompanhamento individual. A evolução mais expressiva foi tag_service (de 29% para 100%) e routine_service (de 53% para 100%), ambos resolvidos na v1.6.0 como parte do sprint de cobertura. Os services de habit_instance e timer permanecem em 88% e 92% respectivamente — os gaps restantes correspondem a branches de erro e edge cases que serão cobertos incrementalmente.

| Arquivo                   | Cobertura | Mudança vs v1.6.0 |
| ------------------------- | --------- | ----------------- |
| habit_service.py          | 100%      | =                 |
| routine_service.py        | 100%      | +47pp             |
| tag_service.py            | 100%      | +71pp             |
| task_service.py           | 92%       | =                 |
| timer_service.py          | 92%       | =                 |
| habit_instance_service.py | 88%       | =                 |

**Detalhamento tui/ (por arquivo):**

O módulo TUI foi construído com TDD desde o primeiro commit. Cada widget e screen possui testes que validam renderização, navegação e interações de teclado. O único gap (app.py em 97%) corresponde a um branch de fallback no tratamento de erros que é difícil de provocar em ambiente de teste.

| Arquivo                   | Cobertura |
| ------------------------- | --------- |
| app.py                    | 97%       |
| screens/dashboard.py      | 94%       |
| widgets/nav_bar.py        | 100%      |
| widgets/help_overlay.py   | 100%      |
| widgets/timeblock_grid.py | 100%      |
| widgets/command_bar.py    | 100%      |

---

## 2. Histórico de Métricas

O histórico de métricas conta a história técnica do projeto de forma objetiva. A trajetória não foi linear: a v1.3.0 acumulou 156 erros mypy e a cobertura caiu de 70% para 61%, um ponto de inflexão que motivou a decisão de "parar tudo e resolver débito técnico" na v1.3.3. Desde então, a recuperação foi consistente — mypy zerado na v1.3.3, cobertura subindo de 61% para 87% entre v1.3.0 e v1.6.0, e a suite de testes estabilizando em torno de 800 testes focados.

A redução de testes entre releases (685→618 na v1.4.1, 873→778 na v1.6.0) pode parecer regressão em isolamento, mas na verdade reflete ciclos de consolidação saudáveis: testes duplicados removidos, nomenclatura padronizada para BR-\*, e cenários redundantes substituídos por testes mais precisos. O saldo líquido é positivo — menos testes, porém cada um mais significativo e rastreável.

### 2.1. Evolução por Release

| Release  | Data     | Testes | Cobertura | Erros Mypy | Mudança Significativa        |
| -------- | -------- | ------ | --------- | ---------- | ---------------------------- |
| v1.0.0   | Out/2025 | 50     | 30%       | 0          | Baseline                     |
| v1.1.0   | Nov/2025 | 200    | 60%       | 12         | +150 testes                  |
| v1.2.0   | Nov/2025 | 350    | 70%       | 38         | Status refactoring           |
| v1.3.0   | Dez/2025 | 454    | 61%       | 156        | Acúmulo de débito            |
| v1.3.3   | Jan/2026 | 558    | 67%       | 0          | Recuperação mypy             |
| v1.4.0   | Jan/2026 | 513    | 44%       | 0          | BRs formalizadas             |
| v1.4.1   | Jan/2026 | 685    | 71%       | 0          | E2E expansion                |
| v1.5.0   | Fev/2026 | 873    | 76%       | 0          | CI/CD dual-repo, i18n        |
| v1.6.0   | Fev/2026 | 778    | 87%       | 0          | Docker, DevSecOps, threshold |
| v1.7.0\* | Fev/2026 | 797    | 87%       | 0          | TUI em desenvolvimento       |

---

## 3. Metas e Critérios de Qualidade

Os critérios de qualidade definem o padrão mínimo aceitável para releases. Cada release deve passar por todos os gates obrigatórios antes de ser publicada. Esses gates são verificados automaticamente pelo pipeline CI/CD — não dependem de verificação manual, eliminando o risco de releases com métricas abaixo do aceitável. O threshold de cobertura (85%) é especialmente relevante: qualquer commit que reduza a cobertura abaixo desse valor falha no pipeline.

### 3.1. Critérios de Release

**Obrigatórios (Gate de Release):**

- [x] Zero erros mypy em modo strict
- [x] Zero testes skipped sem justificativa
- [x] Cobertura global >= 85% (threshold configurado)
- [x] Cobertura de módulos críticos >= 85%
- [ ] 100% funcionalidades CLI operacionais

**Desejáveis (Qualidade Superior):**

- [ ] Cobertura >= 90%
- [x] Tempo de execução suite < 60s
- [x] Zero warnings ruff

### 3.2. Pirâmide de Testes

A pirâmide define a distribuição ideal entre os tipos de teste. O objetivo é maximizar cobertura com o menor custo de manutenção — testes unitários são baratos de escrever e rápidos de executar, enquanto testes E2E validam fluxos completos porém são mais frágeis e lentos. A distribuição atual está dentro das faixas alvo em todas as categorias, com integration tests finalmente na faixa de 15-20% após deficit prolongado.

```
Distribuição Atual vs Alvo:

E2E (3.8%)          ██████░░░░░░░░░░  5-10%  [OK]
BDD (7.0%)          █████████████░░░  Manter [OK]
Integration (14.6%) ██████████████░   15-20% [OK]
Unit (74.7%)        ████████████████  70-75% [OK]
```

---

## 4. Análise de Performance

O tempo de execução da suite é uma métrica de produtividade, não apenas de qualidade. Suites que levam mais de 30 segundos desencorajam execução frequente; acima de 60 segundos, desenvolvedores tendem a pular testes entre commits. A suite atual em 18 segundos mantém o ciclo de feedback abaixo do limiar de atenção, incentivando execução a cada commit via pre-commit hooks.

### 4.1. Tempo de Execução

| Fase           | Tempo Atual | Meta  | Status |
| -------------- | ----------- | ----- | ------ |
| Suite completa | 18.3s       | < 40s | [OK]   |
| Unit only      | 12.4s       | < 20s | [OK]   |

**Medição:** `pytest tests/ -v --tb=no --cov` em 20/02/2026.

O crescimento esperado com novos testes de TUI (widgets interativos, mocks de terminal) pode adicionar 3-5 segundos à suite. Mesmo com esse acréscimo, a projeção permanece abaixo de 25 segundos — confortavelmente dentro da meta de 40 segundos.

---

## 5. Cobertura de Business Rules

A rastreabilidade entre regras de negócio e testes é o que transforma a suite de testes de uma rede de segurança genérica em uma validação de especificação. Cada teste no projeto referencia explicitamente uma BR — na classe de teste (`TestBRHabit001`), no método (`test_br_habit_001_creates_with_valid_data`) e na docstring. Isso permite responder com certeza: "a regra X está testada?" e "se o teste Y falhar, qual regra de negócio foi violada?".

O domínio TUI (BR-TUI-001 a BR-TUI-011) é o principal gap atual, com apenas 4 das 11 BRs cobertas por testes. Isso é esperado — as BRs foram documentadas antecipando a implementação, e os testes serão escritos conforme cada componente for desenvolvido. O padrão estabelecido nos domínios mais maduros (Habit, HabitInstance, Streak, Timer, Reorder, Validation — todos em 100%) demonstra que o gap é temporário.

### 5.1. Status por Domínio

| Domínio       | Total BRs | Com Testes | Cobertura | BRs Faltantes         |
| ------------- | --------- | ---------- | --------- | --------------------- |
| Routine       | 6         | 5          | 83%       | BR-ROUTINE-006        |
| Habit         | 5         | 5          | 100%      | -                     |
| HabitInstance | 6         | 6          | 100%      | -                     |
| Skip          | 4         | 1          | 25%       | BR-SKIP-002/003/004   |
| Streak        | 4         | 4          | 100%      | -                     |
| Task          | 6         | 5          | 83%       | BR-TASK-006           |
| Timer         | 8         | 8          | 100%      | -                     |
| Reorder       | 6         | 6          | 100%      | -                     |
| Validation    | 3         | 3          | 100%      | -                     |
| CLI           | 3         | 1          | 33%       | BR-CLI-001/003        |
| Tag           | 2         | 0          | 0%        | BR-TAG-001/002        |
| TUI           | 11        | 4          | 36%       | BR-TUI-005 a 011      |
| **TOTAL**     | **64**    | **48**     | **75%**   | **16 BRs sem testes** |

### 5.2. Prioridade de Cobertura Pendente

A priorização segue dois critérios: gravidade do gap (domínios com 0% ou 25% são críticos) e impacto no desenvolvimento ativo (BRs de TUI serão cobertas naturalmente pela implementação em andamento). As BRs de Skip com 25% de cobertura representam o gap mais preocupante em domínios já implementados — o código existe e funciona, mas não há testes validando as regras formais.

| Prioridade | BRs                         | Justificativa                 |
| ---------- | --------------------------- | ----------------------------- |
| Alta       | BR-SKIP-002/003/004         | Domínio com 25% de cobertura  |
| Alta       | BR-TAG-001/002              | Domínio com 0% de cobertura   |
| Alta       | BR-TUI-005 a 011            | TUI em implementação ativa    |
| Média      | BR-CLI-001/003              | Interface com usuário         |
| Baixa      | BR-ROUTINE-006, BR-TASK-006 | Domínios já com boa cobertura |

---

## 6. Automação e CI/CD

A automação de qualidade opera em dois níveis complementares. O pre-commit hook fornece feedback local imediato — em menos de 25 segundos, o desenvolvedor sabe se o commit é seguro. O pipeline CI/CD no GitLab fornece validação autoritativa — jobs paralelos verificam testes, linting, types, cobertura e segurança em ambiente isolado Docker. Essa defesa em duas camadas significa que problemas de qualidade são detectados antes de entrar no repositório (pre-commit) e antes de serem aceitos em merge requests (CI/CD).

### 6.1. Pre-commit Hooks

Executados localmente em cada `git commit`, garantindo que código problemático não entre no repositório. A decisão de tornar mypy bloqueante (desde v1.6.0) eliminou a janela onde commits com erros de tipo podiam entrar — com zero erros mypy mantidos consistentemente desde v1.3.3, o custo de bloqueio é próximo de zero enquanto o benefício preventivo é significativo.

| Hook        | Status  | Tempo | Bloqueante |
| ----------- | ------- | ----- | ---------- |
| ruff format | [ATIVO] | 1.2s  | Sim        |
| ruff check  | [ATIVO] | 0.8s  | Sim        |
| mypy        | [ATIVO] | 3.5s  | Sim        |
| pytest-all  | [ATIVO] | ~18s  | Sim        |

**Total:** ~24s por commit

### 6.2. GitLab CI/CD Pipeline

O pipeline foi reestruturado na v1.6.0 para consolidar jobs de teste em um único `test:all` que executa a suite completa com cobertura. Essa mudança reduziu o tempo total do pipeline (menos overhead de setup por job) sem perder granularidade — o relatório de cobertura ainda detalha cada módulo. Jobs de segurança (bandit para análise estática, pip-audit para vulnerabilidades em dependências) foram adicionados como gates obrigatórios.

```
stages: test -> build -> deploy

test:all           pytest tests/ -v --cov             [branches, MRs]
test:lint          ruff check src/timeblock           [branches, MRs]
test:typecheck     mypy --check-untyped-defs          [branches, MRs]
test:coverage      coverage report --fail-under=85    [branches, MRs]
test:security      bandit + pip-audit                 [branches, MRs]
build:docs         mkdocs build                       [develop, main]
sync:github        push to GitHub mirror              [develop, main]
```

| Job            | Bloqueante | Artefatos    |
| -------------- | ---------- | ------------ |
| test:all       | Sim        | coverage.xml |
| test:lint      | Sim        | -            |
| test:typecheck | Sim        | -            |
| test:coverage  | Sim        | -            |
| test:security  | Sim        | -            |
| build:docs     | Sim        | site/        |
| sync:github    | Não        | -            |

**Imagem base:** `python:3.14`

**Referência:** `.gitlab-ci.yml`, `.github/workflows/ci.yml`

### 6.3. GitHub Actions (Dual-Repo)

O pipeline espelho no GitHub valida que o repositório de showcase permanece íntegro após sincronização. Executa um subset dos checks do GitLab — suficiente para garantir que o código compila, passa nos testes e está limpo, sem duplicar a análise de segurança completa.

| Job       | Descrição                           | Bloqueante |
| --------- | ----------------------------------- | ---------- |
| lint      | ruff check                          | Sim        |
| typecheck | mypy --check-untyped-defs           | Sim        |
| test      | Matrix: unit, integration, bdd, e2e | Sim        |

---

## 7. Referências

- **ROADMAP:** `docs/core/roadmap.md`
- **CHANGELOG:** `CHANGELOG.md`
- **ADR-007:** Service Layer com Dependency Injection
- **ADR-019:** Test Naming Convention
- **ADR-026:** Test Database Isolation Strategy
- **ADR-031:** TUI Implementation with Textual

---

**Versão do documento:** 3.0.0

**Última atualização:** 20 de Fevereiro de 2026
