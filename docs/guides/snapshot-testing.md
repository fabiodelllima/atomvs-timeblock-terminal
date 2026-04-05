# Estratégia de Snapshot Testing para TUI

**Status:** Implementado (local-only, excluído do CI)

**Criado:** 2026-03-23

**Atualizado:** 2026-04-02

**Referências:**

- pytest-textual-snapshot 1.1.0 (Textualize, 2024)
- syrupy 4.8.0
- Textual Testing Guide (textual.textualize.io/guide/testing)
- ADR-037: Testes E2E com Textual Pilot

---

## 1. Contexto e Motivação

O ATOMVS Time Planner Terminal possui ~1320 testes (mar/2026), com cobertura extensiva de lógica via `pilot.press()` + asserções de estado. Porém, esses testes não validam renderização visual — é possível que um bloco de agenda renderize com cores trocadas, alinhamento quebrado ou accent bar ausente sem que nenhum teste falhe.

Snapshot testing preenche essa lacuna: captura SVGs da TUI em execução e compara com baselines aprovadas. Mudanças visuais — intencionais ou acidentais — geram falhas com diff visual, permitindo detecção automática de regressões visuais.

---

## 2. Ferramenta: pytest-textual-snapshot

O `pytest-textual-snapshot` é o plugin oficial da Textualize, mantido pela mesma equipe que desenvolve o Textual. Internamente, o Textual usa snapshot testing para validar todos os widgets builtin em cada release.

**Instalação:**

```bash
pip install pytest-textual-snapshot
```

**Como funciona:**

1. O teste instancia a app Textual (sem rodar)
2. O plugin renderiza a app num terminal virtual
3. Gera um SVG da tela renderizada
4. Na primeira execução, salva como baseline (teste falha — esperado)
5. Nas execuções seguintes, compara SVG atual com baseline
6. Se diferir, gera report HTML com diff visual lado a lado

**Exemplo básico:**

```python
def test_dashboard_initial_state(snap_compare):
    """Snapshot: dashboard renderiza corretamente com rotina ativa."""
    assert snap_compare("src/timeblock/tui/app.py")
```

**Com interação antes da captura:**

```python
def test_dashboard_after_creating_habit(snap_compare):
    """Snapshot: dashboard após criar hábito via modal."""
    async def run_before(pilot):
        await pilot.press("tab", "tab")   # Foca panel hábitos
        await pilot.press("n")            # Abre FormModal
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

    assert snap_compare(
        "src/timeblock/tui/app.py",
        run_before=run_before,
        terminal_size=(120, 40),
    )
```

**Atualizando baselines:**

```bash
# Após validar visualmente que o output está correto:
pytest tests/e2e/test_snapshots.py --snapshot-update
```

---

## 3. Organização no Projeto

```
tests/e2e/
├── __snapshots__/
│   ├── test_snapshots/                # Dashboard states básicos
│   │   ├── TestDashboardSnapshots.test_snapshot_dashboard_80x24.svg
│   │   ├── TestDashboardSnapshots.test_snapshot_dashboard_empty.svg
│   │   └── TestDashboardSnapshots.test_snapshot_dashboard_with_routine.svg
│   └── test_snapshot_cruds/           # CRUD modais + estados + métricas
│       ├── TestDashboardStateSnapshots.test_snapshot_dashboard_habit_done.svg
│       ├── TestDashboardStateSnapshots.test_snapshot_dashboard_habit_skipped.svg
│       ├── TestDashboardStateSnapshots.test_snapshot_dashboard_timer_running.svg
│       ├── TestHabitCrudSnapshots.test_snapshot_habit_*.svg (5 SVGs)
│       ├── TestMetricsSnapshots.test_snapshot_metrics_*.svg (2 SVGs)
│       ├── TestRoutineCrudSnapshots.test_snapshot_routine_*.svg (2 SVGs)
│       └── TestTaskCrudSnapshots.test_snapshot_task_*.svg (2 SVGs)
├── test_snapshots.py                  # 3 testes — dashboard básico
├── test_snapshot_cruds.py             # 14 testes — CRUD + estados + métricas
└── test_snapshot_coverage.py          # 9 testes — cobertura comportamental
```

Os SVGs em `__snapshots__/` são rastreados pelo git. São a "verdade visual" do projeto — qualquer mudança neles deve ser revisada no MR.

---

## 4. Inventário de Baselines

