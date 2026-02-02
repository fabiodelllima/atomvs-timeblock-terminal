# Roadmap

**Versão:** 3.0.0

**Status:** Single Source of Truth (SSOT)

**Documentos Relacionados:** architecture.md, business-rules.md, quality-metrics.md, technical-debt.md

---

## Sumário Executivo

TimeBlock Organizer é uma aplicação CLI para gerenciamento de tempo baseada em Time Blocking e nos princípios de Atomic Habits. A arquitetura segue o modelo offline-first, priorizando funcionalidade completa sem dependência de rede, com evolução planejada para API REST (v2.x), sincronização distribuída (v3.x) e mobile Android (v4.x).

O projeto atingiu um ponto de inflexão significativo: toda a infraestrutura de qualidade -- CI/CD dual-repo, branch protection, pre-commit hooks, typecheck bloqueante e pipeline de 6 estágios -- está operacional e validada. O foco agora é fechar os gaps de cobertura de testes remanescentes e preparar a base de código para a introdução da interface TUI.

**Estado Atual (01/02/2026):**

- Versão: v1.4.1 (desenvolvimento)
- Qualidade: 72% cobertura, 0 erros mypy, 0 testes skipped
- Funcionalidade: 85% comandos CLI operacionais
- Infraestrutura: CI/CD dual-repo (GitLab + GitHub), branch protection, 6 jobs bloqueantes

---

## 1. Visão de Produto

### 1.1. Evolução Arquitetural

A estratégia de evolução do TimeBlock Organizer segue um modelo incremental onde cada versão major adiciona uma camada de capacidade sem descartar as anteriores. A CLI permanece funcional mesmo após a introdução da TUI e da API, garantindo que automações e scripts existentes não sejam quebrados.

```
v1.x CLI => v1.x TUI => v2.x API => v3.x Sync => v4.x Mobile
```

A decisão de introduzir TUI ainda dentro da v1.x, antes da API, reflete a prioridade de manter a experiência do usuário local rica enquanto a camada de serviços amadurece. Detalhes em: `architecture.md` seção 9 (Evolução Futura).

### 1.2. Princípios de Desenvolvimento

Estes princípios guiam todas as decisões técnicas e de produto. Não são aspiracionais -- são critérios de aceite aplicados em cada commit, verificados automaticamente pelo pipeline CI/CD e pelos pre-commit hooks.

1. **Offline-First:** Funcionalidade completa sem rede
2. **User Control:** Sistema propõe, usuário decide
3. **Quality First:** 80% cobertura, zero erros mypy em produção
4. **DOCS => CODE:** Documentação precede implementação

---

## 2. Releases Entregues

O histórico de releases mostra uma progressão consistente: cada versão expandiu funcionalidade enquanto manteve ou melhorou métricas de qualidade. A exceção foi a v1.3.0, que acumulou débito técnico significativo (156 erros mypy), integralmente resolvido na série v1.3.x/v1.4.x.

| Versão | Data     | Escopo                     | Detalhes     |
| ------ | -------- | -------------------------- | ------------ |
| v1.0.0 | Out/2025 | Foundation                 | CHANGELOG.md |
| v1.1.0 | Nov/2025 | Core Features              | CHANGELOG.md |
| v1.2.0 | Nov/2025 | Status Refactoring         | CHANGELOG.md |
| v1.3.0 | Dez/2025 | Event Reordering (Parcial) | CHANGELOG.md |

O detalhamento de métricas por release está disponível em `docs/ssot/quality-metrics.md`, seção 2 (Histórico de Métricas).

---

## 3. Estado Atual

A versão v1.4.1 representa o estado mais maduro do projeto até o momento. Dos quatro sprints planejados para v1.4.0, três foram concluídos integralmente e o quarto parcialmente. Além disso, cinco itens originalmente planejados para v1.5.0 foram entregues antecipadamente, o que permitiu replanejar a v1.5.0 com foco exclusivo em qualidade.

