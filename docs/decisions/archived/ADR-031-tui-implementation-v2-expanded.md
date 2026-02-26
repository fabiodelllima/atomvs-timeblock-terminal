# ADR-031: TUI Implementation with Textual

**Status**: Aceito

**Data**: 2026-02-05

**Atualizado**: 2026-02-20 (dashboard redesign)

**Supersedes**: ADR-006 (expande decisão original com detalhes de implementação)

## Contexto

O TimeBlock Organizer v1.6.0 possui CLI funcional com 95% dos comandos operacionais, 87% de cobertura e 778 testes. A interface CLI atende automação e uso pontual, mas a experiência interativa diária (consultar agenda, marcar hábitos, operar timer) requer navegação repetitiva entre comandos.

ADR-006 propôs Textual como framework TUI. Este ADR detalha a implementação concreta para v1.7.0.

Requisitos:

- Experiência interativa fluida para uso diário
- Coexistência CLI/TUI sem duplicação de lógica
- Visual moderno (Material-like) com cards, spacing e paleta consistente
- Testabilidade automatizada da TUI
- Textual como dependência opcional (CLI funciona sem ela)

## Decisão

### 1. Entry Point: Detecção Automática

`timeblock` sem argumentos abre a TUI. Com argumentos, executa CLI normalmente.

```python
# main.py
import sys

def main():
    if len(sys.argv) <= 1:
        from timeblock.tui.app import TimeBlockApp
        TimeBlockApp().run()
    else:
        app()  # Typer CLI
```

**Justificativa:** O uso mais frequente será interativo (abrir, consultar, operar). Automação via CLI permanece idêntica. `timeblock --help` continua funcionando pois tem argumento.

### 2. Framework: Textual

**Versão mínima:** textual >= 0.89.0
**Dependência:** Opcional (grupo `[tui]` no pyproject.toml)

```toml
[project.optional-dependencies]
tui = ["textual>=0.89.0"]
```

**Fallback:** Se textual não instalado e usuário executar sem args, exibir mensagem orientando instalação.

### 3. Package Structure

```
src/timeblock/
├── commands/           # CLI (existente, inalterado)
├── tui/                # TUI (novo)
│   ├── __init__.py
│   ├── app.py          # TimeBlockApp (classe principal)
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── routines.py
│   │   ├── habits.py
│   │   ├── tasks.py
│   │   └── timer.py
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── card.py             # Card genérico com borda e título
│   │   ├── sidebar.py          # Menu lateral de navegação
│   │   ├── status_bar.py       # Barra inferior (rotina/timer/hora)
│   │   ├── confirm_dialog.py   # Dialog de confirmação
│   │   ├── header_bar.py       # Barra de contexto do dashboard
│   │   ├── agenda.py           # Timeline vertical (Google Calendar)
│   │   ├── habit_list.py       # Lista de hábitos com quick actions
│   │   ├── task_list.py        # Lista de tarefas com prioridade
│   │   ├── timer_display.py    # Display do timer com estados
│   │   ├── metrics_panel.py    # Painel de métricas/streaks
│   │   └── progress_bar.py     # Barra de progresso ASCII reutilizável
│   └── styles/
│       ├── theme.tcss          # Estilos globais Material-like
│       └── dashboard.tcss      # Estilos específicos do dashboard
├── services/                   # Compartilhado (existente)
├── models/                     # Compartilhado (existente)
└── main.py                     # Entry point modificado
```

### 4. Screen Architecture

Cinco screens na v1.7.0, navegáveis por sidebar:

| Screen    | Funcionalidade                         | Keybinding |
| --------- | -------------------------------------- | ---------- |
| Dashboard | Visão geral do dia, quick actions      | `1` ou `d` |
| Routines  | CRUD rotinas, ativar/desativar         | `2` ou `r` |
| Habits    | Hábitos + instâncias, marcar done/skip | `3` ou `h` |
| Tasks     | CRUD tarefas, marcar completa          | `4` ou `t` |
| Timer     | Display live, start/pause/resume/stop  | `5` ou `m` |

**Dashboard layout (tela principal):**

