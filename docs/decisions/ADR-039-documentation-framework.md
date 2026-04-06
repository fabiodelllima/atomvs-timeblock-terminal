# ADR-039: Framework de Documentação e Reestruturação

- **Status:** Aceito
- **Data:** 2026-03-16

---

## Contexto

O projeto acumula 12 documentos em `docs/core/`, 38 ADRs em `docs/decisions/`, 16 diagramas, mockups TUI e artefatos de system design. Os documentos foram criados organicamente ao longo de 5 sprints sem um framework formal de documentação — cada um segue convenções implícitas (SSOT versionado, headers em português, referências ABNT) sem uma referência declarada sobre como organizar, classificar e escrever documentação técnica.

Problemas concretos que motivam a reestruturação:

1. **business-rules.md (3703 linhas)** — monólito com 16 domínios num único arquivo. Difícil de navegar, editar e manter. Patches de `sed` e scripts Python frequentemente colidem em edições simultâneas.

2. **development.md (550 linhas)** — mistura fundamentação conceitual ("por que usamos BDD", referências acadêmicas) com instruções práticas ("como rodar testes", "como fazer commit"). Leitor que busca um how-to precisa filtrar teoria; leitor que busca entendimento profundo precisa filtrar comandos.

3. **Pasta `docs/core/` como saco de gatos** — contém SSOTs de referência (business-rules, technical-debt), guias práticos (workflows, ci-optimization), documentação conceitual (architecture), referência de API (cli-reference) e tracking operacional (sprints, roadmap, quality-metrics). Não há distinção de propósito.

4. **Artefatos descartáveis misturados com SSOTs** — `docs/tui/` contém mockups v1 a v4 (histórico iterativo) ao lado de specs ativas. `docs/sysdesign/` contém comparativos before/after, cópias duplicadas e um `pending.md`.

5. **Ausência de onboarding** — nenhum documento tutorial para um novo desenvolvedor (ou agente autônomo) começar a contribuir.

6. **Ausência de framework declarado** — o ADR-027 definiu tooling (MkDocs Material) mas não framework de organização de conteúdo nem estilo de escrita.

---

## Decisão

### Estado atual: modularidade implícita

Uma varredura dos 12 documentos em `docs/core/` revela que 9 já seguem o princípio de modularidade — cada arquivo pertence a exatamente um tipo de conteúdo, sem mistura. O `cli-reference.md` é referência pura (tabelas de comandos e parâmetros). O `workflows.md`, `cicd-flow.md` e `ci-optimization.md` são procedurais puros (passo a passo). O `technical-debt.md`, `quality-metrics.md`, `sprints.md`, `sprints-archive.md` e `roadmap.md` são referência factual de consulta. Os 38 ADRs são conceituais (contexto, decisão, consequências).

Os 3 documentos que violam o princípio são: `business-rules.md` (monólito de 3703 linhas com 16 domínios — deveria ser N módulos de referência), `development.md` (mistura fundamentação conceitual com instruções práticas), e `architecture.md` (mistura conceito com referência). O `mkdocs.yml` já exerce o papel de assembly, compondo módulos individuais numa estrutura de navegação.

A reestruturação, portanto, não é adoção de um framework novo do zero — é formalização do que já se pratica e correção dos 3 desvios.

### Frameworks adotados

**Diátaxis (Procida)** como framework primário de organização de conteúdo. Define quatro categorias baseadas na intenção do leitor: Tutorials (aprender fazendo), Guides (resolver problemas), Reference (consulta factual), Explanation (entender conceitos). Cada documento pertence a exatamente uma categoria. Diátaxis formaliza a separação que 9 dos 12 documentos core já praticam implicitamente.

