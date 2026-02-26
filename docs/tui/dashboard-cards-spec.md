# Dashboard Cards -- Especificação de Design v5

> **Data:** 24 Fev 2026
>
> **Branch:** feat/tui-phase1
>
> **Contexto:** Especificação detalhada de cada card do dashboard com regras
> de cor, limites de coluna e BRs pendentes. Este documento serve como
> insumo para formalização das BRs no business-rules.md.

**Referências:**

- `docs/tui/color-system.md` (paleta Catppuccin Mocha)
- `docs/tui/dashboard-mockup-v4.md` (mockup anterior)
- `docs/architecture/adr-021-status-substatus-refactor.md`

---

## Terminologia

- **Card**: container com borda `round`, título, conteúdo e footer opcional.
  Termo único para toda a TUI. O termo "painel" não é usado.
- **Viewport**: área visível do card sem scroll.
- **Overflow**: itens que excedem o viewport. Indicador `+N ▼` no rodapé.
- **Zona**: região focável do dashboard. Tab navega entre zonas.

---

## Paleta de referência (Catppuccin Mocha)

```plaintext
Texto principal .... #CDD6F4 (Text)
Texto secundário ... #BAC2DE (Subtext1)
Texto dim .......... #A6ADC8 (Subtext0)
Texto muted ........ #6C7086 (Overlay0)
Borda card ......... #45475A (Surface1)
Fundo card ......... #1E1E2E (Base)
Fundo elevado ...... #313244 (Surface0)
```

**Status → Cor (foreground):**

```plaintext
done/full .......... #A6E3A1 (Green)       ✓
done/partial ....... #F5E0DC (Rosewater)   ✓~
done/overdone ...... #F2CDCD (Flamingo)    ✓+
done/excessive ..... #FAB387 (Peach)       ✓!
not_done/justified . #F9E2AF (Yellow)      !
not_done/unjustified #F38BA8 (Red)         ✗!
not_done/ignored ... #EBA0AC (Maroon)      ✗?
running ............ #CBA6F7 (Mauve)       ▶
paused ............. #F9E2AF (Yellow)      ⏸
pending ............ #6C7086 (Overlay0)    ·
cancelled .......... #6C7086 (Overlay0)    ✗
```

---

## 1. Card Agenda do Dia

### Mockup anotado

```
                    ANOTAÇÕES
                    ┊
 ┌─ Agenda do Dia ──────────── Terça, 24 de Fevereiro ─┐
 │                                                     │
 │  ── Rotina Matinal ─────────────── Manhã ── 3/4 ──  │.............. separador de período
 │                                                     │               cor: Subtext0 #A6ADC8
 │  06:00 ─┬─ Despertar · 1h    ✓ done                 │.............. header do bloco
 │  ┊      ┊▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░            │.............. fill bar (30min = 1 linha)
 │  ┊      ┊▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░            │
 │  ┊      ┊┊                                          │
 │  07:00 ─┼─ Academia · 45m    ✓~ partial             │.............. transição ─┼─
 │         │▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░            │
 │         │                                           │
 │  08:00  │           ┈ livre ┈                       │.............. gap >= 30min
 │  ┊      ┊                                           │               cor: Overlay0
 │  09:00 ─┼─ Trabalho · 3h     ▶ running 47m          │.............. bold (running)
 │  ┊       ┊▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓           │.............. fill denso ▓
 │  ┊       ┊▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓           │               borda ▌ = Mauve
 │  ┊       ┊▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓           │               fill = Mauve escuro
 │  ┊       ┊▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓           │
 │  ┊       ┊▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓           │
 │  ┊       ┊▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓           │
 │  ┊       ┊                                          │
 │  ── Tarde ─── Rotina Vespertina ─── 0/3 ───────── │
 │  ┊       ┊                                           │
 │  12:00 ─┬─ Almoço · 1h15     ✓+ overdone             │
 │         │▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░             │
 │  ┊      ┊                                            │
 │  c0  c1 c2  c3        c4     c5 c6                   │
 │                                                      │
 └──────────────────────────────────────────────────────┘
```

