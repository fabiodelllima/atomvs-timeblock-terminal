# Metodologia de Desenvolvimento

**Versão:** 3.0.0

**Status:** Consolidado (SSOT)

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
| Verificação (TDD) | Beck (2003)             | RED-GREEN-REFACTOR          |
| Sprints           | Scrum                   | Iterações 1-2 semanas       |
| WIP Limits        | Kanban/Lean             | Max 2 itens In Progress     |
| Atomic Commits    | Git Best Practices      | 1 commit = 1 mudança lógica |

---

## 2. Engenharia de Requisitos

O projeto adota técnicas de Engenharia de Requisitos como princípio organizador central do processo de desenvolvimento. Cada fase do ciclo produz artefatos que são pré-requisito da fase seguinte, criando uma cadeia de dependências onde violações são detectáveis e rastreáveis. A direção predominante é descendente: especificação informa validação, validação informa verificação, verificação informa implementação. A flexibilidade está na escolha deliberada da técnica conforme a natureza da regra — não no relaxamento do rigor. O nível de formalismo é maior do que uma hierarquia fixa, porque exige do desenvolvedor a competência de selecionar a técnica apropriada para cada situação.

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
|    - Cenários em formato Gherkin (Given/When/Then)              |
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

Os cenários BDD traduzem business rules em especificações executáveis usando o formato Gherkin em inglês (Given/When/Then), conforme formalizado por Dan North (2006). A escolha do inglês para features segue ADR-018 (Language Standards): código e especificações executáveis em inglês, documentação de projeto em português. Esta fase corresponde à validação de requisitos no ciclo de engenharia de requisitos: confirmar que os requisitos expressam corretamente a intenção do sistema antes de implementar. A norma ISO/IEC/IEEE 29148:2018 chama isso de "stakeholder requirements verification". Estruturalmente, o formato Given/When/Then é uma aplicação do Hoare Triple {P} S {Q} — precondição, comando, pós-condição (HOARE, 1969) — à especificação comportamental em linguagem natural.

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

O projeto adota TDD conforme formalizado por Kent Beck em "Test-Driven Development: By Example" (2003), com o ciclo RED-GREEN-REFACTOR aplicado sem exceção. As "Three Laws of TDD", articuladas posteriormente por Robert C. Martin, operacionalizam o ciclo de Beck em regras prescritivas. No contexto da engenharia de requisitos, esta fase corresponde à verificação: garantir que a implementação atende ao requisito especificado. O padrão de nomenclatura `test_br_*` cria uma matriz de rastreabilidade bidirecional entre requisitos e verificação.

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

| ADR     | Título                                 | Relevância Metodológica         |
| ------- | -------------------------------------- | ------------------------------- |
| ADR-019 | Test Naming Convention (BR-\* pattern) | Rastreabilidade BR -> Test      |
| ADR-025 | Engenharia de Requisitos               | Fundamentação metodológica      |
| ADR-026 | Test Database Isolation Strategy       | Isolamento de fixtures          |
| ADR-031 | TUI Implementation                     | Textual como framework TUI      |
| ADR-033 | Fixture Session Rollback               | join_transaction_mode           |
| ADR-034 | Dashboard-first CRUD                   | Extract Delegate (Fowler)       |
| ADR-035 | Keybindings Standardization            | Padronização de atalhos TUI     |
| ADR-037 | TUI Keybindings Standard               | Mapa definitivo de keybindings  |
| ADR-038 | Dashboard Interaction Patterns         | Modais, undo, fluxos de usuário |

### Referências Externas

As referências abaixo constituem o fundamento teórico do processo de desenvolvimento do projeto. Cada técnica adotada é rastreável a uma fonte primária — padrões internacionais, livros seminais ou artigos fundacionais — que a formaliza como prática de engenharia de software.

**Engenharia de Requisitos**

INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. **ISO/IEC/IEEE 29148:2018 — Systems and software engineering — Life cycle processes — Requirements engineering.** 2. ed. Geneva: ISO, 2018. Padrão internacional que define processos de engenharia de requisitos, itens de informação e guidelines de rastreabilidade. Fundamenta a cadeia BR -> Test -> Code do projeto.

INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. **ISO/IEC/IEEE 12207:2017 — Systems and software engineering — Software life cycle processes.** Geneva: ISO, 2017. Define processos de ciclo de vida de software complementares à ISO 29148.

