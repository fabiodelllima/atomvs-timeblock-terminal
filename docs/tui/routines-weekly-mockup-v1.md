# Routines Screen Mockup — Terminal 120x42

## Visão Geral

A tela de Rotinas exibe a semana completa em formato de grade temporal (estilo Google Calendar weekly view). É a representação visual do "plano ideal" — o template semanal que o usuário desenhou para si. Enquanto o Dashboard mostra o dia _real_ com status de execução, a tela de Rotinas mostra a _intenção_: como a semana deveria ser se tudo corresse conforme planejado.

A grade ocupa toda a largura disponível após a sidebar, com as 7 colunas dos dias da semana distribuídas horizontalmente e a régua de horas avançando verticalmente. Cada hábito aparece como um bloco posicionado no dia e horário correspondentes à sua recorrência, com cor diferenciada e nome legível dentro do bloco.

---

## Layout Principal (terminal 120x42)

```
┌──────────┬──────────────────────────────────────────────────────────────────────────────────────────┐
│          │ ┌─ ROTINAS ─────────────────────────────────────────────────────── Sem 17─23 Fev 2026 ─┐ │
│  ◉ ATOMVS│ │ ▸ Rotina Matinal (ativa)     10 hábitos │  Rotina Noturna  4 háb │  + Nova rotina    │ │
│  ════════│ └──────────────────────────────────────────────────────────────────────────────────────┘ │
│          │                                                                                          │
│   Dash   │ ┌─ Grade Semanal ─ Rotina Matinal ───────────────────────────────────────────────────┐   |
│ ▸ Rotin  │ │       │  Seg 17  │  Ter 18  │  Qua 19  │  Qui 20  │  Sex 21  │  Sáb 22  │  Dom 23  │   │
│   Habit  │ │ ──────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤   │
│   Tasks  │ │       │          │          │          │          │          │          │          │   │
│   Timer  │ │ 06:00 │ ████████ │ ████████ │ ████████ │ ████████ │ ████████ │          │          │   │
│          │ │       │ Gym      │ Gym      │ Gym      │ Gym      │ Gym      │          │          │   │
│ ─────────│ │ 07:00 │ ████████ │ ████████ │ ████████ │ ████████ │ ████████ │          │          │   │
│ q quit   │ │       │          │          │          │          │          │          │          │   │
│ ? help   │ │ 08:00 │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │          │          │   │
│          │ │       │ Inglês   │ Inglês   │ Inglês   │ Inglês   │ Inglês   │          │          │   │
│          │ │ 08:30 │          │          │          │          │          │          │          │   │
│          │ │       │          │          │          │          │          │          │          │   │
│          │ │ 09:00 │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │   │
│          │ │       │ Leitura  │ Leitura  │ Leitura  │ Leitura  │ Leitura  │ Leitura  │ Leitura  │   │
│          │ │ 10:00 │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │   │
│          │ │       │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │   │
│          │ │ 10:30 │ Meditaç. │ Meditaç. │ Meditaç. │ Meditaç. │ Meditaç. │ Meditaç. │ Meditaç. │   │
│          │ │       │          │          │          │          │          │          │          │   │
│          │ │ 11:00 │          │          │          │          │          │          │          │   │
│          │ │       │          │          │          │          │          │          │          │   │
│          │ │ 12:00 │ ▓▓▓▓▓▓▓▓ │ ▓▓▓▓▓▓▓▓ │ ▓▓▓▓▓▓▓▓ │ ▓▓▓▓▓▓▓▓ │ ▓▓▓▓▓▓▓▓ │ ▓▓▓▓▓▓▓▓ │ ▓▓▓▓▓▓▓▓ │   │
│          │ │       │ Almoço   │ Almoço   │ Almoço   │ Almoço   │ Almoço   │ Almoço   │ Almoço   │   │
│          │ │ 13:00 │          │          │          │          │          │          │          │   │
│          │ │       │          │          │          │          │          │          │          │   │
│          │ │ 14:00 │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │          │          │   │
│          │ │       │ Deep W.  │ Deep W.  │ Deep W.  │ Deep W.  │ Deep W.  │          │          │   │
│          │ │ 15:00 │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │          │          │   │
│          │ │       │          │          │          │          │          │          │          │   │
│          │ │ 16:00 │ ████████ │ ████████ │ ████████ │ ████████ │ ████████ │          │          │   │
│          │ │       │ Dev      │ Dev      │ Dev      │ Dev      │ Dev      │          │          │   │
│          │ │ 17:00 │          │          │          │          │          │          │          │   │
│          │ │       │          │          │          │          │          │          │          │   │
│          │ │ 18:00 │ ████████ │          │ ████████ │          │ ████████ │ ████████ │          │   │
│          │ │       │ Corrida  │          │ Corrida  │          │ Corrida  │ Corrida  │          │   │
│          │ │ 18:40 │          │          │          │          │          │          │          │   │
│          │ │       │          │          │          │          │          │          │          │   │
│          │ │ 21:00 │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │ ░░░░░░░░ │   │
│          │ │       │ Journal  │ Journal  │ Journal  │ Journal  │ Journal  │ Journal  │ Journal  │   │
│          │ │ 21:15 │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │ ▒▒▒▒▒▒▒▒ │   │
│          │ │       │ Revisão  │ Revisão  │ Revisão  │ Revisão  │ Revisão  │ Revisão  │ Revisão  │   │
│          │ │ 22:00 │          │          │          │          │          │          │          │   │
│          │ └───────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘   │
│          │                                                                                          │
│          │  [n] novo hábito  [e] editar  [x] deletar  [a] ativar rotina  [←/→] semana  [g] go hab   │
├──────────┴──────────────────────────────────────────────────────────────────────────────────────────┤
│  Rotina Matinal               │  ▶ Deep Work 25:43              │  Qui 20 Fev 2026  14:32           │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Legenda Visual dos Blocos

Cada hábito tem uma cor atribuída (campo `color` do model). Na grade, blocos usam preenchimentos diferentes para distinguir hábitos visualmente em terminais monocromáticos, combinados com a cor real quando o terminal suporta:

```
  ████████  Bloco sólido (cor 1)    — Gym, Dev, Corrida
  ▒▒▒▒▒▒▒▒  Bloco médio (cor 2)     — Leitura, Deep Work, Revisão
  ░░░░░░░░  Bloco leve (cor 3)      — Inglês, Meditação, Journaling
  ▓▓▓▓▓▓▓▓  Bloco denso (cor 4)     — Almoço
