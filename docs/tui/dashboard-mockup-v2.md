# Dashboard Mockup v2 — Terminal 120x42

## Layout Principal: Timeline vertical (Google Calendar style) + Cards

```
┌──────────┬─────────────────────────────────────────────────────────────────────────────────────────────┐
│          │ ┌─ DASHBOARD ──────────────────────────────────────────────────────── Qui 20 Fev 2026 ─────┐│
│  ◉ ATOMVS│ │ Rotina Matinal  6/10 ▪▪▪▪▪▪░░░░ 60%  │  3 tasks pendentes  │  ▶ Deep Work 25:43          ││
│  ════════│ └──────────────────────────────────────────────────────────────────────────────────────────┘│
│          │                                                                                             │
│ ▸ Dash   │ ┌─ Agenda do Dia ───────────────────────────┐ ┌─ Habitos ────── 6/10 ──────────────────────┐│
│   Rotin  │ │                                           │ │                                            ││
│   Habit  │ │  06:00 ┬ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    │ │  ✓  Gym          06:00─07:00   55m  ◼◼◼    ││
│   Tasks  │ │        │ Gym              ✓ done    55m   │ │  ✓  Ingles       08:00─08:30   30m  ◼◼     ││
│   Timer  │ │  07:00 ┤ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    │ │  ✓  Leitura      09:00─10:00   58m  ◼◼◼    ││
│          │ │        │                                  │ │  ✓  Meditacao    10:00─10:30   20m  ◼      ││
│ ─────────│ │  08:00 ┬ ░░░░░░░░░░░░░░░░                 │ │  ✓  Almoco       12:00─13:00   45m  ◼◼     ││
│ q quit   │ │        │ Ingles           ✓ done    30m   │ │  ▶  Deep Work    14:00─15:30   25m+ ◼◼◼    ││
│ ? help   │ │  08:30 ┤ ░░░░░░░░░░░░░░░░                 │ │  ·  Dev          16:00─17:00   60m  ───    ││
│          │ │        │                                  │ │  ·  Corrida      18:00─18:40   40m  ───    ││
│          │ │  09:00 ┬ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │ │  ·  Journaling   21:00─21:15   15m  ───    ││
│          │ │        │ Leitura          ✓ done    58m   │ │  ·  Revisao      21:30─22:00   30m  ───    ││
│          │ │  10:00 ┬ ░░░░░░░░░░░░░░░░░                │ │                                            ││
│          │ │        │ Meditacao        ✓ done    20m   │ │  [enter] done  [s] skip  [g] go to screen  ││
│          │ │  10:30 ┤                                  │ └────────────────────────────────────────────┘│
│          │ │  11:00 │                                  │                                               │
│          │ │        │         ┈ livre ┈                │ ┌─ Tarefas ────── 3 pendentes ───────────────┐│
│          │ │  12:00 ┬ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │ │                                            ││
│          │ │        │ Almoco           ✓ done    45m   │ │  !! Relatorio Q1    alta    hoje   venc.   ││
│          │ │  13:00 ┤ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │ │  !  Code review    media   hoje            ││
│          │ │        │                                  │ │  ·  Email cliente   media   Sex 21         ││
│          │ │  14:00 ┬ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    │ │  ·  Docs sprint     baixa   Seg 24         ││
│          │ │        │ Deep Work    ▶ running   25m+    │ │                                            ││
│          │ │ 14:32▸ ┤ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    │ │  [enter] detalhes  [c] concluir  [g] go    ││
│          │ │  15:00 │ · · · · · · · · · · · · · · · ·  │ └────────────────────────────────────────────┘│
│          │ │  15:30 ┤                                  │                                               │
│          │ │  16:00 ┬ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄    │ ┌─ Timer ────────────────────────────────────┐│
│          │ │        │ Dev              · pend    60m   │ │                                            ││
│          │ │  17:00 ┤ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄    │ │          ◉  25:43   ▶ RUNNING              ││
│          │ │        │                                  │ │          Deep Work                         ││
│          │ │  18:00 ┬ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄          │ │                                            ││
│          │ │        │ Corrida          · pend    40m   │ │  Sessoes: 3  │  Total: 2h 15m  │  Avg: 45m ││
│          │ │  18:40 ┤                                  │ │  [s]tart  [p]ause  [enter]stop  [c]ancel   ││
│          │ │  19:00 │                                  │ └────────────────────────────────────────────┘│
│          │ │        │         ┈ livre ┈                │                                               │
│          │ │  20:00 │                                  │ ┌─ Metricas ─────────────────────────────────┐│
│          │ │  21:00 ┬ ┄┄┄┄┄┄┄┄┄┄                       │ │                                            ││
│          │ │        │ Journaling       · pend    15m   │ │  Streak ·········  12 dias  (best: 28)     ││
│          │ │  21:15 ┤                                  │ │  Completude 7d ··  ▪▪▪▪▪▪▪░░░  72%         ││
│          │ │  21:30 ┬ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄                │ │  Completude 30d ·  ▪▪▪▪▪▪░░░░  63%         ││
│          │ │        │ Revisao          · pend    30m   │ │                                            ││
│          │ │  22:00 ┤ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄                │ │  Seg ▪▪▪▪▪▪▪▪░░ 8/10  ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ · ·  ││
│          │ │        │                                  │ │  Ter ▪▪▪▪▪▪▪▪▪░ 9/10  ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ✓ ·  ││
│          │ │                                           │ │  Qua ▪▪▪▪▪▪▪░░░ 7/10  ✓ ✓ ✓ ✓ ✓ ✓ ✓ · · ·  ││
│          │ │                                           │ │  Qui ▪▪▪▪▪▪░░░░ 6/10  ✓ ✓ ✓ ✓ ✓ ✓ · · · ·  ││
│          │ │                                           │ │                                    ← hoje  ││
│          │ └───────────────────────────────────────────┘ │                                            ││
│          │                                               │  [f] 7d/14d/30d                            ││
│          │                                               └────────────────────────────────────────────┘│
├──────────┴─────────────────────────────────────────────────────────────────────────────────────────────┤
│  Rotina Matinal               │  ▶ Deep Work 25:43              │  Qui 20 Fev 2026  14:32              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Legenda Visual da Timeline (Agenda do Dia)

```
  Blocos concluidos (done):         ░░░░░░░░░░░░░░  cor $success (verde)
  Bloco ativo (running):            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  cor $primary-light (purple)
  Blocos pendentes (pending):       ┄┄┄┄┄┄┄┄┄┄┄┄┄┄  cor $muted (tracejado)
  Blocos skipados:                  ╌╌╌╌╌╌╌╌╌╌╌╌╌╌  cor $warning (amarelo, tracejado)
  Horarios livres:                  ┈ livre ┈        texto dim centralizado
  Marcador "agora":                 14:32▸           seta na regua de horas
  Bloco projetado (continuacao):    · · · · · · · ·  pontilhado apos hora atual
  Conflito (overlap):               ████ ████        dois blocos lado a lado, cor $error
