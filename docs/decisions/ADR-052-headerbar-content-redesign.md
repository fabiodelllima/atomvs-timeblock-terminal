# ADR-052: Redesign do Conteúdo Interno do HeaderBar

- **Status:** Aceito
- **Data:** 2026-04-16

---

## Contexto

A v1.7.2 reestruturou o HeaderBar para usar `border_title` (rotina ativa) e `border_subtitle` (data por extenso) nativos do Textual. O conteúdo interno ficou com elementos legados: nome da rotina duplicado com o `border_title`, progress bar zerada (`0/0 ░░░░░░░░░░ 0%`), contagem de tasks sem contexto, e timer hardcoded (`⏹ --:--`). A implementação atual também faz duas chamadas separadas ao `RoutineService.get_active_routine()` no mesmo refresh.

Apps de referência TUI (btop, k9s, lazygit) convergem em três princípios para barras superiores: (1) contexto estável no border, métricas dinâmicas no conteúdo; (2) omissão ou dim quando o dado não existe, nunca placeholder zerado; (3) densidade proporcional ao viewport.

A issue #52 identificou a necessidade de especificar o comportamento do conteúdo interno em todos os estados possíveis.

---

## Decisão

O conteúdo interno do HeaderBar exibe três seções separadas por `[dim]│[/dim]`:

**Seção 1 — Progresso semanal de hábitos.** Formato: `Hábitos X/Y ▪▪▪▪▪▪░░░░ ZZ%`. X = hábitos com ao menos uma instância DONE na semana (segunda a domingo corrente). Y = total de hábitos ativos da rotina × dias transcorridos. Barra visual com 10 caracteres, proporcional ao percentual. Quando sem rotina ativa: `[dim]Hábitos --/--[/dim]` sem barra.

**Seção 2 — Progresso de tarefas do dia.** Formato: `Tarefas X/Y ▪▪▪░░ ZZ%`. X = tarefas concluídas hoje. Y = total de tarefas com deadline hoje ou sem deadline (pendentes). Barra visual com 5 caracteres. Quando Y = 0 (sem tarefas): `[dim]Sem tarefas[/dim]`. Quando X = Y e Y > 0: cor C_SUCCESS na barra.

**Seção 3 — Próximo item.** Formato: `Próximo: {nome} em {countdown}`. Exibe o próximo hábito com `scheduled_start` futuro ou a próxima tarefa com horário hoje, o que vier primeiro cronologicamente. Countdown em formato relativo: `em 25min`, `em 1h15`. Quando não há itens pendentes restantes hoje: `[dim]Sem próximos hoje[/dim]`. Nome truncado com `…` se exceder espaço disponível.

**Layout e separadores:** as três seções são distribuídas com espaçamento proporcional à largura disponível. Separador `[dim]│[/dim]` entre seções. Em viewports < 80 colunas, seção 3 colapsa primeiro; abaixo de 60, seção 2 colapsa também.

**Eliminação de redundância:** a chamada ao `RoutineService.get_active_routine()` é feita uma única vez em `_refresh_content()` e o resultado alimenta tanto o `border_title` quanto a seção 1. O nome da rotina não aparece no conteúdo interno.

**Timer removido do header:** o TimerPanel já exibe timer com mais detalhe. O header não duplica essa informação.

**Call-to-action removido do header:** hints e instruções vivem exclusivamente no footer (BR-TUI-034).

---

## Consequências

- Requer novo método na service layer para calcular progresso semanal de hábitos (soma de instâncias DONE na semana corrente)
- Requer novo método para identificar próximo item pendente com countdown
- BR-TUI-035 formaliza as regras com testes de validação
- `_get_routine_info()`, `_get_timer_info()` e `_get_active_routine_name()` são substituídos por métodos coesos com responsabilidade única
- Snapshots e2e do dashboard precisam de regeneração
- Issue #52 fechada por esta implementação
