# Release Strategy

- **Versão:** 0.1.0 (esqueleto)
- **Status:** Rascunho

---

## 1. Versionamento

Semântico (MAJOR.MINOR.PATCH) conforme semver.org. MAJOR para breaking changes na CLI/API, MINOR para features novas, PATCH para bugfixes.

---

## 2. Branch Strategy

Gitflow simplificado: `develop` (integração), `main` (releases), feature branches via MR. Branches protegidas exigem pipeline verde.

---

## 3. Critérios de Release

- Pipeline verde (8 jobs)
- 0 erros basedpyright (standard)
- Todos os testes passando
- Sem regressão em snapshots e2e
- CHANGELOG.md atualizado
- Tag anotada com mensagem limpa

---

## 4. Processo de Bug

Modelo Fowler (2018): bug reportado -> teste RED reproduzindo -> fix GREEN -> teste permanece na suite. Bugs competem no backlog normal via GitLab Issues. Classificação por severidade (critical/high/medium/low).

---

## 5. Feature Toggles

Mecanismo para lançar features incrementalmente sem expor funcionalidade incompleta. Detalhes em ADR-048. Ciclo: criado disabled -> habilitado em dev -> habilitado por padrão -> removido na release seguinte.

---

## 6. Distribuição

### Atual (v1.x)
- `pip install` via fonte ou wheel
- Entry point: `atomvs` (pyproject.toml)

### Planejado (v2.0)
- Publicação no PyPI
- Auto-update check (issue #27)

---

## 7. Hotfixes

Branch `hotfix/*` a partir de `main`. MR direto para `main` + cherry-pick para `develop`. Sem feature toggles — fix direto.

---

## Referências

- Humble, J.; Farley, D. Continuous Delivery. 2010. Cap. 10 (release strategy), Cap. 13 (feature toggles)
- Fowler, M. Refactoring. 2018. Cap. 4 (testes e bugs)
- ADR-048: Feature toggles
- Issue #25, #35

---

## Changelog do Documento

| Data       | Versão | Mudanças       |
| ---------- | ------ | -------------- |
| 2026-04-09 | 0.1.0  | Esqueleto      |
