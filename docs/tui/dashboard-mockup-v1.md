# Dashboard Redesign: Proposta Completa

**Data:** 2026-02-20

**Contexto:** Evolucao do dashboard basico (3 cards) para dashboard rico com alta densidade, timeline visual e quick actions.

**Referencia:** ADR-031, BR-TUI-003, BR-TUI-008

---

## 1. Mockup: Visao Geral (terminal 120x40)

```
┌──────────┬──────────────────────────────────────────────────────────────────────────────────────────────┐
│          │ ┌─ DASHBOARD ─────────────────────────────────────────────── Qui 20 Fev 2026 ─────────┐      │
│  ▸ Dash  │ │  Rotina Matinal                      6/10 ▪▪▪▪▪▪░░░░ 60%   3 tasks   ▶ 25:43        │      │
│    Rotin │ └─────────────────────────────────────────────────────────────────────────────────────┘      │
│    Habit │                                                                                              │
│    Tasks │ ┌─ Timeline ───────────────────────────────────────────────────────────────────────────────┐ │
│    Timer │ │  06    07    08    09    10    11    12    13    14▼   15    16    17    18    19    20  │ │
│          │ │  ├─────┤├────┤├─────────┤          ├─────┤├────▓▓▓▓▓▓┤          ├─────────┤├────┤        │ │
│          │ │  Gym    Ing   Leitura              Almoco  Deep Work            Dev        Corr          │ │
│          │ │  ✓done  ✓done ✓done                ✓done  ▶running             ○pend      ○pend          │ │
│          │ └──────────────────────────────────────────────────────────────────────────────────────────┘ │
│          │                                                                                              │
│          │ ┌─ Habitos Hoje ──── 6/10 ─────────────┐  ┌─ Timer ────────────────────────────────────────┐ │
│          │ │                                      │  │                                                │ │
│          │ │  ✓  Gym          07:00-07:55   55m   │  │              ◉  25:43                          │ │
│          │ │  ✓  Ingles       08:30-09:00   30m   │  │              Deep Work                         │ │
│          │ │  ✓  Leitura      09:00-09:45   45m   │  │              ▶ RUNNING                         │ │
│          │ │  ✓  Meditacao    10:00-10:20   20m   │  │                                                │ │
│          │ │  ✓  Almoco       12:00-12:45   45m   │  │   Sessoes hoje: 3  │  Total: 2h 15m            │ │
│          │ │  ✓  Deep Work    14:00-▶ now   25m+  │  │                                                │ │
│          │ │  ·  Dev          16:00         60m   │  │   [s]tart  [p]ause  [enter]stop  [c]ancel      │ │
│          │ │  ·  Corrida      18:00         40m   │  └────────────────────────────────────────────────┘ │
│          │ │  ·  Journaling   21:00         15m   │                                                     │
│          │ │  ·  Revisao      21:30         30m   │  ┌─ Metricas ─────────────────────────────────────┐ │
│          │ │                                      │  │                                                │ │
│          │ │  [enter] marcar  [k] skip            │  │  Streak atual ···· 12 dias                     │ │
│          │ └──────────────────────────────────────┘  │  Melhor streak ··· 28 dias                     │ │
│          │                                           │  Completude 7d ··· ▪▪▪▪▪▪▪░░░  72%             │ │
│          │ ┌─ Tarefas ──── 3 pendentes ───────────┐  │  Completude 30d ·· ▪▪▪▪▪▪░░░░  63%             │ │
│          │ │                                      │  │                                                │ │
│          │ │  ! Relatorio Q1      alta   Qui 20   │  │  Ultimos 7 dias:                               │ │
│          │ │  ▪ Code review       media  Qui 20   │  │  Seg ▪▪▪▪▪▪▪▪░░  8/10                          │ │
│          │ │  ▪ Email cliente     media  Sex 21   │  │  Ter ▪▪▪▪▪▪▪▪▪░  9/10                          │ │
│          │ │                                      │  │  Qua ▪▪▪▪▪▪▪░░░  7/10                          │ │
│          │ │  [enter] detalhes  [c] concluir      │  │  Qui ▪▪▪▪▪▪░░░░  6/10  ← hoje                  │ │
│          │ └──────────────────────────────────────┘  │                                                │ │
│          │                                           │  [f] filtrar periodo                           │ │
│          │                                           └────────────────────────────────────────────────┘ │
├──────────┴──────────────────────────────────────────────────────────────────────────────────────────────┤
│  Rotina Matinal              │  ▶ Deep Work 25:43             │  Qui 20 Fev 2026  14:32                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Anatomia do Layout

O dashboard esta dividido em 5 zonas verticais:

```
┌──────────┬──────────────────────────────────────────────────┐
│          │  ZONA 1: Header Bar (1 linha)                    │
│ Sidebar  │  ZONA 2: Timeline (4 linhas)                     │
│ (fixa)   │  ZONA 3: Grid 2 colunas (scrollable)             │
│          │    ├─ Col Esq: Habitos + Tarefas                 │
│          │    └─ Col Dir:  Timer + Metricas                 │
├──────────┴──────────────────────────────────────────────────┤
│  ZONA 4: Status Bar (1 linha, fixa)                         │
└─────────────────────────────────────────────────────────────┘
```

### Zona 1: Header Bar

Barra compacta com contexto imediato. Uma unica linha densa:

```
┌─ DASHBOARD ────────────────────────────────────────── Qui 20 Fev 2026 ────────┐
│  Rotina Matinal                      6/10 ▪▪▪▪▪▪░░░░ 60%   3 tasks   ▶ 25:43  │
└───────────────────────────────────────────────────────────────────────────────┘
```

Conteudo (esquerda → direita):

- Nome da rotina ativa (ou "[Sem rotina]")
- Progresso do dia: X/Y habitos + barra visual + percentual
- Tarefas pendentes: contagem
- Timer ativo: icone + tempo (ou vazio)
- Data atual (extrema direita do titulo do card)

### Zona 2: Timeline Visual

Representacao horizontal do dia em blocos de tempo. Cada bloco ocupa espaco proporcional a duracao.

```
┌─ Timeline ───────────────────────────────────────────────────────────────────┐
│  06    07    08    09    10    11    12    13    14▼   15    16    17    18  │
│  ├─────┤├────┤├─────────┤          ├─────┤├────▓▓▓▓▓▓┤          ├────┤       │
│  Gym    Ing   Leitura              Almoco  Deep Work            Corrida      │
│  ✓done  ✓done ✓done                ✓done  ▶running             ○pend         │
└──────────────────────────────────────────────────────────────────────────────┘
```

Elementos visuais:

- **Regua de horas:** marcadores a cada hora (06-22)
- **Blocos de tempo:** `├────┤` para eventos, largura proporcional a duracao
- **Bloco ativo:** `▓▓▓▓▓▓` preenchimento denso com cor $primary
- **Marcador "agora":** `▼` na posicao da hora atual na regua
- **Status abaixo de cada bloco:** `✓done` (verde), `▶running` (purple), `○pend` (muted), `✗skip` (amarelo)
- **Gaps:** espacos vazios entre blocos (horarios livres)
- **Conflitos:** blocos sobrepostos em cor $error

Regras de rendering:

- Cada hora ≈ 6 caracteres de largura (ajustavel ao terminal)
- Eventos < 15min: exibe apenas icone de status, sem label
- Scroll horizontal se dia ultrapassa largura do terminal
- Hora atual sempre visivel (auto-scroll)

### Zona 3: Grid de Cards (2 colunas)

#### Coluna Esquerda

**Card "Habitos Hoje"** (ocupa ~60% da altura):

```
┌─ Habitos Hoje ──── 6/10 ────────────────┐
│                                         │
│  ✓  Gym          07:00-07:55   55m      │
│  ✓  Ingles       08:30-09:00   30m      │
│  ✓  Leitura      09:00-09:45   45m      │
│  ✓  Meditacao    10:00-10:20   20m      │
│  ✓  Almoco       12:00-12:45   45m      │
│  ✓  Deep Work    14:00-▶ now   25m+     │
│  ·  Dev          16:00         60m      │
│  ·  Corrida      18:00         40m      │
│  ·  Journaling   21:00         15m      │
│  ·  Revisao      21:30         30m      │
│                                         │
│  [enter] marcar  [k] skip               │
└─────────────────────────────────────────┘
```

Cada linha de habito:

- **Indicador de status:** `✓` (done, verde), `✗` (skipped, amarelo), `!` (missed/overdue, vermelho), `·` (pending, muted), `▶` (running, purple)
- **Nome:** ate 14 caracteres, truncado com `...`
- **Horario:** inicio-fim (ou inicio + `▶ now` se ativo)
- **Duracao:** tempo planejado ou real
- **Titulo do card:** inclui contador `X/Y`
- **Quick actions:** `enter` no item selecionado abre menu (Done/Skip), `k` para skip rapido
- **Cursor:** item atualmente focado tem fundo `$surface-alt`
- **Scroll vertical** se lista excede altura do card

**Card "Tarefas"** (ocupa ~40% da altura):

```
┌─ Tarefas ──── 3 pendentes ──────────────┐
│                                         │
│  ! Relatorio Q1      alta   Qui 20      │
│  ▪ Code review       media  Qui 20      │
│  ▪ Email cliente     media  Sex 21      │
│                                         │
│  [enter] detalhes  [c] concluir         │
└─────────────────────────────────────────┘
```

Cada linha de tarefa:

- **Indicador de prioridade:** `!` (alta, vermelho), `▪` (media, amarelo), `·` (baixa, muted)
- **Nome:** ate 20 caracteres
- **Prioridade:** texto
- **Deadline:** dia abreviado (Qui 20, Sex 21...)
- **Overdue:** linha inteira em cor $error se passou do prazo
- **Quick actions:** `enter` para detalhes, `c` para marcar concluida

#### Coluna Direita

**Card "Timer"** (ocupa ~45% da altura):

```
┌─ Timer ────────────────────────────────────────┐
│                                                │
│              ◉  25:43                          │
│              Deep Work                         │
│              ▶ RUNNING                         │
│                                                │
│   Sessoes hoje: 3  │  Total: 2h 15m            │
│                                                │
│   [s]tart  [p]ause  [enter]stop  [c]ancel      │
└────────────────────────────────────────────────┘
```

Elementos:

- **Display principal:** tempo em fonte grande (numeros ASCII art opcional para terminais largos)
- **Evento associado:** nome do habito/tarefa em timer
- **Status:** `▶ RUNNING` (verde pulsante), `⏸ PAUSED` (amarelo), `⏹ IDLE` (muted)
- **Resumo do dia:** sessoes concluidas + tempo total acumulado
- **Keybindings:** contextuais (so mostra `[p]ause` se running, `[s]tart` se idle)
- **Se nenhum timer ativo:** exibe mensagem + ultimo timer concluido

**Card "Metricas"** (ocupa ~55% da altura):

```
┌─ Metricas ────────────────────────────────────┐
│                                               │
│  Streak atual ···· 12 dias                    │
│  Melhor streak ··· 28 dias                    │
│  Completude 7d ··· ▪▪▪▪▪▪▪░░░  72%            │
│  Completude 30d ·· ▪▪▪▪▪▪░░░░  63%            │
│                                               │
│  Ultimos 7 dias:                              │
│  Seg ▪▪▪▪▪▪▪▪░░  8/10                         │
│  Ter ▪▪▪▪▪▪▪▪▪░  9/10                         │
│  Qua ▪▪▪▪▪▪▪░░░  7/10                         │
│  Qui ▪▪▪▪▪▪░░░░  6/10  <- hoje                │
│                                               │
│  [f] filtrar periodo                          │
└───────────────────────────────────────────────┘
```

Elementos:

- **Streak:** contador de dias consecutivos com >= 70% completude
- **Barras de completude:** 7 dias e 30 dias com percentual
- **Historico semanal:** barra por dia com contagem X/Y
- **Dia atual destacado:** seta indicadora
- **Cores das barras:** verde (>= 80%), amarelo (50-79%), vermelho (< 50%)
- **Filtro de periodo:** `f` permite alternar entre 7d, 14d, 30d

### Zona 4: Status Bar

Ja definida em BR-TUI-007. Sem alteracoes, exceto alinhamento visual:

```
├──────────┴──────────────────────────────────────────────────────────────────┤
│  Rotina Matinal        │  ▶ Deep Work 25:43       │  Qui 20 Fev 2026 14:32  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Hierarquia de Widgets

