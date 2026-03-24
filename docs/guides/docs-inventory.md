# Inventário de Documentação

**Versão:** 1.0.0

**Criado:** 2026-03-23

---

## Objetivo

Listar todos os arquivos em `docs/`, classificar por categoria Diátaxis, verificar presença de data/versão, e identificar documentos desatualizados.

---

## Padrão de Campos Obrigatórios

| Categoria        | Campos obrigatórios                     |
| ---------------- | --------------------------------------- |
| Reference (SSOT) | Versão, Última atualização, Changelog   |
| Reference (BRs)  | Última atualização                      |
| Decisions (ADRs) | Date (formato Nygard)                   |
| Explanation      | Criado em, Última revisão (se revisado) |
| Tutorial/Howto   | Criado em, Última validação             |

---

## docs/reference/

| Arquivo            | Versão | Última atualização | Status     |
| ------------------ | ------ | ------------------ | ---------- |
| roadmap.md         | 7.0.0  | 2026-03-23         | ATUALIZADO |
| sprints.md         | 5.0.0  | 2026-03-23         | ATUALIZADO |
| technical-debt.md  | 2.23.0 | 2026-03-23         | ATUALIZADO |
| quality-metrics.md | ?      | ?                  | VERIFICAR  |
| workflows.md       | ?      | ?                  | VERIFICAR  |
| sprints-archive.md | ?      | ?                  | VERIFICAR  |

## docs/reference/business-rules/

| Arquivo       | Última atualização | Status                              |
| ------------- | ------------------ | ----------------------------------- |
| index.md      | ?                  | VERIFICAR                           |
| br-routine.md | ?                  | VERIFICAR                           |
| br-habit.md   | ?                  | VERIFICAR                           |
| br-task.md    | ?                  | VERIFICAR                           |
| br-tui.md     | 2026-03-23         | ATUALIZADO                          |
| br-cli.md     | ?                  | VERIFICAR                           |
| br-obs.md     | 2026-03-23         | NOVO                                |
| br-testing.md | 2026-03-23         | ATUALIZADO (BR-TEST-002 adicionada) |

## docs/decisions/

| Arquivo           | Date       | Status          |
| ----------------- | ---------- | --------------- |
| ADR-001 a ADR-043 | VERIFICAR  | VERIFICAR       |
| ADR-044           | 2026-03-23 | NOVO (Proposed) |
| ADR-045           | 2026-03-23 | NOVO (Proposed) |
| ADR-046           | 2026-03-23 | NOVO (Proposed) |

## docs/explanation/

| Arquivo                      | Criado     | Status     |
| ---------------------------- | ---------- | ---------- |
| agenda-overlap-rendering.md  | 2026-03-22 | ATUALIZADO |
| quality-barriers-research.md | 2026-03-23 | NOVO       |
| architecture.md              | ?          | VERIFICAR  |
| development-methodology.md   | ?          | VERIFICAR  |
| domain-concepts.md           | ?          | VERIFICAR  |

## docs/guides/

| Arquivo                     | Criado     | Status    |
| --------------------------- | ---------- | --------- |
| snapshot-testing.md         | 2026-03-23 | NOVO      |
| docs-inventory.md           | 2026-03-23 | ESTE DOC  |
| testing-patterns.md         | ?          | VERIFICAR |
| manual-testing-checklist.md | ?          | VERIFICAR |
| ci-optimization.md          | ?          | VERIFICAR |
| development-workflow.md     | ?          | VERIFICAR |
| refactoring-catalog.md      | ?          | VERIFICAR |
| cicd-flow.md                | ?          | VERIFICAR |

---

## Próximos Passos

1. Preencher colunas "?" inspecionando cada arquivo
2. Aplicar padrão de cabeçalho (ADR-046)
3. Branch `docs/standardize-headers` para padronização em batch