```

Em terminais com cor, cada bloco usa a cor definida pelo hábito (`--color sage`, `--color lavender`, etc.). O padrão de preenchimento serve como canal redundante para acessibilidade — dois hábitos adjacentes são distinguíveis mesmo em escala de cinza.

---

## Anatomia da Grade

```
       │  Seg 17  │  Ter 18  │  ···
 ──────┼──────────┼──────────┼──────
       │          │          │           ← célula vazia (horário livre)
 06:00 │ ████████ │ ████████ │           ← bloco inicia nesta hora
       │ Gym      │ Gym      │           ← label do hábito (truncado se necessário)
 07:00 │ ████████ │ ████████ │           ← bloco continua (duração > 30min)
       │          │          │           ← bloco termina, célula vazia
 08:00 │ ░░░░░░░░ │ ░░░░░░░░ │           ← novo bloco começa
       │ Inglês   │ Inglês   │
```

Regras de rendering:

- Cada hora = 2 linhas na grade (preenchimento + label ou continuação)
- Bloco com duração ≤ 30min = 1 linha (preenchimento com label na mesma linha)
- Bloco com duração > 30min = múltiplas linhas (label na primeira linha)
- Nome truncado em 8 caracteres por coluna (largura de ~10 chars por dia)
- Colunas de dias com largura igual, distribuídas proporcionalmente
- Régua de horas à esquerda, alinhada com a régua do dashboard

---

## Header Bar da Tela

```
┌─ ROTINAS ─────────────────────────────────────────────────────────── Sem 17─23 Fev 2026 ─┐
│ ▸ Rotina Matinal (ativa)     10 hábitos │  Rotina Noturna  4 háb │  + Nova rotina        │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

Conteúdo:

- Lista horizontal de rotinas, scrollável se muitas (a ativa com `▸` e `(ativa)`)
- Contagem de hábitos por rotina
- `+ Nova rotina` à direita como ação rápida
- Período da semana exibida (extrema direita do título)

---

## Interatividade e Keybindings

### Navegação na grade

```
  ←/→    Navegar entre dias (colunas)
  ↑/↓    Navegar entre hábitos no dia (pula para próximo bloco)
  j/k    Alternativa vim para ↑/↓
  Tab    Próxima rotina no header
```

### Navegação temporal

```
  [/]    Semana anterior / próxima (alterna semana exibida)
  T      Voltar para semana atual (today)
```

### CRUD de rotinas

```
  n      Nova rotina (abre formulário inline no header)
  e      Editar rotina selecionada (nome)
  x      Deletar rotina selecionada (confirmação)
  a      Ativar rotina selecionada (BR-ROUTINE-001)
```

### CRUD de hábitos

```
  n      Novo hábito (abre formulário — título, horário, recorrência, cor)
  e      Editar hábito selecionado na grade
  x      Deletar hábito selecionado (confirmação)
  enter  Ver detalhes do hábito (instâncias, streaks)
  g      Ir para screen Habits (visão completa com instâncias)
```

O contexto determina se `n/e/x` opera sobre rotina ou hábito: se o foco está no header, opera sobre rotinas; se o foco está na grade, opera sobre hábitos.

---

## Detalhe: Hábito Selecionado na Grade

Quando o cursor está sobre um bloco, ele ganha borda $primary e exibe tooltip com informações completas:

```
       │  Seg 17  │  Ter 18  │
 ──────┼──────────┼──────────┼
 06:00 │┌────────┐│ ████████ │
       ││  Gym   ││ Gym      │
 07:00 │└────────┘│ ████████ │
       │ 06:00─07:00  60min  │    ← tooltip abaixo do bloco
       │ WEEKDAYS  #sage     │
```

Ou um painel lateral fixo:

```
  ┌─ Detalhes ──────────────────────┐
  │  Gym                            │
  │  06:00 ─ 07:00  (60 min)        │
  │  Recorrência: WEEKDAYS          │
  │  Cor: sage                      │
  │  Instâncias: 45 pend / 18 done  │
  │  Streak: 12 dias                │
  │                                 │
  │  [e] editar  [x] deletar        │
  │  [g] ver instâncias             │
  └─────────────────────────────────┘
```

---

## Detalhe: Conflito Visível na Grade

Quando dois hábitos compartilham o mesmo horário no mesmo dia, a célula é dividida:

```
       │  Qua 19   │
 ──────┼───────────┼
 09:00 │ ▒▒▒▒│░░░░ │
       │ Leit│Reun │
 10:00 │ ▒▒▒▒│░░░░ │
       │     │Reun │
 10:30 │     └░░░░ │
```

Blocos em conflito usam cor `$error` na borda e o divisor `│` separa os dois hábitos na mesma célula. Isso é coerente com a filosofia do sistema: conflitos são permitidos e exibidos, nunca bloqueados (BR-REORDER-001).

---

## Detalhe: Rotina sem Hábitos

```
┌─ Grade Semanal ─ Rotina Nova ──────────────────────────────────────────────────────┐
│       │  Seg 17  │  Ter 18  │  Qua 19  │  Qui 20  │  Sex 21  │  Sáb 22  │  Dom 23  │
│ ──────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│       │          │          │          │          │          │          │          │
│       │                                                                            │
│       │                   Nenhum hábito nesta rotina.                              │
│       │                   Pressione [n] para criar o primeiro.                     │
│       │                                                                            │
└───────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## Detalhe: Formulário de Novo Hábito (inline)

Quando o usuário pressiona `n` com foco na grade:

```
┌─ Novo Hábito ──────────────────────────────────────────┐
│                                                        │
│  Título:       [                              ]        │
│  Início:       [  :  ]                                 │
│  Fim:          [  :  ]                                 │
│  Recorrência:  ( ) EVERYDAY  ( ) WEEKDAYS  ( ) Custom  │
│  Cor:          [    sage    ▾]                         │
│                                                        │
│  Custom dias:  [ ] Seg [✓] Ter [ ] Qua [✓] Qui         │
│                [ ] Sex [ ] Sáb [ ] Dom                 │
│                                                        │
│       [Criar]                    [Cancelar]            │
└────────────────────────────────────────────────────────┘
```

O formulário aparece como overlay modal centralizado. Após criar, o hábito aparece imediatamente na grade nos dias correspondentes.

---

## Detalhe: Múltiplas Rotinas com Tab

```
┌─ ROTINAS ─────────────────────────────────────────────────────────── Sem 17─23 Fev 2026 ─┐
│ ▸ Rotina Matinal (ativa)  10 háb │  Rotina Noturna  4 háb │  Rotina FDS  3 háb │  +      │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

`Tab` move o foco entre rotinas no header. A grade abaixo atualiza para exibir os hábitos da rotina focada. A rotina ativa tem indicador `▸` e label `(ativa)`. Para ativar outra rotina, o usuário navega até ela com `Tab` e pressiona `a`.

---

## Responsividade

```
Terminal ≥ 120 colunas (ideal):
  7 colunas de dia (~12 chars cada) + régua de horas (~7 chars) + sidebar (22 chars)
  Todos os dias visíveis simultaneamente

Terminal 80─119 colunas (compacto):
  5 colunas visíveis (Seg─Sex por padrão), Sáb/Dom com scroll horizontal
  Nomes de hábitos truncados em 6 chars
  ←/→ faz scroll entre dias

Terminal < 80 colunas (minimal):
  3 colunas visíveis por vez
  ←/→ faz scroll entre dias
  Blocos mostram apenas cor/preenchimento sem label (tooltip obrigatório)
```

---

## Relação Dashboard vs. Rotinas

| Aspecto        | Dashboard                         | Rotinas                              |
| -------------- | --------------------------------- | ------------------------------------ |
| Escopo         | Dia atual                         | Semana inteira                       |
| Dados          | Instâncias reais (status)         | Templates (hábitos recorrentes)      |
| Eixo temporal  | Vertical (agenda do dia)          | Vertical (horas) + Horizontal (dias) |
| Interação      | Quick actions (done/skip)         | CRUD (criar/editar/deletar hábitos)  |
| Cor dos blocos | Por status (done/pending/running) | Por hábito (cor atribuída)           |
| Conflitos      | Exibe com borda vermelha          | Exibe com divisor vertical           |
| Navegação      | `g` vai para screen completa      | `g` vai para Habits (instâncias)     |