### Colunas do header de bloco

```
  c0     c1   c2               c3     c4  c5
  ┊      ┊    ┊                ┊      ┊   ┊
  06:00 ─┬─ Despertar ········ 1h     ✓  done
  ┊      ┊    ┊                ┊      ┊   ┊
  5ch   3ch   14ch max        5ch   2ch  resto
```

| Col | Campo    | Larg | Cor                  | Regra                                 |
| --- | -------- | ---- | -------------------- | ------------------------------------- |
| c0  | Horário  | 5ch  | Mauve se hora atual, | `HH:MM`. Bold se running neste slot.  |
|     |          |      | Subtext0 se passado, | Só aparece em slots de 30min.         |
|     |          |      | Text se futuro       |                                       |
| c1  | Conector | 3ch  | Surface1 #45475A     | `─┬─` início, `─┤` meio,              |
|     |          |      |                      | `─┼─` transição, `│` vazio            |
| c2  | Nome     | 14ch | Herda cor do status  | Trunca `...` se > 14ch.               |
|     |          |      |                      | Bold se running/paused.               |
| c3  | Duração  | 5ch  | Herda cor do status  | `XhYY` (>= 60min) ou `XXm` (< 60min). |
|     |          |      |                      | Bold se running. `──:──` se sem dado. |
| c4  | Ícone    | 2ch  | Herda cor do status  | Ícone composto: `✓` `✓~` `✓+` `✓!`    |
|     |          |      |                      | `▶` `⏸` `✗!` `✗?` `·`                 |
| c5  | Label    | rest | Herda cor do status  | `done` `partial` `running 47m` etc.   |
|     |          |      |                      | Para running: append elapsed time.    |

### Cores do horário (c0) por contexto temporal

```
  Passado:  #A6ADC8 (Subtext0) -- horas já transcorridas
  Atual:    #CBA6F7 (Mauve)    -- hora corrente, bold
  Futuro:   #CDD6F4 (Text)     -- horas ainda por vir
```

### Fill bar (linha abaixo do header)

```
  │▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  ┊┊╰── fill chars (fw - 1), cor varia ──╯
  ┊╰── borda ▌ (1ch), cor do status (foreground)
  ╰── conector │ (1ch), Surface1
```

| Status      | Char fill | Cor borda ▌      | Cor fill              |
| ----------- | --------- | ---------------- | --------------------- |
| done/\*     | ░         | cor do substatus | mesma (foreground)    |
| running     | ▓         | Mauve #CBA6F7    | Mauve escuro #8B6EAC  |
| paused      | ▒         | Yellow #F9E2AF   | Yellow escuro #B8A050 |
| not_done/\* | ┄         | cor do substatus | mesma (foreground)    |
| pending     | ░         | Overlay0 #6C7086 | mesma (foreground)    |

### Separador de período

```
  ── Manhã ─── Rotina Matinal ──── 3/4 ──────────────
  ┊            ┊                   ┊
  período      rotina associada    progresso X/Y
```

| Campo   | Cor               | Regra                                     |
| ------- | ----------------- | ----------------------------------------- |
| Período | Subtext0 #A6ADC8  | "Manhã" "Tarde" "Noite"                   |
| Rotina  | Text #CDD6F4      | Nome da rotina. "[Sem rotina]" se nenhuma |
| X/Y     | Green se >= 80%,  | X = done+running, Y = total do período    |
|         | Yellow se >= 50%, |                                           |
|         | Red se < 50%      |                                           |

### Períodos padrão

| Período | Range       | Visibilidade                      |
| ------- | ----------- | --------------------------------- |
| Manhã   | 06:00-12:00 | Oculto se sem eventos neste range |
| Tarde   | 12:00-18:00 | Oculto se sem eventos neste range |
| Noite   | 18:00-23:00 | Oculto se sem eventos neste range |