**Red Hat Modular Documentation** como referência complementar para o princípio de modularidade. Define três tipos de módulo — concept (o que é X), procedure (como fazer Y), reference (tabela/consulta de Z) — cada um autocontido e composto em documentos maiores via assemblies. O projeto já aplica esse modelo: o `cli-reference.md` é um módulo reference, os ADRs são módulos concept, o `workflows.md` é procedure. A quebra planejada do `business-rules.md` em 12 arquivos com `index.md` é diretamente o padrão module + assembly da Red Hat. A distinção tutorial vs. procedure do Diátaxis (ausente na Red Hat) é preservada porque o projeto necessita de onboarding guiado distinto de how-tos pontuais.

**arc42 (Starke; Hruschka)** como template de documentação de arquitetura. As 12 seções do arc42 organizam a documentação técnica do sistema. O projeto já segue parcialmente o arc42: os ADRs correspondem à seção 9, o `technical-debt.md` à seção 11, os diagramas C4 às seções 5-7. A reestruturação alinha explicitamente o `architecture.md` com as seções 1-8.

**Google Developer Documentation Style Guide** como referência de estilo editorial, adaptado para português brasileiro conforme User Preferences do projeto (accentuação, ABNT, tom, formatação). Complementa as convenções de estilo já definidas no ADR-018 (Language Standards). A contribuição específica é a disciplina de clareza, legibilidade e consistência terminológica — aplicável independente do idioma.

**ISO/IEC/IEEE 26514:2022** e **ISO/IEC/IEEE 15289:2019** como referências acadêmicas para processos de desenvolvimento de informação para usuários, alinhadas com as ISO 29148:2018 e ISO 12207:2017 já adotadas pelo projeto. A 15289 define tipos de artefato de informação por processo de ciclo de vida — complementa o mapeamento de documentos existentes.

### Regra prática derivada

Cada arquivo de documentação pertence a exatamente uma categoria Diátaxis (tutorial, guide, reference, explanation) e é autocontido o suficiente para ser lido isoladamente. Documentos compostos usam um `index.md` como assembly que referencia os módulos individuais. Essa regra unifica Diátaxis (categorização por intent) com Red Hat (modularidade e composição).

### Estrutura-alvo

```plaintext
├── tutorials/                    # Diátaxis: aprendizado guiado
│   └── getting-started.md        # [NOVO] Onboarding de desenvolvedor
│
├── guides/                       # Diátaxis: how-to práticos
│   ├── testing-patterns.md       # [MOVE de core/] Padrões de fixtures e testes
│   ├── development-workflow.md   # [EXTRAIR de core/development.md] Seções 7-10
│   ├── ci-optimization.md        # [MOVE de core/]
│   └── cicd-flow.md              # [MOVE de core/]
│
├── reference/                    # Diátaxis: consulta factual
│   ├── business-rules/           # [QUEBRAR core/business-rules.md]
│   │   ├── index.md              # Introdução + índice de domínios
│   │   ├── br-routine.md         # Seção 3
│   │   ├── br-habit.md           # Seção 4
│   │   ├── br-habitinstance.md   # Seção 5
│   │   ├── br-skip.md            # Seção 6
│   │   ├── br-streak.md          # Seção 7
│   │   ├── br-task.md            # Seção 8
│   │   ├── br-timer.md           # Seção 9
│   │   ├── br-event.md           # Seção 10
│   │   ├── br-tui.md             # Seção 14
│   │   ├── br-data.md            # Seção 15
│   │   └── br-testing.md         # Seção 16
│   ├── cli-reference.md          # [MOVE de core/] Fica intacto
│   ├── technical-debt.md         # [MOVE de core/] Fica intacto
│   ├── quality-metrics.md        # [MOVE de core/] Fica intacto
│   ├── workflows.md              # [MOVE de core/] Fica intacto
│   ├── sprints.md                # [MOVE de core/] Fica intacto
│   ├── sprints-archive.md        # [MOVE de core/] Fica intacto
│   └── roadmap.md                # [MOVE de core/] Fica intacto
│
├── explanation/                  # Diátaxis: entendimento conceitual
│   ├── architecture.md           # [MOVE de core/] Alinhado com arc42 §1-8
│   ├── development-methodology.md # [EXTRAIR de core/development.md] Seções 1-6
│   └── domain-concepts.md        # [EXTRAIR de core/business-rules.md] Seções 1-2
│
├── decisions/                    # arc42 §9 — já existe, fica no lugar
│   ├── ADR-001..039.md
│   └── archived/
│
├── diagrams/                     # arc42 §5-7 (C4, sequences, states) — fica no lugar
│   ├── c4-model/
│   ├── sequences/
│   ├── states/
│   ├── activity/
│   ├── data/
│   └── infrastructure/
│
├── sysdesign/                    # arc42 views detalhadas — avaliar limpeza
│   ├── box-drawing/
│   ├── first-loop.md
│   └── pending.md
│
└── tui/                          # Specs e mockups da TUI — avaliar arquivamento
    ├── color-system.md           # Ativo (referência)
    ├── dashboard-cards-spec.md   # Ativo (referência)
    └── archive/                  # [NOVO] Mockups v1-v3 arquivados
        ├── dashboard-mockup-v1.md
        ├── dashboard-mockup-v2.md
        └── dashboard-mockup-v3.md
```

