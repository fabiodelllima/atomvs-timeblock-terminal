# Processo de Desenvolvimento

**Versão:** 2.0.0

**Data:** 8 de Fevereiro de 2026

**Status:** Consolidado (SSOT)

**Alinhado com:** architecture.md v3.0.0, business-rules.md v4.0.0, quality-metrics.md v2.2.0

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Engenharia de Requisitos](#2-engenharia-de-requisitos)
3. [Vertical Slicing](#3-vertical-slicing)
4. [Especificação de Requisitos](#4-especificação-de-requisitos)
5. [Validação de Requisitos (BDD)](#5-validação-de-requisitos-bdd)
6. [Verificação (TDD)](#6-verificação-tdd)
7. [Estrutura de Testes](#7-estrutura-de-testes)
8. [Padrões de Qualidade](#8-padrões-de-qualidade)
9. [Git Workflow](#9-git-workflow)
10. [Gestão de Sprints](#10-gestão-de-sprints)
11. [Referências](#11-referências)

---

## 1. Visão Geral

O processo de desenvolvimento do ATOMVS segue técnicas formais de Engenharia de Requisitos conforme ISO/IEC/IEEE 29148:2018 e SWEBOK v4.0. O ciclo de desenvolvimento mapeia diretamente para o ciclo clássico da disciplina: elicitação e especificação de requisitos, validação com stakeholders, verificação por testes automatizados e implementação guiada por requisitos verificados. Esta cadeia de rastreabilidade garante que cada linha de código tenha justificativa formal e que nenhuma funcionalidade exista sem validação automatizada.

O projeto adota Vertical Slicing como unidade de trabalho: cada business rule é implementada completamente (especificação, cenário de validação, testes de verificação, código) antes de iniciar a próxima. Esta abordagem, combinada com WIP limits rigorosos, previne trabalho parcialmente concluído e mantém o sistema sempre em estado deployável.

### Práticas Adotadas

| Prática           | Origem                  | Aplicação no Projeto        |
| ----------------- | ----------------------- | --------------------------- |
| Vertical Slicing  | Agile                   | Uma BR completa por vez     |
| Especificação     | ISO/IEC/IEEE 29148:2018 | BRs formalizadas primeiro   |
| Validação (BDD)   | Dan North (2006)        | pytest-bdd com Gherkin      |
| Verificação (TDD) | Robert Martin (2003)    | 3 Leis rigorosas            |
| Sprints           | Scrum                   | Iterações 1-2 semanas       |
| WIP Limits        | Kanban/Lean             | Max 2 itens In Progress     |
| Atomic Commits    | Git Best Practices      | 1 commit = 1 mudança lógica |

---

## 2. Engenharia de Requisitos

O projeto adota técnicas de Engenharia de Requisitos como princípio organizador central do processo de desenvolvimento. Cada fase do ciclo produz artefatos que são pré-requisito da fase seguinte, criando uma cadeia de dependências onde violações são detectáveis e rastreáveis. A direção é sempre descendente: especificação informa validação, validação informa verificação, verificação informa implementação. Nunca o inverso.

```
┌─────────────────────────────────────────────────────────────────┐
|         1. ESPECIFICAÇÃO DE REQUISITOS                          |
|    docs/core/business-rules.md                                  |
|    - Business Rules formalizadas (BR-DOMAIN-XXX)                |
|    - Requisitos funcionais rastreáveis                          |
|    - Critérios de aceitação verificáveis                        |
|    Ref: ISO/IEC/IEEE 29148:2018 (Requirements Specification)    |
└─────────────────────────────────────────────────────────────────┘
                          |
                          v
┌─────────────────────────────────────────────────────────────────┐
|         2. VALIDAÇÃO DE REQUISITOS (BDD)                        |
|    tests/bdd/features/                                          |
|    - Cenários em formato Gherkin (DADO/QUANDO/ENTÃO)            |
|    - Stakeholder requirements verification                      |
|    - Documentação executável                                    |
|    Ref: SWEBOK v4.0 Ch.1 (Requirements Validation)              |
└─────────────────────────────────────────────────────────────────┘
                          |
                          v
┌─────────────────────────────────────────────────────────────────┐
|         3. VERIFICAÇÃO (TDD)                                    |
|    tests/unit/         -> Validam BRs isoladamente              |
|    tests/integration/  -> Validam workflows                     |
|    tests/e2e/          -> Validam experiência completa          |
|    Ref: SWEBOK v4.0 Ch.10 (Software Testing)                    |
└─────────────────────────────────────────────────────────────────┘
                          |
                          v
┌─────────────────────────────────────────────────────────────────┐
|         4. IMPLEMENTAÇÃO                                        |
|    src/timeblock/services/  -> Lógica de negócio                |
|    src/timeblock/commands/  -> Interface CLI                    |
|    src/timeblock/tui/       -> Interface TUI                    |
└─────────────────────────────────────────────────────────────────┘
```

**Princípio fundamental:** quando um teste falha, o código está errado, não o teste. Testes validam business rules que são requisitos formais do sistema. Se um teste precisa mudar, a business rule correspondente deve ser alterada primeiro na especificação.

### Mapeamento para Engenharia de Requisitos

| Fase do Ciclo      | Atividade RE (29148)              | Artefato no Projeto                |
| ------------------ | --------------------------------- | ---------------------------------- |
| Especificação      | Elicitação e especificação formal | BR-DOMAIN-XXX em business-rules.md |
| Validação          | Stakeholder requirements verify.  | Cenários Gherkin (.feature)        |
| Verificação        | Software verification             | Testes unit/integ/e2e              |
| Implementação      | Software construction             | Código em src/timeblock/           |
| Rastreabilidade    | Requirements traceability         | Matriz BR -> Test -> Code          |
| Gestão de mudanças | Requirements change management    | ADRs em docs/decisions/            |

---

## 3. Vertical Slicing

Vertical Slicing significa implementar uma business rule por completo, atravessando todas as camadas da aplicação, antes de iniciar a próxima. Este approach contrasta com horizontal slicing (implementar toda a camada de dados, depois toda a camada de serviço, etc.) que tende a produzir código desconectado e dificulta validação incremental.

Cada vertical slice segue um fluxo de 7 etapas:

```
┌──────────────────────────────────────────────────────────────┐
|                  VERTICAL SLICE (1 BR)                       |
├──────────────────────────────────────────────────────────────┤
|  1. Especificar BR (docs/core/business-rules.md)             |
|  2. Escrever cenário de validação (.feature)                 |
|  3. Implementar steps (step_defs/)                           |
|  4. Criar teste de verificação (RED)                         |
|  5. Implementar código (GREEN)                               |
|  6. Refatorar                                                |
|  7. Commit                                                   |
├──────────────────────────────────────────────────────────────┤
│  [OK] BR completa ──> Próxima BR                             │
└──────────────────────────────────────────────────────────────┘
```

**WIP Limits:** Para prevenir acúmulo de trabalho parcial, o projeto opera com limites rigorosos de work-in-progress.

| Coluna         | Limite     |
| -------------- | ---------- |
| Backlog        | Sem limite |
| Sprint Backlog | 5-10       |
| In Progress    | 1-2        |
| Code Review    | 2-3        |
| Done           | Sem limite |

O limite de 1-2 itens In Progress é deliberadamente restritivo. Com um desenvolvedor solo, context switching entre múltiplas BRs desperdiça tempo e aumenta risco de inconsistências.

---

## 4. Especificação de Requisitos

Toda business rule é formalmente especificada antes de qualquer código ou teste ser escrito. A especificação funciona como contrato entre requisitos e implementação, seguindo princípios de rastreabilidade da ISO/IEC/IEEE 29148:2018. Cada requisito é univocamente identificável, verificável e rastreável até a implementação.

### Formato de Business Rule

Cada BR segue o padrão `BR-DOMAIN-XXX` com estrutura fixa:

- **ID:** Identificador único (ex: BR-HABIT-003)
- **Título:** Descrição concisa em português
- **Descrição:** Comportamento esperado detalhado
- **Critérios de aceitação:** Condições verificáveis
- **Referência de implementação:** Classe/método que implementa
- **Referência de teste:** Classe/método que valida

### Localização e Índice

As business rules residem em `docs/core/business-rules.md` organizadas por domínio. Cada domínio tem sua seção com tabela de regras seguida de descrições detalhadas. O documento é versionado independentemente e atualizado antes de qualquer implementação.

### Validação de Existência

Antes de iniciar implementação de qualquer funcionalidade:

```bash
# Verificar se BR existe
grep -r "BR-HABIT-003" docs/core/business-rules.md

# Se não existir: PARE. Especifique primeiro.
```

---

## 5. Validação de Requisitos (BDD)

Os cenários BDD traduzem business rules em especificações executáveis usando o formato Gherkin com verbos em português (DADO/QUANDO/ENTÃO). Esta fase corresponde à validação de requisitos no ciclo de engenharia de requisitos: confirmar que os requisitos fazem sentido e expressam corretamente a intenção do sistema antes de implementar. A norma ISO/IEC/IEEE 29148 chama isso de "stakeholder requirements verification".

### Formato Gherkin

```gherkin
Funcionalidade: Gerenciamento de Hábitos
  Como usuário do ATOMVS
  Eu quero gerenciar meus hábitos
  Para manter consistência na minha rotina

  Cenário: Criar hábito com horários válidos
    Dado que existe uma rotina ativa "Rotina Matinal"
    Quando eu crio um hábito "Meditação" das "06:00" às "06:30"
    Então o hábito deve ser criado com sucesso
    E instâncias devem ser geradas para os dias de recorrência
```

### Estrutura de Diretórios

```
tests/bdd/
├── features/            # Arquivos .feature (Gherkin)
│   ├── habit.feature
│   ├── routine.feature
│   └── timer.feature
└── step_defs/           # Steps Python (pytest-bdd)
    ├── conftest.py
    ├── test_habit_steps.py
    └── test_routine_steps.py
```

### Relação com Business Rules

Cada cenário BDD referencia explicitamente a BR que valida, mantendo rastreabilidade bidirecional. Um cenário BDD pode cobrir uma ou mais BRs, mas toda BR com comportamento observável deve ter pelo menos um cenário BDD associado.

---

## 6. Verificação (TDD)

O projeto adota Strict TDD conforme formalizado por Robert C. Martin, com as três leis aplicadas sem exceção. No contexto da engenharia de requisitos, esta fase corresponde à verificação: garantir que a implementação atende ao requisito especificado. O padrão de nomenclatura `test_br_*` cria uma matriz de rastreabilidade bidirecional entre requisitos e verificação.

### As 3 Leis do Strict TDD

1. Não escreva código de produção exceto para passar um teste que falha
2. Não escreva mais de um teste que seja suficiente para falhar
3. Não escreva mais código do que o suficiente para passar o teste

### Ciclo RED → GREEN → REFACTOR

O ciclo TDD opera em iterações curtas (minutos, não horas):

**RED:** Escrever um teste que falha. O teste deve ser o mais simples possível, validando exatamente um aspecto da BR. Executar e confirmar que falha pela razão esperada (não por erro de sintaxe ou import).

**GREEN:** Escrever a quantidade mínima de código para o teste passar. Resistir à tentação de implementar funcionalidade adicional. Se o teste pede que uma função retorne True para input X, retornar True literalmente é válido nesta fase.

**REFACTOR:** Com todos os testes verdes, refatorar código de produção e testes para eliminar duplicação, melhorar nomes e simplificar estrutura. Executar testes após cada alteração para garantir que permaneçam verdes.

### Naming Convention (ADR-019)

Testes seguem padrão que referencia diretamente a BR validada:

- **Classe:** `TestBRDomainXXX` (ex: `TestBRHabit003`)
- **Método:** `test_br_domain_xxx_cenário` (ex: `test_br_habit_003_validates_time_range`)
- **Docstring:** Referência à BR e descrição do cenário

```python
class TestBRHabit003:
    """BR-HABIT-003: Horário de início deve ser anterior ao horário de fim."""

    def test_br_habit_003_rejects_end_before_start(self, session):
        """Rejeita criação quando end_time < start_time."""
        with pytest.raises(ValueError, match="end_time must be after start_time"):
            HabitService(session).create(
                title="Meditação",
                start_time=time(8, 0),
                end_time=time(7, 0),
                routine_id=1,
            )
```

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
| Requisito (BR)     | docs/core/business-rules.md | BR-DOMAIN-XXX               |
| Validação (BDD)    | tests/bdd/features/         | Gherkin (DADO/QUANDO/ENTÃO) |
| Verificação (Unit) | tests/unit/test_services/   | TestBRDomainXXX             |
| Implementação      | src/timeblock/services/     | Método no service           |

**Verificação rápida:**

```bash
# BR especificada?
grep -r "BR-HABIT-003" docs/core/business-rules.md

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
main          ─────────────────────────────────── produção
                    ↑ merge (squash)
develop       ───────────────────────────────── integração
               ↗ ↑ merge (squash)
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

O projeto utiliza squash merge via MR/PR para integrar feature branches em develop. Squash merge condensa todos os commits de uma branch em um único commit no destino, mantendo o histórico de develop linear e legível. O comando padrão é `glab mr merge <number> --squash --yes` no GitLab.

### Tags e Releases

Tags anotadas marcam releases no branch main:

```bash
git tag -a v1.7.0 -m "v1.7.0: TUI com Textual"
git push origin main --tags
```

### Dual-Repo

O GitLab é fonte de verdade para desenvolvimento. O GitHub é showcase público sincronizado automaticamente via CI/CD. Detalhes completos em `docs/core/cicd-flow.md`.

---

## 10. Gestão de Sprints

Sprints organizam o trabalho em iterações de 1-2 semanas com escopo definido e critérios de aceitação claros. O planejamento ativo reside em `docs/core/sprints.md` enquanto sprints concluídos são arquivados em `docs/core/sprints-archive.md`.

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

## 11. Referências

### Documentos Internos

| Documento          | Conteúdo                | Localização                  |
| ------------------ | ----------------------- | ---------------------------- |
| architecture.md    | Camadas, stack, modelos | docs/core/architecture.md    |
| business-rules.md  | 60 BRs formalizadas     | docs/core/business-rules.md  |
| quality-metrics.md | Métricas e histórico    | docs/core/quality-metrics.md |
| cicd-flow.md       | Pipeline e automação    | docs/core/cicd-flow.md       |
| sprints.md         | Planejamento ativo      | docs/core/sprints.md         |
| sprints-archive.md | Histórico de sprints    | docs/core/sprints-archive.md |

### ADRs Relacionadas

| ADR     | Título                                 |
| ------- | -------------------------------------- |
| ADR-019 | Test Naming Convention (BR-\* pattern) |
| ADR-025 | Engenharia de Requisitos               |
| ADR-026 | Test Database Isolation Strategy       |
| ADR-031 | TUI Implementation                     |

### Referências Externas

| Recurso                  | Autor/Org           | Relevância                  |
| ------------------------ | ------------------- | --------------------------- |
| ISO/IEC/IEEE 29148:2018  | ISO/IEC/IEEE        | Especificação de requisitos |
| SWEBOK v4.0              | IEEE                | Corpo de conhecimento SE    |
| Clean Code (2008)        | Robert C. Martin    | 3 Leis do TDD               |
| BDD in Action (2014)     | John Ferguson Smart | Gherkin, cenários BDD       |
| Specification by Example | Gojko Adzic         | Especificação executável    |
| ISO/IEC 12207:2017       | ISO/IEC             | Processos de ciclo de vida  |

---

**Versão do documento:** 2.0.0

**Última atualização:** 8 de Fevereiro de 2026