### Régua e scroll

- **Range**: `min(06, first_event_hour - 1)` até `max(22, last_event_hour + 1)`
- **Auto-scroll**: hora atual posicionada no terço superior ao abrir
- **Marcador**: `▸` no slot da hora atual (col c1, substitui conector)
- **Gaps**: `┈ livre ┈` centralizado em Overlay0, só se gap >= 30min
- **Proporcionalidade**: 30min = 1 linha de fill

---

## 2. Card Hábitos

### Mockup anotado

```
 ┌─ Hábitos ────────────────────────────── ●●●●○○○○○ 4/9 44% ─┐
 │                                                            │
 │  c0   c1                c2              c3       c4        │
 │  ┊    ┊                 ┊               ┊        ┊         │
 │  ✓    Despertar         06:00 ─ 07:00   01h00m   ●●●●●     │... Green #A6E3A1
 │  ✓~   Academia          07:00 ─ 08:00   00h45m   ●●●●·     │... Rosewater #F5E0DC
 │  ▶    Trabalho          09:00 ─ 12:00   00h47m   ●●●●●     │... Mauve #CBA6F7, bold
 │  ✓+   Almoço            12:00 ─ 13:00   01h15m   ●●●●●●    │... Flamingo #F2CDCD
 │  ⏸    Estudo            14:00 ─ 16:00   00h12m   ●●···     │... Yellow #F9E2AF, bold
 │  ✓!   Café da Tarde     16:00 ─ 17:00   00h50m   ●●●●●●●   │... Peach #FAB387
 │  ✗!   Organização       17:00 ─ 18:00   01h00m   ─────     │... Red #F38BA8
 │  ✗?   Jantar            19:00 ─ 20:00   01h00m   ─────     │... Maroon #EBA0AC
 │  ·    Leitura           21:00 ─ 22:00   01h00m   ·····     │... Overlay0 #6C7086
 │                                                            │
 └────────────────────────────────────────────────────────────┘
```

### Colunas

| Col | Campo        | Larg | Cor                        | Regra                                 |
| --- | ------------ | ---- | -------------------------- | ------------------------------------- |
| c0  | Ícone+sub    | 3ch  | Cor do status/substatus    | Ícone composto conforme tabela        |
|     |              |      |                            | de status. Espaço se só 1 char.       |
| c1  | Nome         | 16ch | Cor do status              | Trunca `...` se > 16ch.               |
|     |              |      |                            | Bold se running/paused.               |
|     |              |      |                            | Strikethrough se not_done.            |
| c2  | Horário      | 13ch | Cor do status se done/run. | `HH:MM ─ HH:MM`.                      |
|     |              |      | Overlay0 se pending.       | Segundo horário = end_time planejado. |
|     |              |      | Yellow se paused.          | `──:── ─ ──:──` se sem horário.       |
| c3  | Duração real | 6ch  | Cor do status.             | `XXhYYm` formato fixo.                |
|     |              |      | Bold se running.           | Mostra actual_minutes, não planned.   |
|     |              |      |                            | `──h──m` se sem dado.                 |
| c4  | Effort bar   | 5ch  | Cor do status.             | ● = actual/planned proporcional.      |
|     |              |      |                            | · = resto não preenchido.             |
|     |              |      |                            | ───── se not_done (traço contínuo).   |

### Effort bar (c4) -- regras de renderização

```
  actual/planned = 100%   →  ●●●●●     (5 dots cheios)
  actual/planned = 80%    →  ●●●●·     (4 cheios, 1 vazio)
  actual/planned = 60%    →  ●●●··     (3 cheios, 2 vazios)
  actual/planned = 120%   →  ●●●●●●    (6 dots = overflow, max 7)
  not_done (qualquer)     →  ─────     (traço contínuo, cor status)
  pending (sem dados)     →  ·····     (5 vazios, Overlay0)
```