Novos widgets necessarios alem dos ja definidos no ADR-031:

```
src/timeblock/tui/
├── widgets/
│   ├── card.py              # (existente) Card generico
│   ├── sidebar.py           # (existente) Menu lateral
│   ├── status_bar.py        # (existente) Barra inferior
│   ├── confirm_dialog.py    # (existente) Dialog confirmacao
│   ├── header_bar.py        # [NOVO] Barra de contexto do dashboard
│   ├── timeline.py          # [NOVO] Timeline horizontal do dia
│   ├── habit_list.py        # [NOVO] Lista de habitos com quick actions
│   ├── task_list.py         # [NOVO] Lista de tarefas com prioridade
│   ├── timer_display.py     # [NOVO] Display do timer com estado
│   ├── metrics_panel.py     # [NOVO] Painel de metricas/streaks
│   └── progress_bar.py      # [NOVO] Barra de progresso ASCII reutilizavel
```

Composicao da DashboardScreen:

```python
class DashboardScreen(Screen):
    """Dashboard principal com layout hibrido."""

    def compose(self) -> ComposeResult:
        yield HeaderBar(id="header-bar")
        yield TimelineWidget(id="timeline")
        with Horizontal(id="grid"):
            with Vertical(id="col-left"):
                yield HabitListWidget(id="habits-today")
                yield TaskListWidget(id="tasks-pending")
            with Vertical(id="col-right"):
                yield TimerDisplayWidget(id="timer-display")
                yield MetricsPanelWidget(id="metrics-panel")
```

