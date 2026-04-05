# Developer Reference

Referência para retomada de contexto e consulta durante o desenvolvimento.

---

## 1. Setup do Ambiente

- **Python requerido:** 3.13+
- **Banco:** SQLite em `~/.local/share/atomvs/atomvs.db`
- **Logs:** JSON Lines em `~/.local/share/atomvs/logs/atomvs.jsonl`

```bash
git clone git@gitlab.com:delimafabio/atomvs-timeblock-terminal.git
cd atomvs-timeblock-terminal

python -m venv venv
source venv/bin/activate
pip install -e ".[tui,dev]"

# Verificação rápida
python -m pytest tests/ -x -q
ruff check .
atomvs     # Abre a TUI
```


---

## 2. Estrutura do Projeto

```plaintext
atomvs-timeblock-terminal/
├── src/timeblock/
│   ├── models/                  # SQLModel entities + enums
│   │   ├── enums.py             # Status, DoneSubstatus, SkipReason, TimerStatus
│   │   ├── habit.py             # Habit + Recurrence enum
│   │   ├── habit_instance.py
│   │   ├── routine.py
│   │   ├── task.py
│   │   └── event.py
│   ├── services/                 # Lógica de negócio (service layer)
│   ├── commands/                 # Comandos Typer (CLI)
│   └── tui/
│       ├── screens/dashboard/
│       │   ├── screen.py         # DashboardScreen (coordenador)
│       │   ├── loader.py         # load_instances, load_metrics
│       │   ├── crud_habits.py    # CRUD de hábitos
│       │   ├── crud_tasks.py     # CRUD de tarefas
│       │   └── crud_routines.py  # Seletor + deleção de rotinas
│       ├── widgets/              # FocusablePanel, FormModal, etc.
│       └── styles/               # Arquivos TCSS
├── tests/
│   ├── unit/                 # ~75% (BRs isoladas)
│   ├── integration/          # ~20% (service + DB)
│   ├── e2e/                  # ~5% (CLI/TUI completa)
│   └── bdd/                  # Cenários Gherkin (Given/When/Then)
├── docs/                     # Documentação (Diátaxis + arc42)
│   ├── tutorials/            # Aprendizado guiado
│   ├── guides/               # How-to práticos
│   ├── reference/            # Consulta factual (BRs, CLI, métricas)
│   │   └── business-rules/   # 14 módulos por domínio + index.md
│   ├── explanation/          # Conceitual (arquitetura, metodologia)
│   ├── decisions/            # 39 ADRs
│   └── diagrams/             # C4, sequências, estados
└── design/                   # Artefatos de design (untracked)
```

---

## 3. Enums — Nomes vs. Valores

- Os enums do domínio usam `StrEnum`.
- O `SkipReason` tem **nomes em inglês e valores em português**.
- Acessar sempre **por nome**, nunca por valor.

```python
# CORRETO — acesso por nome
DoneSubstatus["FULL"]          # → DoneSubstatus.FULL
SkipReason["HEALTH"]           # → SkipReason.HEALTH (valor: "saude")

# ERRADO — acesso por valor (falha em SkipReason)
DoneSubstatus("FULL")          # Funciona (nome == valor lowercase)
SkipReason("HEALTH")           # ValueError! Valor é "saude", não "HEALTH"
```

### Tabela completa

| Enum                 | Nome                                                                           | Valor                                                                             | Arquivo  |
| -------------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- | -------- |
| **Status**           | PENDING / DONE / NOT_DONE                                                      | pending / done / not_done                                                         | enums.py |
| **DoneSubstatus**    | FULL / OVERDONE / EXCESSIVE / PARTIAL                                          | full / overdone / excessive / partial                                             | enums.py |
| **NotDoneSubstatus** | SKIPPED_JUSTIFIED / SKIPPED_UNJUSTIFIED / IGNORED                              | skipped_justified / skipped_unjustified / ignored                                 | enums.py |
| **SkipReason**       | HEALTH / WORK / FAMILY / TRAVEL / WEATHER / LACK_RESOURCES / EMERGENCY / OTHER | saude / trabalho / familia / viagem / clima / falta_recursos / emergencia / outro | enums.py |
| **TimerStatus**      | RUNNING / PAUSED / DONE / CANCELLED                                            | running / paused / done / cancelled                                               | enums.py |
| **Recurrence**       | MONDAY..SUNDAY / WEEKDAYS / WEEKENDS / EVERYDAY                                | MONDAY..SUNDAY / WEEKDAYS / WEEKENDS / EVERYDAY                                   | habit.py |