IEEE COMPUTER SOCIETY. **Guide to the Software Engineering Body of Knowledge (SWEBOK), Version 4.0.** Hironori Washizaki (Ed.). IEEE Computer Society, 2024. Corpo de conhecimento que organiza as 18 Knowledge Areas da engenharia de software. Chapter 1 (Software Requirements) e Chapter 5 (Software Testing) fundamentam as práticas de especificação e verificação do projeto.

**Behavior-Driven Development (BDD)**

NORTH, D. Introducing BDD. **Better Software Magazine**, mar. 2006. Artigo fundacional que formalizou BDD como evolução do TDD, introduzindo a mudança de vocabulário de "testes" para "comportamentos" e o formato Given/When/Then. Fonte primária da prática de BDD adotada no projeto.

HOARE, C. A. R. An Axiomatic Basis for Computer Programming. **Communications of the ACM**, v. 12, n. 10, p. 576-580, Oct. 1969. Artigo seminal que define o Hoare Triple {P} S {Q} (precondição, comando, pós-condição). O formato Given/When/Then do BDD é estruturalmente uma aplicação desta lógica à especificação comportamental em linguagem natural.

SMART, J. F. **BDD in Action: Behavior-Driven Development for the Whole Software Lifecycle.** Shelter Island: Manning, 2014. ISBN 978-1-617-29165-4. Referência prática para implementação de BDD com frameworks como Cucumber e pytest-bdd. Complementa o artigo fundacional de North com patterns de adoção em projetos reais.

ADZIC, G. **Specification by Example: How Successful Teams Deliver the Right Software.** Shelter Island: Manning, 2011. ISBN 978-1-617-29008-4. Descreve como equipes de sucesso usam exemplos concretos como especificações executáveis, convergindo com a prática BDD adotada no projeto.

**Test-Driven Development (TDD)**

BECK, K. **Test-Driven Development: By Example.** Boston: Addison-Wesley, 2003. ISBN 0-321-14653-0. Livro seminal que formaliza o ciclo RED-GREEN-REFACTOR. Fonte primária da prática de TDD adotada no projeto. Define TDD como prática de design, não de teste.

MARTIN, R. C. **Clean Code: A Handbook of Agile Software Craftsmanship.** Upper Saddle River: Prentice Hall, 2008. ISBN 978-0-13-235088-4. Formaliza as "Three Laws of TDD" como regras prescritivas que operacionalizam o ciclo de Beck. As 3 Leis aplicadas no projeto derivam desta formulação.

**Architecture Decision Records (ADRs)**

NYGARD, M. Documenting Architecture Decisions. **Cognitect Blog**, 15 nov. 2011. Blog post que popularizou ADRs como registros curtos, sequenciais e versionados no repositório do projeto. Formato adotado integralmente pelo ATOMVS (38 ADRs documentados).

KEELING, M.; RUNDE, J. Love Unrequited: The Story of Architecture, Agile, and How Architecture Decision Records Brought Them Together. **IEEE Software**, v. 39, n. 4, 2022. Apresenta evidência empírica sobre o impacto de ADRs em projetos reais.

ZDUN, U. et al. Sustainable Architectural Decisions. **IEEE Software**, v. 30, n. 6, p. 46-53, 2013. Define guidelines e o Y-statement format para decisões arquiteturais sustentáveis, base teórica da organização adr.github.io.

**Refactoring e Design**

FOWLER, M. **Refactoring: Improving the Design of Existing Code.** 2. ed. Boston: Addison-Wesley, 2018. ISBN 978-0-13-475759-9. Catálogo de refatorações referenciado nas ADRs do projeto (Extract Delegate, Split Phase). Guia para a fase REFACTOR do ciclo TDD.

HUMBLE, J.; FARLEY, D. **Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation.** Boston: Addison-Wesley, 2010. ISBN 978-0-321-60191-9. Fundamenta as práticas de CI/CD, pipeline como gatekeeper de qualidade e deployment automation do projeto.

FOWLER, M. **Patterns of Enterprise Application Architecture.** Boston: Addison-Wesley, 2002. ISBN 978-0-321-12742-6. Padrões arquiteturais de referência para a camada de serviços e persistência do projeto.

---

**Versão do documento:** 3.0.0

**Última atualização:** 15 de Março de 2026