---

## 4. Layout TCSS

```css
/* dashboard.tcss */

#header-bar {
  height: 3;
  margin: 0 1;
  background: $surface-alt;
  border: round $primary;
  padding: 0 2;
}

#timeline {
  height: 6;
  margin: 1 1 0 1;
  background: $surface-alt;
  border: round $primary;
  padding: 0 1;
}

#grid {
  height: 1fr;
  margin: 0 1;
}

#col-left {
  width: 1fr;
  margin-right: 1;
}

#col-right {
  width: 1fr;
}

#habits-today {
  height: 3fr;
  border: round $primary;
  margin-bottom: 1;
  padding: 1 2;
}

#tasks-pending {
  height: 2fr;
  border: round $primary;
  padding: 1 2;
}

#timer-display {
  height: 2fr;
  border: round $primary;
  margin-bottom: 1;
  padding: 1 2;
}

#metrics-panel {
  height: 3fr;
  border: round $primary;
  padding: 1 2;
}
```

---

## 5. Responsividade

O dashboard deve funcionar em diferentes tamanhos de terminal:

```
Terminal >= 120 colunas (ideal):
  Layout completo conforme mockup (2 colunas, timeline expandida)

Terminal 80-119 colunas (compacto):
  Timeline: menos horas visiveis, scroll horizontal
  Cards: 2 colunas mantidas, conteudo truncado
  Metricas: historico reduzido para 3 dias

Terminal < 80 colunas (minimal):
  Layout 1 coluna (cards empilhados, vertical scroll)
  Timeline: oculta (ou reduzida a barra de progresso simples)
  Metricas: apenas streak + completude 7d
```