Fórmula: `filled = round((actual / planned) * 5)`, clamped a [0, 7].

### Título (border_title)

```
  Hábitos ──────────────────────────── ●●●●○○○○○ 4/9 44%
  ╰── fixo    ╰── traços (espaço)     ╰── dot matrix + contadores

  ● = done ou running    (cor Green se >= 80%, Yellow 50-79%, Red < 50%)
  ○ = pending/not_done   (cor Overlay0)
  4/9 = done+running / total
  44% = percentual
```

### Cores do dot matrix do título

| Completude | Cor dos ●      | Cor do percentual |
| ---------- | -------------- | ----------------- |
| >= 80%     | Green #A6E3A1  | Green #A6E3A1     |
| 50-79%     | Yellow #F9E2AF | Yellow #F9E2AF    |
| < 50%      | Red #F38BA8    | Red #F38BA8       |

### Ordenação

Cronológica por `start_time` do hábito. Running sempre visível
(scroll automático se necessário).

---

## 3. Card Tarefas

### Mockup anotado

```
 ┌─ Tarefas ─────────────── 5 pend. 1 done 1 canc. 2 over. ─┐
 │                                                          │
 │  c0  c1                   c2          c3      c4         │
 │  ┊   ┊                    ┊           ┊       ┊          │
 │  !   Dentista             Hoje        23 Feb  15:00      │.. Yellow #F9E2AF
 │  !   Email cliente        Amanhã      24 Feb  09:00      │.. Peach #FAB387
 │  ·   Deploy staging       3 dias      26 Feb  10:00      │.. Text #CDD6F4
 │  ·   Code review          5 dias      28 Feb  14:00      │.. Rosewater #F5E0DC
 │  ·   Retrospectiva        2 mês       25 Apr  ──:──      │.. Overlay0 #6C7086
 │  ✓   Comprar domínio───   Hoje        23 Feb  09:30      │.. Green #A6E3A1 + strike
 │  ✗   Evento cancelado──   ───         20 Feb  16:00      │.. Overlay0 + strike
 │  ✗   Enviar relatório     1 sem       16 Feb  ──:──      │.. Red #F38BA8 (overdue)
 │  ✗   Revisar PR #142      3 dias      20 Feb  14:00    │.. Red #F38BA8 (overdue)
 │      +2 ▼                                                │.. overflow indicator
 └──────────────────────────────────────────────────────────┘
```

### Colunas

| Col | Campo       | Larg | Cor                         | Regra                               |
| --- | ----------- | ---- | --------------------------- | ----------------------------------- |
| c0  | Indicador   | 2ch  | Cor da faixa de proximidade | `!` hoje/amanhã (urgente)           |
|     |             |      |                             | `·` pendente normal                 |
|     |             |      |                             | `✓` done (Green)                    |
|     |             |      |                             | `✗` overdue/canc (Red/Overlay0)     |
| c1  | Nome        | 18ch | Cor da faixa de proximidade | Trunca `...` > 18ch.                |
|     |             |      |                             | Strikethrough se done ou cancelled. |
| c2  | Proximidade | 10ch | Cor da faixa (ver tabela)   | Texto relativo: Hoje, Amanhã,       |
|     |             |      |                             | X dias, X sem, X mês.               |
|     |             |      |                             | `──` se cancelled.                  |
| c3  | Data        | 6ch  | Subtext1 #BAC2DE            | `DD Mmm` fixo. Dim se > 14 dias.    |
|     |             |      | ou Overlay0 se > 14d        |                                     |
| c4  | Horário     | 5ch  | Subtext1 #BAC2DE            | `HH:MM` ou `──:──` se sem horário.  |
|     |             |      |                             | Bold se hoje.                       |

### Faixas de proximidade -- sistema de cores

