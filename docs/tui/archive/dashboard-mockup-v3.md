# Dashboard Mockup v3 — Terminal 120x42

## Layout Principal: Timeline vertical (Google Calendar style) + Cards

```
┌────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┐
│            │ ┌─ DASHBOARD ─────────────────────────────────────────────── Quinta-feira, 20 de Fevereiro ─┐│
│  ◉ ATOMVS  │ │ Rotina Matinal  │  6/10 ▪▪▪▪▪▪░░░░ 60%  │  3 tasks pendentes  │  ▶ Deep Work       25:43  ││
│  ════════  │ └───────────────────────────────────────────────────────────────────────────────────────────┘│
│            │                                                                                              │
│  ▸ Dash    │ ┌─ Agenda do Dia ───────────────────────────┐ ┌─ Hábitos ─────────────────────────── 6/10 ──┐│
│    Rotin   │ │                                           │ │                                             ││
│    Tasks   │ │  06:00 ┬ Gym           ✓ done   55min     │ │  ✓  Inglês       08:00 ─ 08:30  30m  ◼◼     ││
│    Habit   │ │  06:30 │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    │ │  ✓  Gym          06:00 ─ 07:00  55m  ◼◼◼    ││
│    Timer   │ │  07:00 ┤ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    │ │  ✓  Leitura      09:00 ─ 10:00  58m  ◼◼◼    ││
│            │ │        │                                  │ │  ✓  Meditação    10:00 ─ 10:30  20m  ◼      ││
│            │ │  08:00 ┬ Inglês        ✓ done   30min     │ │  ▶  Deep Work    14:00 ─ 15:30  25m+ ◼◼◼    ││
│            │ │        │ ░░░░░░░░░░░░░░░░                 │ │  ✓  Almoço       12:00 ─ 13:00  45m  ◼◼     ││
│            │ │  08:30 ┤ ░░░░░░░░░░░░░░░░                 │ │  ·  Dev          16:00 ─ 17:00  60m  ───    ││
│            │ │        │                                  │ │  ·  Corrida      18:00 ─ 18:40  40m  ───    ││
│            │ │  09:00 ┬ Leitura       ✓ done   58min     │ │  ·  Revisão      21:30 ─ 22:00  30m  ───    ││
│            │ │        │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │ │  ·  Journaling   21:00 ─ 21:15  15m  ───    ││
│            │ │  10:00 ┬ Meditação     ✓ done   20min     │ │                                             ││
│            │ │        │ ░░░░░░░░░░░░░░░░░                │ │  [enter] done  [s] skip  [g] go to screen   ││
│            │ │  10:30 ┤                                  │ └─────────────────────────────────────────────┘│
│            │ │  11:00 │                                  │                                                │
│            │ │        │         ┈ livre ┈                │ ┌─ Tarefas ──────────────────── 3 pendentes ──┐│
│            │ │  12:00 ┬ Almoço        ✓ done   45min     │ │                                             ││
│            │ │  12:00 │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ │  !! Relatório Q1    Alta    Hoje     venc.  ││
│            │ │  13:00 ┤ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ │  !  Code review     Média   Hoje            ││
│            │ │        │                                  │ │  ·  Email cliente   Média   Sex 21          ││
│            │ │  14:00 ┬ Deep Work    ▶ running 25min+    │ │  ·  Docs sprint     Baixa   Seg 24          ││
│            │ │        │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │                                             ││
│            │ │  14:32▸┤ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │  [enter] detalhes  [c] concluir  [g] go     ││
│            │ │  15:00 │ · · · · · · · · · · · · · · · ·  │ └─────────────────────────────────────────────┘│
│            │ │  15:30 ┤                                  │                                                │
│            │ │  16:00 ┬ Dev          · pend    60min     │ ┌─ Timer ─────────────────────────────────────┐│
│            │ │        │ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │ │          ◉  25:43   ▶ RUNNING               ││
│            │ │  17:00 ┤ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │ │          Deep Work                          ││
│            │ │        │                                  │ │                                             ││
│            │ │  18:00 ┬ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄          │ │  Sessões: 3  │  Total: 2h 15m  │  Avg: 45m  ││
│            │ │        │ Corrida          · pend    40m   │ │  [s]tart  [p]ause  [enter]stop  [c]ancel    ││
│            │ │  18:40 ┤                                  │ └─────────────────────────────────────────────┘│
│            │ │  19:00 │                                  │                                                │
│            │ │        │         ┈ livre ┈                │ ┌─ Métricas ──────────────────────────────────┐│
│            │ │  20:00 │                                  │ │                                             ││
│            │ │  21:00 ┬ ┄┄┄┄┄┄┄┄┄┄                       │ │  Streak ·········  12 dias  (best: 28)      ││
│            │ │        │ Journaling       · pend    15m   │ │  Completude 7d ··  ▪▪▪▪▪▪▪░░░  72%          ││
│            │ │  21:15 ┤                                  │ │  Completude 30d ·  ▪▪▪▪▪▪░░░░  63%          ││
│            │ │  21:30 ┬ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄                │ │                                             ││
│            │ │        │ Revisão          · pend    30m   │ │  Seg ▪▪▪▪▪▪▪▪░░ 8/10  ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ · ·   ││
│            │ │  22:00 ┤ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄                │ │  Ter ▪▪▪▪▪▪▪▪▪░ 9/10  ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ·   ││
│            │ │        │                                  │ │  Qua ▪▪▪▪▪▪▪░░░ 7/10  ✓ ✓ ✓ ✓ ✓ ✓ ✓ · · ·   ││
│            │ │                                           │ │  Qui ▪▪▪▪▪▪░░░░ 6/10  ✓ ✓ ✓ ✓ ✓ ✓ · · · ·   ││
│            │ │                                           │ │                                    ← hoje   ││
│            │ │                                           │ │                                             ││
│  q quit    │ │                                           | │  [f] 7d/14d/30d                             ││
│  ──────────│ └───────────────────────────────────────────┘ └─────────────────────────────────────────────┘│
│  ? help    │                                                                                              │
├────────────┴──────────────────────────────────────────────────────────────────────────────────────────────┤
│  Rotina Matinal               │  Qui, 20 Fev 2026              14:32  │  ▶ Deep Work               25:43  │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Legenda Visual da Timeline (Agenda do Dia)

```
  Blocos concluídos (done):         ░░░░░░░░░░░░░░  cor $success (verde)
  Bloco ativo (running):            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  cor $primary-light (purple)
  Blocos pendentes (pending):       ┄┄┄┄┄┄┄┄┄┄┄┄┄┄  cor $muted (tracejado)
  Blocos skipados:                  ╌╌╌╌╌╌╌╌╌╌╌╌╌╌  cor $warning (amarelo, tracejado)
  Horários livres:                  ┈ livre ┈        texto dim centralizado
  Marcador "agora":                 14:32▸           seta na régua de horas
  Bloco projetado (continuação):    · · · · · · · ·  pontilhado após hora atual
  Conflito (overlap):               ████ ████        dois blocos lado a lado, cor $error