Implementacao via Textual CSS media queries:

```css
/* Compacto */
@media (width < 120) {
  #timeline {
    height: 4;
  }
  .habit-name {
    max-width: 10;
  }
}

/* Minimal */
@media (width < 80) {
  #grid {
    layout: vertical;
  }
  #col-right {
    width: 100%;
  }
  #timeline {
    display: none;
  }
}
```

---

## 6. Interatividade e Keybindings do Dashboard

### Navegacao entre zonas

O dashboard tem 4 zonas focaveis. `Tab` e `Shift+Tab` navegam entre elas:

```
Tab order: Timeline → Habitos → Tarefas → Timer → Metricas → (cicla)
```

### Keybindings por zona

**Timeline (quando focada):**

- `left`/`right`: scroll horizontal
- `enter`: navega para screen do evento selecionado (Habits ou Tasks)

**Habitos (quando focado):**

- `up`/`down` ou `j`/`k`: navegar entre itens
- `enter`: marcar done (abre prompt de duracao)
- `k`: skip rapido (abre prompt de categoria)
- `g`: ir para screen de Habitos (visao completa)

**Tarefas (quando focado):**

- `up`/`down` ou `j`/`k`: navegar entre itens
- `enter`: ver detalhes
- `c`: marcar concluida
- `g`: ir para screen de Tarefas