```
┌──────────┬─────────────────────────────────────────────────────────────┐
│          │  ┌─ Header Bar ──────────────────────────────────── Data ─┐ │
│  Sidebar │  │  Rotina  │  Progresso  │  Tasks  │  Timer              │ │
│          │  └────────────────────────────────────────────────────────┘ │
│ ▸[1] D   │  ┌─ Agenda ──────────────┐  ┌─ Hábitos ───────────────────┐ │
│  [2] R   │  │  06:00 ┬ ▓▓▓▓▓▓▓▓▓▓▓  │  │  ✓ Gym      06:00  55m      │ │
│  [3] H   │  │        │ Gym   ✓ done │  │  ✓ Inglês   08:00  30m      │ │
│  [4] T   │  │  07:00 ┤              │  │  ▶ Deep W.  14:00  25m+     │ │
│  [5] M   │  │  08:00 ┬ ░░░░░░░░░░░  │  │  · Dev      16:00  60m      │ │
│          │  │        │ Inglês ✓     │  │  [enter] [s] [g]            │ │
│  ─────   │  │  ···   │              │  └─────────────────────────────┘ │
│  q quit  │  │ 14:32▸ ┤ ▓▓▓▓▓▓▓▓▓▓▓  │  ┌─ Tarefas ───────────────────┐ │
│  ? help  │  │        │ Deep W. ▶    │  │  !! Relatório   alta  venc  │ │
│          │  │  ···   │              │  │  !  Review      média       │ │
│          │  │  18:00 ┬ ┄┄┄┄┄┄┄┄┄┄┄  │  │  [enter] [c] [g]            │ │
│          │  │        │ Corrida ·    │  └─────────────────────────────┘ │
│          │  │  ···   │              │  ┌─ Timer ─────────────────────┐ │
│          │  │        │              │  │  ◉ 25:43  ▶ RUNNING         │ │
│          │  │        │              │  │  Sessões: 3  Total: 2h15m   │ │
│          │  │        │              │  └─────────────────────────────┘ │
│          │  │        │              │  ┌─ Métricas ──────────────────┐ │
│          │  │        │              │  │  Streak: 12d  (best: 28)    │ │
│          │  │        │              │  │  7d ▪▪▪▪▪▪▪░░░ 72%          │ │
│          │  │        │              │  │  Seg 8/10  Ter 9/10  ···    │ │
│          │  └───────────────────────┘  │  [f] filtrar                │ │
│          │                             └─────────────────────────────┘ │
├──────────┴─────────────────────────────────────────────────────────────┤
│  Rotina Matinal       │  ▶ Deep Work 25:43      │  Qui 20 Fev  14:32   │
└────────────────────────────────────────────────────────────────────────┘
```

**Mockup completo:** `docs/tui/dashboard-mockup-v3.md` (terminal 120x42 com todos os detalhes)

### 5. Session Management

Services recebem `Session` no construtor. A TUI tem lifecycle longo (minutos/horas), diferente da CLI (segundos).

**Estratégia:** Session-per-action (não session-per-screen).

```python
from contextlib import contextmanager
from sqlmodel import Session
from timeblock.database.engine import get_engine

@contextmanager
def get_session():
    """Cria session para uma operação atômica."""
    engine = get_engine()
    with Session(engine) as session:
        yield session
        session.commit()
```

**Cada operação TUI:**

1. Abre session via context manager
2. Instancia service com session
3. Executa operação
4. Session fecha automaticamente (commit ou rollback)

**Justificativa:** Evita sessions stale em TUI de longa duração. Cada ação vê dados frescos do banco. Consistente com CLI que já usa sessions curtas.

### 6. Data Flow

```
User Input (keybinding/click)
    │
    v
Screen Handler (método on_*)
    │
    v
get_session() context manager
    │
    v
Service.method(session, args)
    │
    v
Model/ORM operation
    │
    v
Session commit/rollback
    │
    v
Screen.refresh_data() → atualiza widgets
```

### 7. Visual Design: Material-like

**Paleta de cores (TCSS):**

```
$primary:       #7C4DFF   (deep purple)
$primary-light: #B388FF   (light purple)
$surface:       #1E1E2E   (dark surface)
$surface-alt:   #2A2A3E   (elevated surface)
$on-surface:    #CDD6F4   (text on dark)
$success:       #A6E3A1   (green - done)
$warning:       #F9E2AF   (yellow - pending)
$error:         #F38BA8   (red - missed/overdue)
$muted:         #6C7086   (secondary text)
```

