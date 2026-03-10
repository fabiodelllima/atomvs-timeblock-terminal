# Technical Debt

**Versão:** 2.0.0

**Status:** SSOT

**Documentos Relacionados:** roadmap.md, quality-metrics.md, sprint-4-code-review.md

---

## 1. Inventário

| ID     | Descrição                                  | Severidade | Status    | Resolvido em | Sprint planejado         |
| ------ | ------------------------------------------ | ---------- | --------- | ------------ | ------------------------ |
| DT-001 | 156 erros mypy                             | CRÍTICA    | RESOLVIDO | Jan/2026     | v1.4.0 S1-S3             |
| DT-002 | 15 testes skipped                          | ALTA       | RESOLVIDO | Jan/2026     | v1.4.0 S4                |
| DT-003 | Cobertura abaixo de 80%                    | ALTA       | RESOLVIDO | Mar/2026     | v1.6.0                   |
| DT-004 | EventReordering parcial (61%)              | MÉDIA      | RESOLVIDO | Fev/2026     | -                        |
| DT-005 | Código morto                               | BAIXA      | RESOLVIDO | Fev/2026     | -                        |
| DT-006 | Idioma misto EN/PT em CLI                  | MÉDIA      | RESOLVIDO | Fev/2026     | v1.5.0                   |
| DT-007 | migration_001 sem cobertura                | BAIXA      | ACEITO    | -            | -                        |
| DT-008 | GitHub Actions --fail-under divergente     | MÉDIA      | PENDENTE  | -            | v1.7.0                   |
| DT-009 | FocusablePanel: C_HIGHLIGHT na base        | ALTA       | PENDENTE  | -            | v1.7.0                   |
| DT-010 | FocusablePanel: flag \_showing_placehold.  | ALTA       | PENDENTE  | -            | v1.7.0                   |
| DT-011 | FocusablePanel: count em dois lugares      | ALTA       | PENDENTE  | -            | v1.7.0                   |
| DT-012 | DI inconsistente entre services            | MÉDIA      | PENDENTE  | -            | v2.0                     |
| DT-013 | \_parse_time duplicado (crud_habits/tasks) | BAIXA      | PENDENTE  | -            | v1.7.0                   |
| DT-014 | Keybindings divergentes BR vs código       | ALTA       | PENDENTE  | -            | feat/tui-dashboard-timer |

---

## 2. Detalhamento de Itens Resolvidos

### DT-001: Erros Mypy (RESOLVIDO)

- **Descoberto:** 16/01/2026
- **Resolvido:** Jan/2026
- **Impacto original:** 156 erros em modo strict, commands não passavam no type checker
- **Resolução:** Instalação de stubs, correção de Session.exec, correção de SQLAlchemy datetime comparisons, completude do Service Layer, null checks em commands
- **Estado final:** 0 erros em 45 arquivos fonte

### DT-002: Testes Skipped (RESOLVIDO)

- **Descoberto:** 16/01/2026
- **Resolvido:** Jan/2026
- **Impacto original:** 15 testes marcados como skip (stubs vazios, timer API v1, migrations)
- **Resolução:** Implementação dos stubs, atualização para API v2, remoção de testes obsoletos
- **Estado final:** 0 testes skipped, 618 passando

### DT-003: Cobertura Abaixo de 80% (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Mar/2026
- **Cobertura original:** 76%
- **Cobertura atual:** ~81% (threshold 80%)
- **Resolução:** Sprint 3.2 e Sprint 4 adicionaram ~300 testes TUI

### DT-004: EventReordering Parcial (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Fev/2026
- **Cobertura original:** 61%
- **Cobertura atual:** 86%
- **Resolução:** Testes de integração cobrindo cenários de reorganização

### DT-005: Código Morto (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Fev/2026
- **Verificação:** `ruff check src/timeblock --select F401,F841` retorna 0 issues
- **Resolução:** Limpeza gradual durante refatorações

### DT-006: Idioma Misto EN/PT (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Fev/2026
- **Referência:** ADR-018 (Language Standards)
- **Resolução:** Tradução de mensagens CLI para PT-BR, criação de script lint-i18n.py
- **Verificação:** `python scripts/lint-i18n.py` retorna 0 inconsistências

---

## 3. Detalhamento de Itens Pendentes

### DT-007: migration_001 Sem Cobertura (ACEITO)

- **Cobertura:** 0%
- **Justificativa:** Migração one-shot já executada em produção. Custo de testar supera benefício. Será removida quando migração definitiva for criada (v2.0.0).
- **Decisão:** Aceitar o débito. Não investir esforço em cobertura.

### DT-008: GitHub Actions --fail-under Divergente

- **Descoberto:** 08/03/2026
- **Impacto:** Job `CI / test (push)` falha no GitHub com `--fail-under=85` enquanto GitLab usa 80%. GitHub Actions também usa Python 3.13 enquanto projeto roda em 3.14.
- **Arquivo:** `.github/workflows/ci.yml`
- **Ação:** Alinhar `--fail-under=80` e `python-version: "3.14"` com GitLab CI.
- **Sprint:** feat/tui-dashboard-timer ou próximo commit de CI.

### DT-009: C_HIGHLIGHT Acoplado na Classe Base FocusablePanel (CRITICAL-001)