- **Versão:** v1.4.1 (desenvolvimento)
- **Branch:** `chore/ci-branch-protection`
- **Data:** 01 de Fevereiro de 2026

### 3.1. Métricas Principais

As métricas atuais refletem medições reais executadas em 01/02/2026, não estimativas. Todas foram coletadas via `pytest --cov`, `mypy --check-untyped-defs` e análise automatizada do codebase.

| Métrica        | Atual | Meta v1.5.0 | Status |
| -------------- | ----- | ----------- | ------ |
| Cobertura      | 72%   | 80%         | [OK]   |
| Erros mypy     | 0     | 0           | [DONE] |
| Testes skipped | 0     | 0           | [DONE] |
| CLI funcional  | 85%   | 100%        | [OK]   |
| BRs cobertas   | 83%   | 95%         | [OK]   |

O detalhamento completo por módulo e por domínio de BRs está em `docs/ssot/quality-metrics.md`.

### 3.2. Sprints v1.4.0 (Retrospectiva)

A execução da v1.4.0 demonstrou que o investimento em documentação prévia (business rules, ADRs) acelerou significativamente os sprints de implementação. O sprint S4 ficou parcial porque o escopo de BRs descobertas durante a formalização foi maior que o estimado inicialmente -- de 17 BRs sem testes, 44 das 53 totais já estão cobertas.

| Sprint | Objetivo            | Status    | Resultado                      |
| ------ | ------------------- | --------- | ------------------------------ |
| S1     | Infraestrutura mypy | [DONE]    | 156 → 0 erros                  |
| S2     | Completar services  | [DONE]    | Timer funcional, imports OK    |
| S3     | Atualizar commands  | [DONE]    | Zero erros mypy, 85% funcional |
| S4     | Cobertura de BRs    | [PARCIAL] | 53 BRs, 44 com testes (83%)    |

### 3.3. Itens Concluídos Antecipadamente

Cinco features originalmente planejadas para v1.5.0 foram entregues durante a v1.4.x, aproveitando o momentum de infraestrutura. Isso é uma demonstração concreta do benefício de documentação-first: com a base técnica sólida, itens de infraestrutura se tornaram triviais de implementar.

| Feature              | Planejado | Entregue em |
| -------------------- | --------- | ----------- |
| GitLab CI (6 jobs)   | v1.5.0    | v1.4.1      |
| GitHub Actions       | v1.5.0    | v1.4.1      |
| Pre-commit hooks     | v1.5.0    | v1.4.1      |
| Branch protection    | v1.5.0    | v1.4.1      |
| Typecheck bloqueante | v1.5.0    | v1.4.1      |

---

## 4. Roadmap Futuro

### v1.5.0 - Cobertura e Qualidade (Fevereiro 2026)

A v1.5.0 é dedicada integralmente a fechar gaps de qualidade antes de introduzir novas funcionalidades. A razão é pragmática: adicionar TUI ou novas features sobre uma base com 35% de cobertura em commands/ e dois domínios inteiros sem testes (Tag, Skip parcial) cria risco de regressões silenciosas que o pipeline não capturaria.

**Objetivo:** Atingir os release gates de qualidade definidos na seção 3.1 do quality-metrics.md.

| Sprint | Objetivo                              | Estimativa |
| ------ | ------------------------------------- | ---------- |
| S1     | Cobrir 9 BRs sem testes               | 3h         |
| S2     | Subir cobertura services/             | 3h         |
| S3     | Subir cobertura commands/ (35% → 60%) | 4h         |
| S4     | DT-006: Padronizar idioma CLI (PT-BR) | 3h         |

**Critérios de Conclusão:**

- [ ] Cobertura global >= 80%
- [ ] 95%+ BRs com testes
- [ ] 100% comandos CLI funcionais
- [ ] Mensagens CLI 100% em português (ADR-018)

O detalhamento de cada sprint está na seção 4.1.

---