> `Recurrence` é `Enum` (não `StrEnum`) e nome == valor (uppercase).

---

## 4. service_action

> Wrapper da TUI para chamadas de service. Encapsula session + commit + error handling.

```python
from timeblock.tui.session import service_action

# Assinatura
def service_action[T](action: Callable[[Session], T]) -> tuple[T | None, str | None]:
    ...

# Uso
result, error = service_action(lambda s: RoutineService(s).get_active_routine())
if error:
    self.notify(error, severity="error")
    return
# result contém o valor de retorno do service
```

- Sucesso: `(resultado, None)`.
- Falha: `(None, "mensagem de erro")`.

---

## 5. Armadilhas Conhecidas

### session.refresh() cross-session

- Instâncias criadas via `generate_instances` e depois passadas para outra session causam erro de detached instance.
- Nunca chamar `session.refresh()` em objetos de outra session.

### FormModal com apenas campos Select

- Campos `Select` do Textual não propagam submit via Enter.
- Formulários que têm apenas `Select` (sem `Input`) precisam de um `Button("Confirmar")` explícito para submit via teclado.

### on_focus vs on_descendant_focus

- `App.on_focus` não recebe eventos de widgets filhos — eles ficam no widget.
- Para reagir a foco de descendentes no nível do App ou Screen, usar `on_descendant_focus`.

### load_instances(None) retorna []

- Sem rotina ativa, o dashboard não deve exibir instâncias.
- O early return `if routine_id is None: return []` evita dados órfãos nos panels.

### max-height do FormModal

- 24 linhas é insuficiente para formulários com 4+ campos.
- Valor atual: 36 (em `styles/forms.tcss`).

### Routine usa campo name, não title

- O modelo `Routine` tem campo `name`.
- `Habit` e `Task` usam `title`.

---

## 6. Comandos de Teste

```bash
# Suíte completa
python -m pytest tests/ -x -q

# Por escopo
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/e2e/ -v

# Paralelo (CI)
python -m pytest tests/ -n auto --dist=loadfile

# Teste específico
python -m pytest tests/unit/test_services/test_routine_service.py -v -k "test_br_routine_001"

# Coverage
python -m pytest tests/ --cov=src/timeblock --cov-report=term-missing

# Linting
ruff check .
ruff format --check .
```

---

## 7. Formato de Commit

Tipos de commit: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`

```
type(scope): Descrição em português com inicial maiúscula
```

Exemplos reais do projeto:

```
feat(loader): Implementa load_metrics com filtro de rotina (DT-026)
fix(loader): Corrige elapsed pausado, detecta timer ativo e filtra por rotina (DT-054, DT-055, DT-049)
test(e2e): Remove xfails e corrige testes de métricas (DT-026)
docs(br): Quebra business-rules.md em 14 módulos por domínio (ADR-039 Fase 2)
refactor(widget): Extrai HIGHLIGHT_COLOR e _enter_placeholder_mode no FocusablePanel (DT-009, DT-010, DT-011)
```

---

## 8. Git Workflow

Gitflow:

- `develop` → feature branches → `main` (via MR).
- `--no-ff` não é suportado pelo `glab mr merge`.

```bash
# Branches partem de develop
git switch develop
git pull origin develop
git switch -c feat/minha-feature

# Push e MR
git push origin feat/minha-feature
glab mr create --target-branch develop --title "feat(scope): Descrição"

# Merge (via glab ou GitLab UI)
glab mr merge <id>
```

---

## 9. Mapa de Documentação (Diátaxis)

| Pasta            | Propósito          | Exemplos                                                                          |
| ---------------- | ------------------ | --------------------------------------------------------------------------------- |
| `tutorials/`     | Aprendizado guiado | Este documento                                                                    |
| `guides/`        | How-to práticos    | development-workflow, ci-optimization, testing-patterns, manual-testing-checklist |
| `reference/`     | Consulta factual   | business-rules/ (14 módulos), cli-reference, technical-debt, workflows, sprints   |
| `reference/tui/` | Specs TUI          | color-system, dashboard-cards-spec, mockup-v4                                     |
| `explanation/`   | Conceitual         | architecture, development-methodology, domain-concepts                            |
| `decisions/`     | ADRs (arc42 §9)    | 39 ADRs categorizados                                                             |
| `diagrams/`      | arc42 §5-7         | C4, sequências, estados, ER, atividade                                            |

---

**Última atualização:** 20 de Março de 2026