**Card widget:**

- Borda arredondada (border: round $primary)
- Padding interno: 1 2 (vertical horizontal)
- Margin: 1
- Título em bold com cor contextual
- Conteúdo com texto muted para labels

**Spacing system:**

- Padding padrão: 1 (vertical), 2 (horizontal)
- Margin entre cards: 1
- Sidebar width: 22 caracteres fixo
- Content area: fluid

**Indicadores ASCII padronizados:**

| Indicador | Significado       | Cor              |
| --------- | ----------------- | ---------------- |
| ✓         | Done/concluído    | `$success`       |
| ✗         | Skipped           | `$warning`       |
| !         | Alta/missed       | `$error`         |
| !!        | Overdue + alta    | `$error` bold    |
| ▪         | Média             | `$warning`       |
| ·         | Baixa/pending     | `$muted`         |
| ▶         | Running           | `$primary-light` |
| ◼         | Sparkline esforço | contextual       |

**Agenda do Dia — legenda visual:**

| Padrão        | Significado       | Cor              |
| ------------- | ----------------- | ---------------- |
| ▓▓▓▓▓▓▓▓▓▓▓▓  | Bloco ativo       | `$primary-light` |
| ░░░░░░░░░░░░  | Bloco concluído   | `$success`       |
| ┄┄┄┄┄┄┄┄┄┄┄┄  | Bloco pendente    | `$muted`         |
| ╌╌╌╌╌╌╌╌╌╌╌╌  | Bloco skipado     | `$warning`       |
| · · · · · · · | Projeção (futuro) | `$muted` dim     |
| ┈ livre ┈     | Horário livre     | `$muted` dim     |

**Barras de progresso — cores por faixa:**

| Faixa  | Cor        |
| ------ | ---------- |
| ≥ 80%  | `$success` |
| 50–79% | `$warning` |
| < 50%  | `$error`   |

**Responsividade (3 breakpoints):**

| Breakpoint | Colunas | Layout                                                |
| ---------- | ------- | ----------------------------------------------------- |
| Completo   | ≥ 120   | Sidebar + Agenda vertical + Cards grid (2 subcolunas) |
| Compacto   | 80–119  | Sidebar + Agenda reduzida + Cards truncados           |
| Minimal    | < 80    | Sidebar + Cards empilhados (1 coluna), agenda oculta  |

### 8. Testing Strategy

**Framework:** Textual Pilot (built-in testing)

```python
async def test_dashboard_shows_active_routine():
    async with TimeBlockApp().run_test() as pilot:
        # Verificar que dashboard exibe rotina ativa
        assert pilot.app.query_one("#routine-name").renderable == "Rotina Matinal"
```

**Distribuição:**

| Tipo        | Escopo                                | Meta |
| ----------- | ------------------------------------- | ---- |
| Unit        | Widgets isolados, lógica de rendering | 60%  |
| Integration | Screen + Service (com DB)             | 30%  |
| E2E         | Navegação completa, flows de usuário  | 10%  |

**Naming:** Segue ADR-019: `test_br_tui_xxx_scenario`

### 9. Dependency Management

```toml
[project.optional-dependencies]
tui = ["textual>=0.89.0"]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
    "textual-dev>=1.0.0",  # Debug tools
]
```

**Import guard em main.py:**

```python
try:
    from timeblock.tui.app import TimeBlockApp
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False

# No entry point:
if len(sys.argv) <= 1:
    if HAS_TEXTUAL:
        TimeBlockApp().run()
    else:
        print("[WARN] TUI requer 'textual'. Instale com: pip install timeblock-organizer[tui]")
        print("       Uso CLI: timeblock --help")
```

## Alternativas Consideradas

### Textual sem detecção automática (subcomando `timeblock tui`)

**Pros:** Explícito, sem ambiguidade
**Contras:** Mais digitação para uso mais frequente, UX inferior

### Prompt Toolkit para TUI

**Pros:** Maduro, menos opinionado
**Contras:** Low-level, requer mais código para visual Material-like, não aproveita Rich