```
  Linha do tempo:
  ─────┬────┬────┬──────────┬──────────┬──────────┬───────
  over │hoje│ama │  2-7d    │  8-14d   │ 15-29d   │ 30d+
  due  │    │nhã │          │          │          │
  ─────┴────┴────┴──────────┴──────────┴──────────┴───────
  Red    Yel  Pch  Rosewater  Subtext1   Subtext0   Muted
  F38BA8 F9E2 FAB3 F5E0DC     BAC2DE     A6ADC8    6C7086
```

| Faixa      | Dias  | Cor     | Nome Catppuccin |
| ---------- | ----- | ------- | --------------- |
| Overdue    | < 0   | #F38BA8 | Red             |
| Hoje       | 0     | #F9E2AF | Yellow          |
| Amanhã     | 1     | #FAB387 | Peach           |
| 2-3 dias   | 2-3   | #F2CDCD | Flamingo        |
| 4-7 dias   | 4-7   | #F5E0DC | Rosewater       |
| 8-14 dias  | 8-14  | #BAC2DE | Subtext1        |
| 15-29 dias | 15-29 | #A6ADC8 | Subtext0        |
| 30+ dias   | 30+   | #6C7086 | Overlay0        |

A cor aplica-se a c0, c1 e c2 (indicador, nome, proximidade).
c3 e c4 (data, horário) usam Subtext1 fixo (informação auxiliar).

### Indicador c0 -- regras compostas

| Condição                   | Char | Cor           |
| -------------------------- | ---- | ------------- |
| Pendente + hoje            | `!`  | Yellow        |
| Pendente + amanhã          | `!`  | Peach         |
| Pendente + 2-7d            | `·`  | Flamingo/Rose |
| Pendente + 8d+             | `·`  | Subtext1/0    |
| Done                       | `✓`  | Green         |
| Cancelled                  | `✗`  | Overlay0      |
| Overdue (vencida+pendente) | `✗`  | Red           |

### Título (border_title)

```
  Tarefas ──────────── 5 pend. 1 done 1 canc. 2 over.
  ╰── fixo              ╰── contadores por status

  Cores dos contadores:
    pend. → Text #CDD6F4
    done  → Green #A6E3A1
    canc. → Overlay0 #6C7086
    over. → Red #F38BA8
```

### Ordenação

1. Pendentes primeiro, ordenados por proximidade ascendente (mais urgente no topo)
2. Done no final (agrupado)
3. Cancelled no final (agrupado)
4. Overdue no topo absoluto (mais urgente)

### Overflow

```
  Quando itens > viewport_height - 2 (título + padding):
                                              +N ▼
  Cor: Overlay0. Alinhado à direita.
  Indica N itens não visíveis abaixo.
  Scroll com j/k quando card focado.
```

---

## 4. Card Timer (compacto)

### Mockup -- estado Running

```
 ┌─ Timer ─────────────────────────────────── ▶ ativo ─┐
 │                                                     │
 │  ▶  Deep Work · Sessão 2/4              47:23       │
 │     Hoje: 3 sessões · 2h15m total                   │
 │                                                     │
 └─────────────────────────────────────────────────────┘
      c0  c1          c2                    c3
```

### Mockup -- estado Paused

```
 ┌─ Timer ────────────────────────────────── ⏸ paused ─┐
 │                                                     │
 │  ⏸  Estudo · Sessão 1/2                 12:45       │
 │     Hoje: 3 sessões · 2h15m total                   │
 │                                                     │
 └─────────────────────────────────────────────────────┘
```

### Mockup -- estado Idle

```
 ┌─ Timer ───────────────────────────────────── ⏹ idle ─┐
 │                                                      │
 │  Última: Deep Work · 45m · 14:32                     │
 │  Hoje: 3 sessões · 2h15m total · média 45m           │
 │                                                      │
 └──────────────────────────────────────────────────────┘
```

### Campos por estado

**Running / Paused (linha 1):**