**Timer (quando focado):**

- `s`: start (se idle)
- `p`: pause/resume
- `enter`: stop
- `c`: cancel
- `g`: ir para screen do Timer

**Metricas (quando focado):**

- `f`: alternar filtro de periodo (7d → 14d → 30d → 7d)
- `g`: ir para screen de Reports (quando implementado)

---

## 7. Atualizacao BR-TUI-003 (Proposta)

### BR-TUI-003: Dashboard Screen (REVISADA)

**Descricao:** O Dashboard exibe visao completa e interativa do dia: header com contexto, timeline visual, habitos com quick actions, tarefas pendentes, timer ativo e metricas de desempenho. Layout hibrido com timeline no topo e grid de cards abaixo. Alta densidade informacional.

**Regras:**

1. **Header Bar:** exibe rotina ativa, progresso do dia (X/Y + barra + %), tarefas pendentes, timer ativo e data
2. **Timeline:** representacao horizontal do dia com blocos proporcionais a duracao, marcador "agora", status por cor
3. **Card Habitos:** lista instancias do dia com status, horario, duracao. Quick actions: `enter`=done, `k`=skip
4. **Card Tarefas:** lista tarefas pendentes com prioridade, deadline. Quick actions: `enter`=detalhes, `c`=concluir
5. **Card Timer:** display do timer ativo (ou ultimo concluido), sessoes do dia, keybindings contextuais
6. **Card Metricas:** streak atual/melhor, completude 7d/30d com barras, historico semanal por dia
7. **Responsividade:** 3 breakpoints (>=120 cols: completo, 80-119: compacto, <80: minimal empilhado)
8. **Navegacao:** Tab entre zonas, keybindings de zona ativa, `g` para navegar a screen completa
9. **Refresh:** dados atualizados ao entrar na screen (on_focus) e apos qualquer quick action
10. **Timer update:** se timer ativo, header e card Timer atualizam a cada segundo
11. Se nao ha rotina ativa, header exibe "[Sem rotina]" com orientacao para criar/ativar

**Testes:**

- `test_br_tui_003_header_shows_routine_and_progress`
- `test_br_tui_003_header_shows_no_routine_message`
- `test_br_tui_003_timeline_renders_day_blocks`
- `test_br_tui_003_timeline_shows_current_time_marker`
- `test_br_tui_003_timeline_shows_event_status_colors`
- `test_br_tui_003_habits_list_with_status_and_time`
- `test_br_tui_003_habits_quick_done_action`
- `test_br_tui_003_habits_quick_skip_action`
- `test_br_tui_003_tasks_sorted_by_priority`
- `test_br_tui_003_tasks_overdue_highlighted`
- `test_br_tui_003_timer_shows_active_session`
- `test_br_tui_003_timer_shows_idle_state`
- `test_br_tui_003_metrics_shows_streak`
- `test_br_tui_003_metrics_shows_weekly_history`
- `test_br_tui_003_metrics_period_filter`
- `test_br_tui_003_responsive_compact_layout`
- `test_br_tui_003_responsive_minimal_layout`
- `test_br_tui_003_tab_navigates_zones`
- `test_br_tui_003_refreshes_on_focus`
- `test_br_tui_003_refreshes_after_quick_action`