```

## Legenda Visual dos Cards

```
  Hábitos - Indicadores:
    ✓  done       ($success)       ◼◼◼  esforço relativo (mini sparkline)
    ▶  running    ($primary-light)
    ✗  skipped    ($warning)
    !  missed     ($error)
    ·  pending    ($muted)          ───  ainda sem dados

  Tarefas - Prioridade:
    !! overdue + alta  ($error, bold)
    !  alta            ($error)
    ▪  média           ($warning)
    ·  baixa           ($muted)

  Métricas - Histórico:
    ▪▪▪▪▪▪▪▪░░  barra de progresso (preenchido/vazio)
    ✓ ✓ ✓ · ·   dot matrix por hábito (done/pending)
```

## Detalhe: Conflito na Timeline

```
  09:00 ┬ ░░░░░░░░░░░░░░│░░░░░░░░░░░░░░░
        │ Leitura    ✓  │ Reunião    ✓
  10:00 ┤ ░░░░░░░░░░░░░░│
        │               │ Reunião (cont.)
  10:30 ┤               └░░░░░░░░░░░░░░░
```

## Detalhe: Timer em estado IDLE

```
  ┌─ Timer ─────────────────────────────────────┐
  │                                             │
  │          ◎  00:00   ⏹ IDLE                  │
  │          Nenhum timer ativo                 │
  │                                             │
  │  Último: Leitura  58m  (09:02─10:00)        │
  │                                             │
  │  Sessões: 3  │  Total: 2h 15m  │  Avg: 45m  │
  │  [s]tart novo timer                         │
  └─────────────────────────────────────────────┘
```

## Detalhe: Dashboard sem rotina ativa

```
  ┌─ DASHBOARD ──────────────────────────────────────────── Qui 20 Fev 2026 ──────┐
  │ [Sem rotina]   Crie uma rotina: timeblock routine add   ou   [2] Rotinas      │
  └───────────────────────────────────────────────────────────────────────────────┘
```

## Detalhe: Métricas com filtro 30d

```
  ┌─ Métricas ──── 30 dias ─────────────────────────────────┐
  │                                                         │
  │  Streak ·········  12 dias  (best: 28)                  │
  │  Completude 30d ·  ▪▪▪▪▪▪░░░░  63%                      │
  │                                                         │
  │  Jan 22 ░░░░░░░░░░  10/10       Fev 05 ░░░░░░░░░░ 10/10 │
  │  Jan 23 ░░░░░░░░░░  10/10       Fev 06 ░░░░░░░░░░ 10/10 │
  │  Jan 24 ░░░░░░░░░   9/10        Fev 07 ░░░░░░░░   8/10  │
  │  Jan 25 ░░░░░░░     7/10        Fev 08 ░░░░░░     6/10  │
  │  Jan 26 ░░░░░       5/10        Fev 09 ░░░░░░░░   8/10  │
  │  Jan 27 ░░░░░░░░    8/10        Fev 10 ░░░░░░░░   8/10  │
  │  ···                             ···                    │
  │  Fev 04 ░░░░░░░░░   9/10        Fev 20 ░░░░░░     6/10  │
  │                                                 ← hoje  │
  │  [f] 7d/14d/30d  [h] heatmap                            │
  └─────────────────────────────────────────────────────────┘
```