```

## Legenda Visual dos Cards

```
  Habitos - Indicadores:
    ✓  done       ($success)       ◼◼◼  esforco relativo (mini sparkline)
    ▶  running    ($primary-light)
    ✗  skipped    ($warning)
    !  missed     ($error)
    ·  pending    ($muted)          ───  ainda sem dados

  Tarefas - Prioridade:
    !! overdue + alta  ($error, bold)
    !  alta            ($error)
    ▪  media           ($warning)
    ·  baixa           ($muted)

  Metricas - Historico:
    ▪▪▪▪▪▪▪▪░░  barra de progresso (preenchido/vazio)
    ✓ ✓ ✓ · ·   dot matrix por habito (done/pending)
```

## Detalhe: Conflito na Timeline

```
  09:00 ┬ ░░░░░░░░░░░░░░│░░░░░░░░░░░░░░░
        │ Leitura    ✓  │ Reuniao    ✓
  10:00 ┤ ░░░░░░░░░░░░░░│
        │               │ Reuniao (cont.)
  10:30 ┤               └░░░░░░░░░░░░░░░
```

## Detalhe: Timer em estado IDLE

```
  ┌─ Timer ─────────────────────────────────────┐
  │                                             │
  │          ◎  00:00   ⏹ IDLE                  │
  │          Nenhum timer ativo                 │
  │                                             │
  │  Ultimo: Leitura  58m  (09:02-10:00)        │
  │                                             │
  │  Sessoes: 3  │  Total: 2h 15m  │  Avg: 45m  │
  │  [s]tart novo timer                         │
  └─────────────────────────────────────────────┘
```

## Detalhe: Dashboard sem rotina ativa

```
  ┌─ DASHBOARD ──────────────────────────────────────────── Qui 20 Fev 2026 ──────┐
  │ [Sem rotina]   Crie uma rotina: timeblock routine add   ou   [2] Rotinas      │
  └───────────────────────────────────────────────────────────────────────────────┘
```

## Detalhe: Metricas com filtro 30d

```
  ┌─ Metricas ──── 30 dias ─────────────────────────────────┐
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
  │                                              ← hoje     │
  │  [f] 7d/14d/30d  [h] heatmap                            │
  └─────────────────────────────────────────────────────────┘
```