---

## 8. Novos Widgets: Descricao Tecnica

### TimelineWidget

Widget customizado que renderiza a timeline horizontal do dia.

```python
class TimelineWidget(Widget):
    """Timeline horizontal do dia com blocos de tempo proporcionais."""

    events: reactive[list] = reactive(list)
    current_hour: reactive[float] = reactive(0.0)
    scroll_offset: reactive[int] = reactive(0)

    # Configuracao
    HOURS_START = 6   # Primeira hora visivel
    HOURS_END = 23    # Ultima hora visivel
    CHARS_PER_HOUR = 6  # Largura base por hora

    def render(self) -> RenderableType:
        """Renderiza regua + blocos + labels + status."""
        ...

    def on_key(self, event: Key) -> None:
        """Scroll horizontal com left/right."""
        ...
```

Dados de entrada (via service):

- Lista de eventos do dia (habitos + tarefas com horario)
- Status de cada evento (done, running, pending, skipped, missed)
- Hora atual

### MetricsPanelWidget

Widget que calcula e exibe metricas de desempenho.

```python
class MetricsPanelWidget(Widget):
    """Painel de metricas: streaks, completude, historico."""

    period_days: reactive[int] = reactive(7)

    def compute_streak(self, daily_completions: list[float]) -> int:
        """Calcula streak atual (dias consecutivos >= 70%)."""
        ...

    def render_progress_bar(self, value: float, width: int = 10) -> str:
        """Renderiza ▪▪▪▪▪▪░░░░ com cor contextual."""
        ...
```

Dados de entrada (via service):

- Completude diaria dos ultimos N dias
- Streak atual e melhor streak (calculados no widget ou no service)

### ProgressBarWidget (reutilizavel)

Widget compacto para barras de progresso em qualquer contexto.

```python
class ProgressBar(Widget):
    """Barra de progresso ASCII: ▪▪▪▪▪▪░░░░ 60%"""

    value: reactive[float] = reactive(0.0)  # 0.0 a 1.0
    width: int = 10
    show_percentage: bool = True

    # Cores por faixa
    COLOR_HIGH = "$success"     # >= 80%
    COLOR_MED = "$warning"      # 50-79%
    COLOR_LOW = "$error"        # < 50%
```

---

## 9. Impacto na Package Structure

Adicoes ao ADR-031 secao 3:

```
src/timeblock/tui/
├── widgets/
│   ├── __init__.py
│   ├── card.py
│   ├── sidebar.py
│   ├── status_bar.py
│   ├── confirm_dialog.py
│   ├── header_bar.py          # [NOVO]
│   ├── timeline.py            # [NOVO]
│   ├── habit_list.py          # [NOVO]
│   ├── task_list.py           # [NOVO]
│   ├── timer_display.py       # [NOVO]
│   ├── metrics_panel.py       # [NOVO]
│   └── progress_bar.py        # [NOVO]
├── styles/
│   ├── theme.tcss
│   └── dashboard.tcss         # [NOVO] Estilos especificos do dashboard
```

---

## 10. Impacto no Roadmap (Sprint 3 expandida)

O Sprint 3 original era:

```
Sprint 3: Dashboard funcional com dados reais
  S3.1: BR-TUI-003 Dashboard com 3 cards de resumo
```

Proposta revisada:

```
Sprint 3: Dashboard completo (2-3 entregas)

  S3.1: Foundation
    - HeaderBar widget
    - TimelineWidget (rendering basico, sem interatividade)
    - DashboardScreen com compose() e layout TCSS
    - Testes: header, timeline rendering, layout zones

  S3.2: Cards interativos
    - HabitListWidget com quick actions (done/skip)
    - TaskListWidget com prioridade e conclusao
    - TimerDisplayWidget integrado com TimerService
    - Testes: quick actions, cursor navigation, refresh

  S3.3: Metricas + Polish
    - MetricsPanelWidget com streaks e historico
    - ProgressBar reutilizavel
    - Responsividade (3 breakpoints)
    - Tab navigation entre zonas
    - Testes: metricas, responsividade, tab order
```