### v1.6.0 - TUI + Produção (Março 2026)

A introdução da TUI com Textual marca a transição do TimeBlock de ferramenta de linha de comando pura para uma aplicação interativa completa. A TUI e a CLI coexistem: a CLI permanece como interface para automação e scripts, enquanto a TUI oferece navegação visual para uso interativo. A publicação no PyPI e a automação de releases completam o ciclo de produção.

| Feature            | Estimativa |
| ------------------ | ---------- |
| TUI com Textual    | 16h        |
| MkDocs publicado   | 4h         |
| Release automation | 4h         |
| PyPI publish       | 2h         |

---

### v2.0.0 - REST API (Q2 2026)

A migração para API REST representa a mudança arquitetural mais significativa do projeto: separação entre frontend e backend, autenticação, e persistência em banco de dados relacional. Esta versão viabiliza clientes múltiplos e prepara o terreno para sincronização.

**Stack:** FastAPI + PostgreSQL + JWT + Prometheus

Ver: `architecture.md` seção 9.2

---

### v3.0.0 - Sync (Q3 2026)

A camada de sincronização resolve o problema de múltiplos dispositivos acessando os mesmos dados. O modelo event-driven com resolução de conflitos garante que mudanças offline sejam integradas de forma consistente quando a conectividade for restaurada.

**Stack:** Kafka + CloudEvents + Conflict Resolution

Ver: `architecture.md` seção 9.3

---

### v4.0.0 - Mobile (Q4 2026)

O cliente Android é o objetivo final da evolução arquitetural, tornando o TimeBlock acessível no dispositivo que o usuário mais carrega consigo. A arquitetura offline-first definida desde a v1.0 foi projetada com este momento em mente.

**Stack:** Kotlin + Jetpack Compose + Room

Ver: `architecture.md` seção 9.4

---

## 4.1. Detalhamento v1.5.0

### Sprint 1: BRs Sem Cobertura (3h)

Das 53 business rules formalizadas, 9 não possuem testes rastreáveis. Três dessas (BR-SKIP-002/003/004) podem ser falsos negativos causados por divergência de nomenclatura entre grep e nomes de teste -- a verificação é o primeiro passo antes de implementar novos testes.

| BR             | Domínio | Prioridade | Estimativa |
| -------------- | ------- | ---------- | ---------- |
| BR-TAG-001     | Tag     | Alta       | 30min      |
| BR-TAG-002     | Tag     | Alta       | 30min      |
| BR-SKIP-002\*  | Skip    | Verificar  | 15min      |
| BR-SKIP-003\*  | Skip    | Verificar  | 15min      |
| BR-SKIP-004\*  | Skip    | Verificar  | 15min      |
| BR-ROUTINE-006 | Routine | Média      | 30min      |
| BR-TASK-006    | Task    | Média      | 30min      |
| BR-CLI-001     | CLI     | Baixa      | 15min      |
| BR-CLI-003     | CLI     | Baixa      | 15min      |

\*BR-SKIP-002/003/004 possivelmente já cobertas (testes usam underscore, grep não detectou por buscar hífen). Verificar antes de implementar.

---

### Sprint 2: Cobertura Services (3h)

Três arquivos de service concentram o maior gap de cobertura fora de commands/. O tag_service.py está com apenas 29%, o que significa que praticamente todo o CRUD de tags não está sendo validado por testes automatizados. Priorizar esse arquivo evita que bugs em tags passem despercebidos quando a TUI for introduzida.

| Arquivo                     | Atual | Meta | Ação                  |
| --------------------------- | ----- | ---- | --------------------- |
| tag_service.py              | 29%   | 80%+ | Testes CRUD completos |
| routine_service.py          | 53%   | 80%+ | Testes de fluxos      |
| event_reordering_service.py | 61%   | 75%+ | Fluxo principal       |

---

### Sprint 3: Cobertura Commands (4h)

