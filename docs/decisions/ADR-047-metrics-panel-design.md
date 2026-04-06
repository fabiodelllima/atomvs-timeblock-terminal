# ADR-047: Design do MetricsPanel — Filosofia e Padrões

- **Status:** Proposto

- **Data:** 2026-04-03

## Contexto

O MetricsPanel foi implementado (DT-017, DT-026) sem especificação formal. O painel exibe streak, completude 7d/30d e heatmap semanal, mas apresenta problemas: dias anteriores mostram 0/0 porque `ensure_today_instances` só gera instâncias para o dia atual, e decisões de design não estão documentadas.

Apps de referência (Streaks, Stepwise, Habitify, HabitBoard, Loop, Habi) convergem em streak como mecânica central, heatmap estilo GitHub, e atualização reativa ao marcar completude.

A filosofia de Atomic Habits (CLEAR, 2018, Cap. 16) fundamenta três princípios para rastreamento visual: (1) **claro** — sinais visuais lembram o usuário de agir, (2) **atraente** — ver progresso alimenta motivação, (3) **satisfatório** — marcar completude é recompensa imediata. Sobre recuperação, Clear estabelece: "nunca quebre um hábito duas vezes — o primeiro erro é um acidente, a espiral de erros repetidos é o que leva tudo por água abaixo."

## Decisão

**Escopo:** Métricas agregadas da rotina ativa. Métricas por hábito individual deferidas para v2.0.

**Streak:** Dias consecutivos com pelo menos 1 hábito DONE. Skip e ausência de registro têm o mesmo efeito: o hábito não foi praticado. Um dia sem DONE pausa o streak. Dois dias consecutivos sem DONE quebram o streak — alinhado com a regra "nunca quebre duas vezes" de Clear.

**Heatmap:** Mostra `done/total` por dia, onde total = número de hábitos ativos da rotina. Dias sem instâncias geradas exibem `0/N`, não `0/0`, via geração retroativa de instâncias PENDING ao abrir o dashboard.

**Atualização reativa:** Marcar done/skip/undo recalcula métricas imediatamente no dashboard.

**Período:** 7d como padrão. Alternância para 14d/30d via keybinding `f`, informação exibida no footer contextual (status_bar) quando o MetricsPanel está focado — não no corpo do painel.

**Best streak:** Persistido no banco para não depender do limite temporal da query.

## Consequências

- Formaliza BR-TUI-033 com regras detalhadas do MetricsPanel
- Requer lógica de geração retroativa de instâncias PENDING
- Requer campo `best_streak` no modelo ou tabela dedicada
- Requer handler de keybinding `f` no MetricsPanel
- Itens de implementação registrados no `sprints.md` e `roadmap.md`

## Referências

- CLEAR, J. Atomic Habits. New York: Avery, 2018. Cap. 16.
- ISO/IEC/IEEE 29148:2018
- Stepwise App — Individual Habit Heatmaps
- HabitBoard — Streaks and Personal Agency
- Habi — Streak Protection
