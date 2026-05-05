# Sprints

- **Versão:** 8.0.0
- **Status:** [HISTÓRICO] — Descontinuado como SSOT operacional desde a Sessão 19 (2026-04-09)
- **Substituído por:** GitLab Issues com milestones a partir de v1.7.2
- **Documentos relacionados:** roadmap.md, sprints-archive.md, technical-debt.md

---

## Aviso de Descontinuação

Este documento foi o registro de tracking operacional do projeto entre v1.5.0 e v1.7.1. A partir da v1.7.2 (entregue em 2026-04-13) o tracking operacional migrou para **GitLab Issues** com milestones por release, decisão registrada no handoff da Sessão 19 (2026-04-09).

A motivação da migração foi prática: GitLab Issues oferecem labels estruturadas, vinculação automática a MRs via `Closes #N`, milestones com burndown automático e busca cross-referência entre issues. Manter um arquivo Markdown sincronizado com este nível de granularidade duplicava esforço sem agregar valor.

Este documento permanece versionado como **registro histórico** dos sprints v1.7.0 e v1.7.1, com link para o `sprints-archive.md` que cobre v1.0.0 a v1.6.0. A partir de v1.7.2, consultar:

- **Tracking corrente:** [GitLab Milestones](https://gitlab.com/delimafabio/atomvs-timeblock-terminal/-/milestones)
- **Histórico de releases:** `CHANGELOG.md`
- **Planejamento de longo prazo:** `docs/reference/roadmap.md`

Não há previsão de retomar o tracking via Markdown. Caso a equipe cresça e essa decisão precise ser revista, o ponto de retomada será uma nova ADR documentando a justificativa.

---

## Visão Geral Histórica

Este documento acompanhou as sprints ativas do projeto ATOMVS Time Planner Terminal entre v1.5.0 e v1.7.1. Cada sprint representava um ciclo de entregas incrementais onde requisitos formalizados eram decompostos em tarefas atômicas, validados e implementados com rastreabilidade completa. A metodologia de engenharia de requisitos, análise comportamental e implementação orientada por testes está documentada em `docs/explanation/development-methodology.md`.

O histórico de sprints concluídas até v1.7.0 está arquivado em `docs/reference/sprints-archive.md`.

---

## v1.7.1 — Polish e Docs (Concluído — 2026-04-09)

A v1.7.1 foi entregue em 2026-04-09 (tag `v1.7.1`, commit `723a41a`). Release de polimento pós-v1.7.0 focada em documentação, auditoria de diagramas e observabilidade. Sprint 7.3 (padronização ADRs) foi deferida para v1.8.0 como DT-070/DT-071.

**Métricas de acompanhamento:**

| Métrica            | Início (v1.7.0) | Entrega (v1.7.1) |
| ------------------ | --------------- | ---------------- |
| Cobertura global   | ~82%            | ~82%             |
| Testes totais      | ~1.340          | ~1.345           |
| Erros basedpyright | 0 (standard)    | 0                |
| DTs resolvidos     | 58/71           | 62/71            |

### Sprint 7.1 — Documentação Pós-Release [DONE]

O Sprint 7.1 atualizou toda a documentação de referência para refletir o estado pós-v1.7.0 e resolveu DTs de baixa complexidade documentais.

**Branch:** `docs/post-release-v1.7.0`

**Critério de conclusão:** roadmap.md, sprints.md e technical-debt.md atualizados, DT-066 resolvido, DT-065/DT-067 re-tagged.

- [x] Atualizar roadmap.md — v1.7.0 entregue, métricas atualizadas, bump v8.0.0
- [x] Atualizar sprints.md — v1.7.0 movida para archive, v1.7.1 criada
- [x] Atualizar technical-debt.md — DT-066 RESOLVIDO, DT-065/067 re-tagged para v1.7.1, bump v2.28.0
- [x] Fix sync:github — push normal para main/develop, --force para branches
- [x] Validar: pipeline verde na branch

### Sprint 7.2 — Auditoria de Diagramas e README [DONE]

| Item  | Descrição                                              | DT     |
| ----- | ------------------------------------------------------ | ------ |
| 7.2.1 | Auditar 16 diagramas em docs/diagrams/ vs estado atual | DT-067 |
| 7.2.2 | Remover ou atualizar diagramas desatualizados          | DT-067 |
| 7.2.3 | Linkar diagramas válidos no README                     | DT-067 |
| 7.2.4 | Screenshots/GIFs do dashboard funcional no README      | —      |

### Sprint 7.3 — Padronização ADRs e Docs [DEFERIDO → v1.8.0]

| Item  | Descrição                                                | DT     |
| ----- | -------------------------------------------------------- | ------ |
| 7.3.1 | Script para padronizar headers de 46 ADRs (EN → PT-BR)   | DT-070 |
| 7.3.2 | Definir e documentar padrão de header/footer para docs   | DT-071 |
| 7.3.3 | Documentar responsividade 80x24 como limitação conhecida | DT-065 |

---

## Continuação Pós-v1.7.1

A partir de v1.7.2 (corte 2026-04-13), o tracking de sprint está em GitLab Issues. Para consultar entregas:

- **v1.7.2:** Milestone fechada — onze issues entregues, tag `7218bb0`
- **v1.7.3:** Milestone fechada — três fixes em categoria `Fixed`, tag `2a90333` em 2026-05-01
- **v1.7.4:** Milestone aberta — escopo em padronização documental e estabilidade de snapshots
- **v1.7.5:** Milestone aberta — escopo em bugs e cobertura BR pendente
- **v1.8.0:** Milestone aberta — agenda redesign, archive lifecycle (issue #61 reescopada), reconciliação Gitflow (issue #64)

Detalhamento estratégico em `docs/reference/roadmap.md` seção 4.

---

## Changelog do Documento

| Data       | Versão | Mudanças                                                   |
| ---------- | ------ | ---------------------------------------------------------- |
| 2026-02-05 | 1.0.0  | Criação inicial — planejamento v1.7.0 com 7 sprints        |
| 2026-03-02 | 2.0.0  | Sprint 0/1/2 marcados DONE, Sprint 3.1 DONE, 3.2 detalhado |
| 2026-03-05 | 3.0.0  | Sprint 3.2 marcada DONE, Sprint 4 reescrita                |
| 2026-03-10 | 4.0.0  | Sprint 4 DONE, Sprint 4.5 First Complete Loop              |
| 2026-03-15 | 5.0.0  | Sprint 5.5 planejada, ADR-038, DT-034 a DT-042             |
| 2026-03-27 | 6.0.0  | Sprint 4.5 DONE, Fase 5 progresso, ~1320 testes            |
| 2026-04-05 | 7.0.0  | v1.7.0 entregue — sprints movidos para archive,            |
|            |        | v1.7.1 (Polish e Docs) e v1.8.0 (Agenda e Sidebar) criados |
| 2026-05-01 | 8.0.0  | Documento marcado como [HISTÓRICO]. Tracking operacional   |
|            |        | migrou oficialmente para GitLab Issues a partir de v1.7.2. |
|            |        | Aviso de descontinuação adicionado no topo. v1.7.1 marcada |
|            |        | como concluída. Ponteiro para milestones do GitLab.        |

---

- **Última atualização:** 1 de Maio de 2026
- **Estado:** Não receberá novas entradas. Atualizações apenas para correções históricas ou para registrar uma eventual reversão da decisão de descontinuação.