### Classificação de cada documento existente

#### Ficam intactos (SSOT, só mudam de pasta)

| Documento               | Linhas | De    | Para        | Justificativa                            |
| ----------------------- | ------ | ----- | ----------- | ---------------------------------------- |
| technical-debt.md       | 430    | core/ | reference/  | Tracking operacional, referência factual |
| cli-reference.md        | 2529   | core/ | reference/  | Referência de API, consulta pura         |
| quality-metrics.md      | 268    | core/ | reference/  | Métricas factuais                        |
| workflows.md            | 2024   | core/ | reference/  | Fluxos documentados, consulta            |
| sprints.md              | 587    | core/ | reference/  | Tracking de sprints                      |
| sprints-archive.md      | 159    | core/ | reference/  | Histórico                                |
| roadmap.md              | 286    | core/ | reference/  | Planejamento factual                     |
| testing-patterns.md     | ~200   | core/ | guides/     | How-to prático                           |
| ci-optimization.md      | 203    | core/ | guides/     | How-to de otimização                     |
| cicd-flow.md            | 304    | core/ | guides/     | How-to de CI/CD                          |
| color-system.md         | 550    | tui/  | tui/ (fica) | Referência ativa                         |
| dashboard-cards-spec.md | 587    | tui/  | tui/ (fica) | Spec ativa                               |

#### Precisam ser quebrados

| Documento         | Linhas | Ação                                                                                                                                                                     |
| ----------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| business-rules.md | 3703   | Quebrar em 12 arquivos por domínio em reference/business-rules/ + index. Seções 1-2 (conceitos) vão para explanation/domain-concepts.md                                  |
| development.md    | 550    | Seções 1-6 (conceitual) → explanation/development-methodology.md. Seções 7-10 (prático) → guides/development-workflow.md. Seção 11 (referências) distribuída entre ambos |

#### Precisam de limpeza

| Documento/Pasta                | Ação                                                 |
| ------------------------------ | ---------------------------------------------------- |
| tui/dashboard-mockup-v1..v3.md | Arquivar em tui/archive/ (histórico iterativo)       |
| tui/dashboard-mockup-v4.md     | Manter ativo como versão corrente                    |
| sysdesign/pending.md           | Avaliar: incorporar ao roadmap ou deletar            |
| refactoring-catalog.md         | Mover para guides/ ou explanation/ conforme conteúdo |

#### Novos documentos a criar