| Col | Campo       | Cor                          | Regra                               |
| --- | ----------- | ---------------------------- | ----------------------------------- |
| c0  | Ícone       | Mauve (run) / Yellow (pause) | `▶` ou `⏸`                          |
| c1  | Nome evento | Herda cor do ícone. Bold.    | Nome do hábito/tarefa associado     |
| c2  | Sessão      | Subtext1 #BAC2DE             | `Sessão X/Y` (X=atual, Y=total dia) |
| c3  | Elapsed     | Mauve (run) / Yellow (pause) | `MM:SS`. Bold. Atualiza 1s.         |
|     |             |                              | Pisca se paused (toggle 1s).        |

**Running / Paused (linha 2):**

| Campo         | Cor              | Regra                           |
| ------------- | ---------------- | ------------------------------- |
| Resumo do dia | Subtext0 #A6ADC8 | `Hoje: N sessões · XhYYm total` |

**Idle (linha 1):**

| Campo         | Cor              | Regra                            |
| ------------- | ---------------- | -------------------------------- |
| Última sessão | Subtext1 #BAC2DE | `Última: Nome · Duração · HH:MM` |

**Idle (linha 2):**

| Campo         | Cor              | Regra                                   |
| ------------- | ---------------- | --------------------------------------- |
| Resumo do dia | Subtext0 #A6ADC8 | `Hoje: N sessões · XhYYm total · média` |

### Título (border_title)

| Seção    | Conteúdo                                                      |
| -------- | ------------------------------------------------------------- |
| Esquerda | `Timer`                                                       |
| Direita  | `▶ ativo` (Mauve) / `⏸ paused` (Yellow) / `⏹ idle` (Overlay0) |

### Notas

- Sem ASCII art no dashboard. ASCII art fica na TimerScreen dedicada.
- Card ocupa apenas 4 linhas (borda + 2 conteúdo + borda).
- Timer elapsed no card é redundante com o header, mas o card
  adiciona contexto (sessão X/Y, resumo do dia) que o header não tem.
- Keybindings do timer vivem no footer contextual quando card focado.

---

## 5. Footer (Status Bar contextual)

### Mockup anotado

```
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ Rotina Matinal     │  [enter]done [s]skip [g]screen  │ ▶ 47:23    14:32    │
 │ ┊                   ┊                                 ┊ ┊          ┊       │
 │ rotina ativa        keybindings contextuais           timer      hora      │
 │ (persistente)       (muda por zona focada)            (persistente)        │
 └────────────────────────────────────────────────────────────────────────────┘
   c_left (1fr)         c_center (1fr)                    c_right (auto)
```

### Seções

| Seção  | Largura | Cor              | Conteúdo                         | Atualização |
| ------ | ------- | ---------------- | -------------------------------- | ----------- |
| Left   | 1fr     | Text #CDD6F4     | Rotina ativa (ou "[Sem rotina]") | on_focus    |
| Center | 1fr     | Subtext0 #A6ADC8 | Keybindings da zona focada       | on_focus    |
| Right  | auto    | Timer: Mauve     | Timer elapsed + hora HH:MM       | Timer: 1s   |
|        |         | Hora: Overlay0   |                                  | Hora: 1min  |

### Keybindings por zona

| Zona focada | Footer center                          |
| ----------- | -------------------------------------- |
| Agenda      | `[enter]done [s]skip [g]habit`         |
| Hábitos     | `[enter]done [s]skip [g]screen`        |
| Tarefas     | `[enter]detail [c]complete [g]screen`  |
| Timer       | `[s]tart [p]ause [enter]stop [c]ancel` |
| (nenhum)    | `[Tab]navegar [?]ajuda [q]sair`        |

### Formato dos keybindings

```
  [tecla]ação
  ╰─╯╰──╯
  Overlay0  Subtext0

  Exemplo: [enter]done  [s]skip  [g]screen
           ^^^^^^       ^^^      ^^^         → Overlay0 #6C7086
                 ^^^^      ^^^^     ^^^^^^   → Subtext0 #A6ADC8
```