- **Descoberto:** 08/03/2026 (Sprint 4 Code Review)
- **Impacto:** FocusablePanel importa `C_HIGHLIGHT` de `colors.py` e aplica highlight em `_build_empty_state`. Classe base conhece e decide cor de cursor — responsabilidade de apresentação que pertence às subclasses ou ao TCSS.
- **Arquivo:** `src/timeblock/tui/widgets/focusable_panel.py` linha 11
- **Ação:** Extrair highlight para método `_apply_cursor_highlight` sobrescrevível, ou usar classes CSS do Textual.
- **Referência:** sprint-4-code-review.md CRITICAL-001
- **Sprint:** v1.7.0 (pré-release)

### DT-010: \_showing_placeholders Como Flag Booleano Solto (CRITICAL-002)

- **Descoberto:** 08/03/2026 (Sprint 4 Code Review)
- **Impacto:** Booleano gerenciado manualmente em `update_data()` de cada subclasse. Estado duplicado — pode ser derivado da ausência de dados reais. Bug silencioso se subclasse esquecer de setar o flag.
- **Arquivos:** `focusable_panel.py` linha 30, `habits_panel.py` linhas 35-39, `tasks_panel.py` linhas 38-42
- **Ação:** Transformar em propriedade derivada ou encapsular em método `_set_placeholder_mode(count)`.
- **Referência:** sprint-4-code-review.md CRITICAL-002
- **Sprint:** v1.7.0 (pré-release)

### DT-011: Count Definido em Dois Lugares Divergentes (CRITICAL-003)

- **Descoberto:** 08/03/2026 (Sprint 4 Code Review)
- **Impacto:** `update_data` define `_set_item_count(N)` e `_build_empty_state(..., count=N)` recebe N separadamente. Se divergirem, cursor aceita posições invisíveis. Já aconteceu durante a Sprint 4.
- **Arquivos:** `tasks_panel.py` linhas 41 e 100
- **Ação:** Unificar em método único `_enter_placeholder_mode(placeholder, hint, count)` que seta count e retorna linhas.
- **Referência:** sprint-4-code-review.md CRITICAL-003
- **Sprint:** v1.7.0 (pré-release)

### DT-012: DI Inconsistente Entre Services

- **Descoberto:** 08/03/2026 (Sprint 4 Code Review)
- **Impacto:** Três padrões de DI coexistem: `RoutineService(s)` (constructor), `HabitInstanceService().method(session=s)` (parameter + instance), `TaskService.method(session=s)` (static + parameter). Confuso para contribuidores.
- **Arquivo:** `src/timeblock/tui/screens/dashboard/loader.py`
- **Ação:** Unificar na v2.0 com Application Layer e Repository Pattern.
- **Referência:** sprint-4-code-review.md WARNING-001
- **Sprint:** v2.0

### DT-013: \_parse_time Duplicado em Dois Módulos

- **Descoberto:** 08/03/2026 (Sprint 4 Code Review)
- **Impacto:** Mesma função `_parse_time(value: str) -> time` em `crud_habits.py` e `crud_tasks.py`. Bug fix em um não propaga para o outro.
- **Ação:** Mover para `src/timeblock/tui/utils.py` ou reutilizar `validators.py`.
- **Referência:** sprint-4-code-review.md WARNING-006
- **Sprint:** v1.7.0

### DT-014: Keybindings Divergentes Entre BR-TUI-004 e Código

- **Descoberto:** 08/03/2026
- **Impacto:** BR-TUI-004 especifica `Ctrl+K`, `Ctrl+P`, `Ctrl+W`, `Ctrl+E`, `d/r/h/t/m`. Código usa `n/e/x` sem Ctrl, `Ctrl+K`, `q` sem Ctrl. ADR-035 define mapa definitivo que difere de ambos.
- **Ação:** Alinhar código com ADR-035 e atualizar BR-TUI-004. Remover `d/r/h/t/m` e `Ctrl+K` do app.py e screen.py. Implementar `Ctrl+1..5`, `Ctrl+Q`, `Shift+Enter`, `Ctrl+X`.
- **Referência:** ADR-035 (Keybindings Standardization)
- **Sprint:** feat/tui-dashboard-timer (primeiro commit)

---

## 4. Política de Gestão

Novos débitos técnicos devem ser registrados aqui com ID sequencial (DT-XXX), severidade e sprint planejado para resolução. O inventário é revisado a cada release.

**Severidades:**

- **CRÍTICA:** Bloqueia desenvolvimento ou deploy
- **ALTA:** Impacta qualidade ou manutenibilidade significativamente
- **MÉDIA:** Degradação gradual, deve ser resolvido no próximo release
- **BAIXA:** Cosmético ou preferencial, resolver quando conveniente
- **ACEITO:** Débito consciente com justificativa documentada

---

## 5. Changelog do Documento

| Data       | Versão | Mudanças                                                |
| ---------- | ------ | ------------------------------------------------------- |
| 2026-03-08 | 2.0.0  | DT-003 resolvido. Adicionados DT-008 a DT-014 (Sprint 4 |
|            |        | Code Review + GitHub CI + keybindings divergentes)      |
| 2026-02-03 | 1.1.0  | Atualiza status: DT-004, DT-005, DT-006 resolvidos      |
| 2026-02-01 | 1.0.0  | Extração do roadmap.md para documento dedicado          |

---

**Próxima Revisão:** Release v1.7.0

**Última atualização:** 10 de Março de 2026