| Documento                              | Categoria   | Propósito                                          |
| -------------------------------------- | ----------- | -------------------------------------------------- |
| tutorials/getting-started.md           | Tutorial    | Onboarding: setup, primeiro commit, rodar testes   |
| explanation/domain-concepts.md         | Explanation | Conceitos fundamentais extraídos de business-rules |
| explanation/development-methodology.md | Explanation | Fundamentação teórica extraída de development.md   |
| guides/development-workflow.md         | Guide       | Parte prática extraída de development.md           |
| reference/business-rules/index.md      | Reference   | Índice dos 12 arquivos de BRs por domínio          |

### Atualização do mkdocs.yml

A nav do `mkdocs.yml` será reorganizada para refletir os quadrantes Diátaxis como seções de primeiro nível, substituindo a seção "Core (SSOT)" atual. ADRs e Diagramas permanecem como seções independentes (são transversais).

### Execução incremental

A reestruturação será executada em fases, cada uma numa branch dedicada:

**Fase 1 — Infraestrutura:** criar pastas, mover documentos intactos, atualizar mkdocs.yml. Nenhum conteúdo alterado.

**Fase 2 — Quebra de business-rules.md:** extrair 12 arquivos por domínio + index. Validar cross-references.

**Fase 3 — Quebra de development.md:** extrair methodology + workflow. Atualizar referências cruzadas.

**Fase 4 — Limpeza e novos:** arquivar mockups antigos, deletar duplicatas, criar getting-started.md.

**Fase 5 — Validação:** `mkdocs build` sem warnings, todos os links internos funcionando, grep por referências quebradas.

---

## Consequências

### Positivas

- Cada documento tem propósito declarado (Tutorial, Guide, Reference, Explanation).
- business-rules.md deixa de ser monólito de 3700 linhas — patches cirúrgicos por domínio.
- development.md separado em conceitual e prático — cada leitor encontra o que precisa.
- Onboarding de novos desenvolvedores (e agentes autônomos) com tutorial dedicado.
- Alinhamento com frameworks reconhecidos (Diátaxis, arc42, Google Style Guide).
- mkdocs.yml reflete a organização real, não uma pasta flat.

### Negativas

- Custo de migração: mover 12+ arquivos, atualizar cross-references, atualizar mkdocs.yml.
- Risco de links quebrados durante a transição.
- Período transitório onde README e handoffs referenciam paths antigos.
- business-rules.md quebrado em 12 arquivos exige index consistente para manter a rastreabilidade BR => arquivo.

### Mitigações

- Execução em fases com branch por fase.
- `mkdocs build` como gate de validação em cada fase.
- `grep -rn "docs/core/" .` para encontrar referências ao path antigo.
- Aliases ou redirects no mkdocs para paths movidos.

---

## Referências

- PROCIDA, D. **Diátaxis: A systematic approach to technical documentation authoring.** Disponível em: <https://diataxis.fr/>. Acesso em: 16 mar. 2026.
- STARKE, G.; HRUSCHKA, P. **arc42: Template for software architecture documentation and communication.** Disponível em: <https://arc42.org/>. Acesso em: 16 mar. 2026.
- GOOGLE. **Google developer documentation style guide.** Disponível em: <https://developers.google.com/style>. Acesso em: 16 mar. 2026.
- ISO/IEC/IEEE 26514:2022. **Systems and software engineering — Design and development of information for users.** Geneva: ISO, 2022.
- ISO/IEC/IEEE 15289:2019. **Systems and software engineering — Content of life-cycle information items (documentation).** Geneva: ISO, 2019.
- BROWN, S. **The C4 model for visualising software architecture.** Disponível em: <https://c4model.com/>. Acesso em: 16 mar. 2026.
- RED HAT. **Modular Documentation Reference Guide.** Disponível em: <https://redhat-documentation.github.io/modular-docs/>. Acesso em: 16 mar. 2026.
- RED HAT. **Red Hat Technical Writing Style Guide.** Disponível em: <https://stylepedia.net/style/>. Acesso em: 16 mar. 2026.
- NYGARD, M. Documenting Architecture Decisions. **Cognitect Blog**, 2011. Disponível em: <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions>.
