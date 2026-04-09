# Sprints

- **Versão:** 1.7.2
- **Status:** Single Source of Truth (SSOT)

---

## Visão Geral

Este documento acompanha as sprints ativas do projeto ATOMVS TimeBlock Terminal. Cada sprint representa um ciclo de entregas incrementais onde requisitos formalizados são decompostos em tarefas atômicas, validados e implementados com rastreabilidade completa. A metodologia de engenharia de requisitos, análise comportamental e implementação orientada por testes está documentada em `docs/explanation/development-methodology.md`.

O histórico de sprints concluídas (v1.0.0 a v1.7.0) está arquivado em `docs/reference/sprints-archive.md`.

---

## v1.7.1 — Polish e Docs

A v1.7.1 foi entregue em 2026-04-09 (tag `v1.7.1`, commit `723a41a`). Release de polimento pós-v1.7.0 focada em documentação, auditoria de diagramas e observabilidade. Sprint 7.3 (padronização ADRs) foi deferida para v1.8.0 como DT-070/DT-071.

**Métricas de acompanhamento:**

| Métrica            | Início (v1.7.0) | Meta v1.7.1 |
| ------------------ | --------------- | ----------- |
| Cobertura global   | ~82%            | >= 80%      |
| Testes totais      | ~1340           | ~1340       |
| Erros basedpyright | 0 (standard)    | 0           |
| DTs resolvidos     | 58/71           | 62/71       |

---

### Sprint 7.1 — Documentação Pós-Release [DONE]

O Sprint 7.1 atualiza toda a documentação de referência para refletir o estado pós-v1.7.0 e resolve DTs de baixa complexidade documentais.

**Branch:** `docs/post-release-v1.7.0`

**Critério de conclusão:** roadmap.md, sprints.md e technical-debt.md atualizados, DT-066 resolvido, DT-065/DT-067 re-tagged.

- [ ] Atualizar roadmap.md — v1.7.0 entregue, métricas atualizadas, bump v8.0.0
- [ ] Atualizar sprints.md — v1.7.0 movida para archive, v1.7.1 criada
- [ ] Atualizar technical-debt.md — DT-066 RESOLVIDO, DT-065/067 re-tagged para v1.7.1, bump v2.28.0
- [ ] Fix sync:github — push normal para main/develop, --force para branches
- [ ] Validar: pipeline verde na branch

---

### Sprint 7.2 — Auditoria de Diagramas e README [DONE]

| Item  | Descrição                                              | DT     |
| ----- | ------------------------------------------------------ | ------ |
| 7.2.1 | Auditar 16 diagramas em docs/diagrams/ vs estado atual | DT-067 |
| 7.2.2 | Remover ou atualizar diagramas desatualizados          | DT-067 |
| 7.2.3 | Linkar diagramas válidos no README                     | DT-067 |
| 7.2.4 | Screenshots/GIFs do dashboard funcional no README      | —      |

---

### Sprint 7.3 — Padronização ADRs e Docs [DEFERIDO → v1.8.0]

| Item  | Descrição                                                | DT     |
| ----- | -------------------------------------------------------- | ------ |
| 7.3.1 | Script para padronizar headers de 46 ADRs (EN → PT-BR)   | DT-070 |
| 7.3.2 | Definir e documentar padrão de header/footer para docs   | DT-071 |
| 7.3.3 | Documentar responsividade 80x24 como limitação conhecida | DT-065 |

---

## v1.7.2 — Polish Visual e Correções Urgentes

Release focada em bugs descobertos em uso real do dashboard e polish visual. Tracking via GitLab Issues (milestone v1.7.2). A migração de `technical-debt.md` + `sprints.md` para GitLab Issues foi decidida na Sessão 19.

**Branch:** `chore/gitlab-issues-and-docs` (base: v1.7.1)

**Critérios de conclusão:** pipeline verde, 0 erros basedpyright, sem regressão em snapshots e2e.

### Bugs (prioridade alta)

| Issue | Título                                              | Status  |
| ----- | --------------------------------------------------- | ------- |
| #5    | TimerPanel não converte >60min para H:MM:SS         | backlog |
| #36   | Impossível iniciar nova sessão em habit já done     | backlog |
| #33   | Header exibe placeholders em vez de dados dinâmicos | backlog |
| #1    | update não propaga horários para instâncias         | backlog |
| #2    | generate cria duplicatas                            | backlog |

### Correções e polish (prioridade média/baixa)

| Issue | Título                                              | Status  |
| ----- | --------------------------------------------------- | ------- |
| #30   | Corrigir title/subtitle no header                   | backlog |
| #31   | Reordenar panels (timer > habits > tasks > metrics) | backlog |
| #29   | Remover hint do TimerPanel                          | backlog |
| #32   | Footer — cores dos hints e margem inferior          | backlog |
| #34   | Remover régua no AgendaPanel                        | backlog |
| #11   | DT-073: __pycache__ paths absolutos                 | backlog |

**Ordem de implementação recomendada:** #5 (isolado, localização conhecida) -> #36 (investigar validação de estado) -> #33 (investigar widgets do header) -> #1/#2 (bugs pré-existentes) -> UI polish (#29, #30, #31, #32, #34) como batch -> #11.

---

## v1.8.0 — Agenda e Sidebar (Planejado)

A v1.8.0 implementa o redesign da agenda com blocos de tempo contínuos, scroll horizontal, paginação de dias e sidebar compacta. Representa a próxima evolução visual da TUI.

| Item | Descrição                                     | DT     | Complexidade |
| ---- | --------------------------------------------- | ------ | ------------ |
| 8.1  | Sidebar redesign (horizontal/hidden/vertical) | DT-060 | Alta         |
| 8.2  | AgendaPanel scroll horizontal                 | DT-061 | Alta         |
| 8.3  | Blocos de tempo contínuos (accent bar + cor)  | DT-062 | Alta         |
| 8.4  | Paginação de dias (-3 a +3)                   | DT-063 | Média        |
| 8.5  | Navegação de dia com setas (BR-TUI-030)       | —      | Média        |
| 8.6  | Scroll horizontal com Shift+h/l (BR-TUI-031)  | —      | Média        |
| 8.7  | Renderização de blocos coloridos (BR-TUI-032) | —      | Alta         |

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

---

- **Próxima revisão:** Após v1.7.2 entregue
- **Última atualização:** 9 de Abril de 2026