A camada de commands/ está com 35% de cobertura global, mas a distribuição é muito desigual: task.py está em 89% enquanto habit/display.py está em 14%. O foco deste sprint são testes de integração que exercitam os commands via CliRunner do Typer, cobrindo os caminhos principais sem entrar em testes E2E completos.

| Arquivo          | Atual | Meta | Ação              |
| ---------------- | ----- | ---- | ----------------- |
| habit/display.py | 14%   | 50%+ | Integration tests |
| tag.py           | 22%   | 60%+ | Integration tests |
| habit/atom.py    | 28%   | 60%+ | Integration tests |
| routine.py       | 33%   | 60%+ | Integration tests |
| reschedule.py    | 35%   | 60%+ | Integration tests |

---

### Sprint 4: Padronização de Idioma (3h)

O DT-006 documenta que mensagens user-facing na CLI alternam entre inglês e português, violando o ADR-018 (Language Standards). A correção é mecânica mas requer atenção: cada mensagem de erro, help text e output deve ser traduzida mantendo consistência terminológica. O critério de conclusão é objetivo: o grep por termos em inglês em mensagens user-facing deve retornar vazio.

**Referência:** ADR-018, DT-006

| Arquivo           | Ação                |
| ----------------- | ------------------- |
| init.py           | "Error" → "Erro"    |
| reschedule.py     | Verificar mensagens |
| routine.py        | Verificar mensagens |
| tag.py            | Verificar mensagens |
| timer/commands.py | Verificar mensagens |

**Critério:** `grep -rn "Error\|Warning\|Success\|Created\|Updated\|Deleted\|Not found\|Invalid" src/timeblock/commands/` retorna apenas linhas de código (except, class), não mensagens user-facing.

---

## 5. Débito Técnico

O inventário completo de débito técnico foi extraído para um documento dedicado em `docs/ssot/technical-debt.md`. Esta separação reflete a maturidade do projeto: o roadmap define "para onde vamos", enquanto o technical-debt.md registra "o que devemos antes de ir".

**Resumo:**

| Status    | Quantidade | Itens                                                |
| --------- | ---------- | ---------------------------------------------------- |
| Resolvido | 3          | DT-001 (mypy), DT-002 (skipped), DT-003 (parcial)    |
| Pendente  | 3          | DT-004 (reordering), DT-005 (morto), DT-006 (idioma) |
| Aceito    | 1          | DT-007 (migration_001)                               |

---

## 6. Política de Governança

### 6.1. Hierarquia de Documentos

O projeto mantém cinco documentos SSOT (Single Source of Truth) que formam a base de conhecimento técnico. Cada documento tem escopo definido e não deve duplicar informação presente nos demais. Os ADRs são imutáveis após aceitos -- se uma decisão muda, um novo ADR é criado referenciando o anterior como superseded.

```
SSOT Documents:
├── roadmap.md           => Estado e planejamento
├── business-rules.md    => Regras de negócio
├── architecture.md      => Decisões técnicas
├── quality-metrics.md   => Métricas operacionais
├── technical-debt.md    => Inventário de débito técnico
└── CHANGELOG.md         => Histórico de releases

ADRs (Imutáveis):
└── docs/decisions/      => Decisões arquiteturais

Working Documents:
└── docs/testing/        => Estratégias de teste
```

---

## 7. Changelog do Documento

| Data       | Versão | Mudanças                                                                         |
| ---------- | ------ | -------------------------------------------------------------------------------- |
| 2026-01-14 | 1.0.0  | Criação inicial                                                                  |
| 2026-01-16 | 2.0.0  | Reformulação profissional                                                        |
| 2026-01-16 | 2.1.0  | Remoção de duplicações, referências a docs externos                              |
| 2026-02-01 | 3.0.0  | Atualização com dados reais, retrospectiva v1.4.0, extração de technical-debt.md |

---

**Próxima Revisão:** Fim v1.5.0

**Última atualização:** 01 de Fevereiro de 2026