### Session-per-screen (em vez de session-per-action)

**Pros:** Menos overhead de conexão
**Contras:** Sessions stale em TUI longa, risco de dados desatualizados, inconsistência com CLI

### Timeline horizontal (barra de tempo no topo)

**Pros:** Mais compacta, ocupa menos espaço vertical
**Contras:** Pouco espaço para labels, não permite ver o dia inteiro de relance, perde a familiaridade com Google Calendar. A timeline vertical permite ver blocos de tempo com duração proporcional real e acomodar informações dentro de cada bloco (nome, status, duração).

## Consequências

### Positivas

- Experiência interativa rica para uso diário
- Visual moderno e consistente
- Compartilha 100% da lógica de negócios com CLI (services layer)
- Textual usa Rich internamente (já é dependência)
- Testes automatizados com Pilot
- CLI permanece funcional e independente
- Dashboard de alta densidade permite monitorar todo o dia sem navegar entre screens

### Negativas

- Nova dependência (textual ~15MB)
- Complexidade de manutenção em duas interfaces
- Testes TUI são assíncronos (pytest-asyncio necessário)
- TCSS é específico do Textual (vendor lock-in para styling)
- Dashboard com muitos widgets aumenta complexidade de testes (33 testes só para BR-TUI-003)

### Neutras

- CLI permanece interface primária para automação
- TUI é opcional via dependency group
- Não afeta pipeline CI/CD existente (testes TUI são adicionais)

## Validação

Consideramos acertada se:

- TUI abre em < 500ms
- Navegação entre screens < 100ms
- 80%+ cobertura no pacote tui/
- Zero regressão na CLI existente
- Timer display atualiza a cada segundo sem flicker
- Dashboard renderiza completo em < 200ms com 10+ eventos

## Implementação

### Sprint 1: Foundation

1. Criar estrutura de pacotes tui/
2. Implementar TimeBlockApp com sidebar navigation
3. Definir theme.tcss
4. Modificar main.py (entry point)
5. Screens placeholder (5 screens vazias com navegação funcional)

### Sprint 2: Navegação + Status

1. Sidebar widget funcional com indicador de screen ativa
2. Keybindings globais (quit, help, escape)
3. Status bar (rotina, timer, hora)
4. ConfirmDialog widget

### Sprint 3: Dashboard — Foundation

1. HeaderBar widget (rotina, progresso, tasks, timer, data)
2. AgendaWidget — rendering básico (régua de horas, blocos, marcador "agora")
3. DashboardScreen com compose() e layout TCSS (dashboard.tcss)
4. Testes: header, agenda rendering, layout zones

### Sprint 4: Dashboard — Cards Interativos

1. HabitListWidget com quick actions (done/skip)
2. TaskListWidget com prioridade e conclusão
3. TimerDisplayWidget integrado com TimerService
4. ProgressBar reutilizável
5. Testes: quick actions, cursor navigation, refresh

### Sprint 5: Dashboard — Métricas + Polish

1. MetricsPanelWidget com streaks, histórico e dot matrix
2. Responsividade (3 breakpoints via TCSS media queries)
3. Tab navigation entre zonas do dashboard
4. Agenda: conflitos lado a lado, blocos skipados, projeção
5. Testes: métricas, responsividade, tab order, estados alternativos

### Sprint 6: CRUD Screens

1. RoutinesScreen com CRUD completo
2. HabitsScreen com instâncias
3. TasksScreen com CRUD
4. Formulários inline

### Sprint 7: Timer Screen + Integração Final

1. TimerScreen com display live
2. Integração timer ↔ status bar ↔ dashboard
3. Testes completos de integração
4. Polish visual final

## Referências

- [ADR-006](ADR-006-textual-tui.md) — Decisão original Textual
- [ADR-007](ADR-007-service-layer.md) — Service Layer (consumida pela TUI)
- [Dashboard Mockup v3](../tui/dashboard-mockup-v3.md) — Mockup detalhado do dashboard
- [Textual Documentation](https://textual.textualize.io/)
- [Textual CSS Reference](https://textual.textualize.io/css_types/)
- [Material Design 3 Color System](https://m3.material.io/styles/color)