A tecla entre colchetes fica em Overlay0 (dim), a ação fica em Subtext0.
Isso cria hierarquia visual onde a ação é mais legível que a tecla.

### Diferença do header

O **header** mostra informação resumida do dia (o quê):

- Rotina, progresso X/Y%, tasks pendentes, timer elapsed, data

O **footer** mostra ações disponíveis (o que fazer):

- Rotina (contexto), keybindings da zona ativa, hora

Não há sobreposição funcional. A única duplicação é "rotina" que
aparece em ambos, mas serve propósitos diferentes: no header é
contexto informacional, no footer é label de localização.

O timer elapsed aparece em ambos propositalmente: no header como
indicador passivo, no footer como valor atualizado a cada segundo
com mais destaque visual (Mauve bold).

---

## 6. Segmentação de rotinas -- Períodos

### Conceito

O dashboard quebra automaticamente o dia em 3 períodos baseados em
faixas horárias fixas. Cada período pode ter uma rotina associada
(ou a mesma rotina cobre o dia inteiro).

### Períodos padrão (v1.7)

```
  06:00 ──────────── 12:00 ──────────── 18:00 ──────────── 23:59
  │     Manhã        │     Tarde        │     Noite        │
  │  Rotina Matinal  │ Rot. Vespertina  │  Rotina Noturna  │
```

### Regras de exibição

| Regra               | Comportamento                                   |
| ------------------- | ----------------------------------------------- |
| Período sem eventos | Oculto (não renderiza separador nem espaço)     |
| Período com eventos | Exibe separador + eventos do range              |
| Período passado     | Colapsável: mostra só `── Manhã ── 3/4 done ──` |
| Período ativo       | Expandido: mostra todos os blocos               |
| Período futuro      | Expandido: mostra blocos pendentes              |

### Evolução futura (Settings screen)

- Períodos customizáveis (quantos, quais ranges)
- Esquemas nomeados (Semana, FDS, Férias)
- Auto-switch de esquema por dia da semana
- Rotinas diferentes por período

Na v1.7 os períodos são fixos (3, com ranges hardcoded).
Customização fica para v1.8+ com a SettingsScreen.

---

## 7. Resumo de BRs a formalizar

| ID             | Descrição resumida                                 |
| -------------- | -------------------------------------------------- |
| BR-TUI-003-R12 | Cards sem limite fixo. Viewport determina visíveis |
| BR-TUI-003-R13 | Régua: range adaptativo baseado em eventos         |
| BR-TUI-003-R14 | Subtítulo hábitos: X/Y Z% com dot matrix           |
| BR-TUI-003-R15 | Auto-scroll: hora atual no terço superior          |
| BR-TUI-003-R16 | Marcador ▸ no slot atual                           |
| BR-TUI-003-R17 | Gap >= 30min exibe `┈ livre ┈`                     |
| BR-TUI-003-R18 | Effort bar: 5 dots proporcional actual/planned     |
| BR-TUI-003-R19 | Ordenação hábitos: cronológica por start_time      |
| BR-TUI-003-R20 | Ordenação tarefas: urgência, done/canc no final    |
| BR-TUI-003-R21 | Overflow: `+N ▼` quando excede viewport            |
| BR-TUI-003-R22 | Strikethrough em done e cancelled (tarefas)        |
| BR-TUI-003-R23 | Subtítulo tarefas: contadores por status           |
| BR-TUI-003-R24 | Períodos: Manhã/Tarde/Noite com separador visual   |
| BR-TUI-007-R02 | Footer contextual: keybindings por zona focada     |
| BR-TUI-003-R25 | Timer card compacto: 2 linhas, sem ASCII art       |
| BR-TUI-003-R26 | Horários passados em Subtext0, atual em Mauve      |
| BR-TUI-003-R27 | Nome herda cor do status em todos os cards         |
| BR-TUI-003-R28 | Mock data como fixture de teste, não fallback      |

---

**Última atualização:** 24 Fev 2026
