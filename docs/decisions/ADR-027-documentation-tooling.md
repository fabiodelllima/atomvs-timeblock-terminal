# ADR-027: MkDocs com mkdocstrings para Documentação

**Status:** Aceito

**Data:** 28 de Janeiro de 2026

**Contexto:** Definir stack de documentação para v1.5.0

---

## Decisão

Usar **MkDocs** com **mkdocstrings** para toda documentação do projeto, incluindo extração automática de docstrings.

**Stack definida:**

| Componente | Ferramenta             | Função              |
| ---------- | ---------------------- | ------------------- |
| Core       | MkDocs                 | Site estático       |
| Theme      | Material for MkDocs    | UI moderna          |
| API Docs   | mkdocstrings[python]   | Extração docstrings |
| Diagramas  | mkdocs-mermaid2-plugin | Diagramas Mermaid   |

---

## Contexto

Alternativas consideradas:

| Ferramenta | Formato  | Prós                          | Contras                       |
| ---------- | -------- | ----------------------------- | ----------------------------- |
| MkDocs     | Markdown | Stack unificada, legibilidade | Cross-refs via extensões      |
| Sphinx     | RST      | Autodoc nativo, cross-refs    | Duas ferramentas, sintaxe RST |
| Docusaurus | MDX      | React integrado               | Overkill para CLI Python      |

---

## Razão

1. **Consistência:** Toda documentação existente (50+ BRs, 20+ ADRs) já está em Markdown
2. **Curva de aprendizado:** Markdown é universalmente conhecido
3. **Funcionalidade equivalente:** mkdocstrings oferece autodoc comparável ao Sphinx
4. **Stack unificada:** Uma ferramenta para SSOT docs + API reference
5. **Docstrings existentes:** Projeto já usa Google-style docstrings, integração direta

---

## Implementação

**Dependências:**

```bash
pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-mermaid2-plugin
```

**mkdocs.yml:**

```yaml
site_name: TimeBlock Organizer
theme:
  name: material
  palette:
    scheme: slate

plugins:
  - search
  - mermaid2
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true
            show_root_heading: true
            members_order: source

nav:
  - Home: index.md
  - Core:
      - Business Rules: core/business-rules.md
      - Architecture: core/architecture.md
      - Roadmap: core/roadmap.md
  - API Reference:
      - Services: api/services.md
      - Models: api/models.md
  - Decisions: decisions/
```

**Uso em docs/api/services.md:**

```markdown
# Services API

## HabitService

::: timeblock.services.habit_service.HabitService
options:
members: - create - get_by_id - list_active - update - delete

## TimerService

::: timeblock.services.timer_service.TimerService
```

---

## Trade-offs

**Positivos:**

- [+] Zero migração de documentação existente
- [+] Docstrings já seguem Google style
- [+] Uma stack para tudo
- [+] Hot reload durante desenvolvimento

**Negativos:**

- [-] Cross-references menos poderosos que Sphinx
- [-] Comunidade mkdocstrings menor que Sphinx autodoc

---

## Alternativas Rejeitadas

### Sphinx com RST

Rejeitado porque:

- Requer migração de toda documentação para RST
- Duas ferramentas (Sphinx para API, MkDocs para docs gerais)
- RST menos legível em raw format
- Complexidade sem benefício proporcional para projeto atual

### Manter apenas Markdown sem autodoc

Rejeitado porque:

- Duplicação entre docstrings e documentação
- Sincronização manual propensa a erros
- Perda de type hints na documentação

---

## Métricas de Sucesso

- [ ] Site MkDocs publicado (GitHub Pages ou similar)
- [ ] 100% dos services documentados via mkdocstrings
- [ ] 100% dos models documentados via mkdocstrings
- [ ] Build time < 30s
- [ ] Zero warnings no build

---

## Referências

- MkDocs: <https://www.mkdocs.org/>
- Material for MkDocs: <https://squidfunk.github.io/mkdocs-material/>
- mkdocstrings: <https://mkdocstrings.github.io/>
- ADR-018: Language Standards

---

**Decisão final:** MkDocs + mkdocstrings

**Implementação planejada:** v1.5.0 (Março 2026)