---

## 11. Paleta de Cores Aplicada

Referencia rapida da paleta (definida no ADR-031 secao 7) aplicada ao dashboard:

| Elemento                 | Cor             | Variavel TCSS  |
| ------------------------ | --------------- | -------------- |
| Fundo principal          | #1E1E2E         | $surface       |
| Fundo cards/elevados     | #2A2A3E         | $surface-alt   |
| Bordas de cards          | #7C4DFF         | $primary       |
| Texto principal          | #CDD6F4         | $on-surface    |
| Labels e metadados       | #6C7086         | $muted         |
| Done/Success             | #A6E3A1         | $success       |
| Pending/Warning          | #F9E2AF         | $warning       |
| Missed/Error/Overdue     | #F38BA8         | $error         |
| Timer running            | #B388FF         | $primary-light |
| Cursor/foco              | #2A2A3E + borda | $surface-alt   |
| Barra progresso preench. | Contextual      | (por faixa)    |
| Barra progresso vazia    | #6C7086         | $muted         |

---

## 12. Diagrama de Navegacao Atualizado (ADR-031 secao 4)

Substituicao do diagrama basico por:

```
┌──────────┬──────────────────────────────────────────────────────────────┐
│          │  ┌─ Header Bar ──────────────────────────────────── Data ──┐ │
│  Sidebar │  │  Rotina  │  Progresso  │  Tasks  │  Timer               │ │
│          │  └─────────────────────────────────────────────────────────┘ │
│ ▸[1] D   │  ┌─ Timeline ──────────────────────────────────────────────┐ │
│  [2] R   │  │  06  07  08 ···  14▼ ···  20  21  22                    │ │
│  [3] H   │  │  ├──┤├──┤├────┤  ├▓▓▓▓┤      ├──┤├──┤                   │ │
│  [4] T   │  └─────────────────────────────────────────────────────────┘ │
│  [5] M   │  ┌─ Habitos ──────────────┐  ┌─ Timer ─────────────────────┐ │
│          │  │  ✓ Gym      07:00 55m  │  │       ◉ 25:43               │ │
│  ─────   │  │  ✓ Ingles   08:30 30m  │  │       Deep Work ▶ RUNNING   │ │
│  q quit  │  │  · Dev      16:00 60m  │  │  Sessoes: 3 │ Total: 2h15m  │ │
│  ? help  │  │  [enter] [k]           │  └─────────────────────────────┘ │
│          │  └────────────────────────┘  ┌─ Metricas ──────────────────┐ │
│          │  ┌─ Tarefas ──────────────┐  │  Streak: 12d │ Best: 28d    │ │
│          │  │  ! Relatorio   alta    │  │  7d ▪▪▪▪▪▪▪░ 72%            │ │
│          │  │  ▪ Review      media   │  │  Seg 8/10 Ter 9/10 Qua 7/10 │ │
│          │  │  [enter] [c]           │  │  [f] filtrar                │ │
│          │  └────────────────────────┘  └─────────────────────────────┘ │
├──────────┴──────────────────────────────────────────────────────────────┤
│  Rotina Matinal       │  ▶ Deep Work 25:43      │  Qui 20 Fev  14:32    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Resumo de Mudancas

| Documento         | Alteracao                                              |
| ----------------- | ------------------------------------------------------ |
| ADR-031 sec. 3    | Adicionar 7 novos widgets + dashboard.tcss             |
| ADR-031 sec. 4    | Substituir diagrama por versao detalhada               |
| BR-TUI-003        | Reescrita completa (6 regras → 11 regras, 6→20 testes) |
| BR-TUI-008        | Adicionar regras de responsividade e breakpoints       |
| Sprint 3          | Expandir de 1 entrega para 3 entregas                  |
| Package structure | 7 novos arquivos em widgets/, 1 novo TCSS              |