| Categoria                               | Testes | Baselines |
| --------------------------------------- | ------ | --------- |
| Dashboard (empty, routine, 80x24)       | 3      | 3 SVGs    |
| CRUD modais (routines, habits, tasks)   | 8      | 8 SVGs    |
| Quick actions (done, skip modals)       | 2      | 2 SVGs    |
| Dashboard states (done, skipped, timer) | 3      | 3 SVGs    |
| Metrics (7-day mixed, streak perfeito)  | 2      | 3 SVGs    |
| **Total**                               | **17** | **19**    |

---

## 5. Limitação de CI — Incompatibilidade de Versionamento

Snapshots estão **excluídos de todo CI** (GitLab, GitHub, pre-push hook):

```
Python 3.14 -> pytest 8.4.2 (reportinfo() retorna str | PathLike)
    -> pytest-textual-snapshot 1.1.0 (espera só str) -> CRASH
```

- Monkey-patch em `tests/e2e/conftest.py` resolve localmente
- pytest-textual-snapshot não lançou fix upstream
- **Decisão:** aceitar como limitação — snapshots continuam local-only

**Exclusões configuradas:**

- `.gitlab-ci.yml`: `--ignore=tests/e2e/test_snapshots.py --ignore=tests/e2e/test_snapshot_cruds.py --ignore=tests/e2e/test_snapshot_coverage.py`
- `.github/workflows`: mesmas exclusões
- `pre-push hook`: mesmas exclusões

---

## 6. Gaps sem Baseline

1. **Agenda panel com blocos renderizados** — alta prioridade
2. **Help overlay** — baixa prioridade
3. **Telas secundárias** (Routines, Habits, Tasks, Timer screens)
4. **Layout responsivo 160 colunas**
5. **Timer live updates** — removido por flakiness

---

## 7. Monitoramento

Acompanhar releases de `pytest-textual-snapshot` no PyPI. Quando versao >1.1.0 sair com fix:

1. Remover monkey-patch do conftest.py
2. Remover `--ignore` dos CIs
3. Adicionar job `test:snapshots` no pipeline
4. Definir politica de aprovação (PR review para diff de baseline)

---

## 8. O que Testar com Snapshots

### Prioridade alta (implementado)

- Dashboard vazio (sem rotina) — placeholder com hint
- Dashboard com rotina ativa + hábitos + tasks — estado padrão
- Dashboard 80x24 — responsividade mínima
- Modais CRUD (create, edit, delete, done, skip) para habits e tasks
- Dashboard states (done, skipped, timer running)
- Métricas (7-day mixed, streak perfeito)

### Prioridade média (futuro)

- Agenda com blocos sobrepostos (3 colunas)
- Agenda com blocos consecutivos
- Timer ativo com elapsed visível

### Prioridade baixa (futuro)

- Cada screen (Routines, Habits, Tasks, Timer) em estado padrão
- Help overlay (?) aberto
- Sidebar navigation highlights
- Layout responsivo em terminais menores (80x24 single-column, DT-065)
- Layout responsivo em 160 colunas (wide-screen)

---

## 9. Fluxo de Trabalho

### Ao criar novo snapshot test

1. Escrever o teste em `tests/e2e/`
2. Rodar `pytest tests/e2e/test_novo.py` — vai falhar (sem baseline)
3. Abrir o report HTML, verificar visualmente
4. Se correto: `pytest tests/e2e/test_novo.py --snapshot-update`
5. Commitar o SVG junto com o teste

### Ao alterar renderização visual

1. Rodar `pytest tests/e2e/test_snapshots.py tests/e2e/test_snapshot_cruds.py` — falhas esperadas
2. Verificar cada diff no report HTML
3. Se todas as mudanças são intencionais: `pytest tests/e2e/ --snapshot-update`
4. Commitar SVGs atualizados com mensagem descritiva

### Ao receber falha local inesperada

1. Comparar SVGs — identificar a mudança visual
2. Se regressão: corrigir código
3. Se mudança intencional esquecida: atualizar baselines

---

## 10. Relação com Outros Tipos de Teste

| Tipo        | Valida                    | Ferramenta                     |
| ----------- | ------------------------- | ------------------------------ |
| Unit        | Lógica de negócio isolada | pytest + mocks                 |
| Integration | Service + DB              | pytest + test engine           |
| E2E (pilot) | Fluxos de interação       | pytest-asyncio + Textual pilot |
| Snapshot    | Renderização visual       | pytest-textual-snapshot        |
| BDD         | Cenários de aceite        | pytest-bdd + Gherkin           |

Snapshot tests NÃO substituem testes com pilot. O pilot valida "pressionar Tab foca o próximo panel" (lógica). O snapshot valida "o panel focado tem borda branca e o desfocado tem borda cinza" (visual).
