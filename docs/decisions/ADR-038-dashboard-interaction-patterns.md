# ADR-038: Padrões de Interação do Dashboard

- **Status:** Aceito
- **Data:** 15 de Março de 2026
- **Contexto:** Definir padrões de interação modal e fluxos de usuário para o dashboard plenamente funcional

---

## Contexto

A revisão de testes e2e (Sprint 4.5) revelou ambiguidades, gaps de BRs e bugs
de aderência entre o código implementado e as regras documentadas. Esta ADR
consolida as decisões tomadas para resolver cada ponto e servir de referência
para implementação.

---

## Decisões

### D1. Undo é transição válida (DONE/NOT_DONE → PENDING)

O usuário pode clicar done ou skip por engano. A tecla `u` reverte o status
para PENDING. Isso supersede BR-HABITINSTANCE-001 que definia DONE e NOT_DONE
como estados finais. O undo deve limpar todos os campos de substatus:
`done_substatus`, `not_done_substatus`, `skip_reason`, `skip_note`,
`completion_percentage`.

O TimeLog associado permanece com status DONE — é registro factual de tempo
dedicado, não de decisão do usuário. Sistemas de referência (Toggl, Clockify,
Harvest) tratam time logs como registros imutáveis.

### D2. Re-done detecta TimeLog existente

Quando o usuário pressiona `v` em hábito PENDING que possui TimeLog DONE
vinculado, o sistema oferece restauração:

```plaintext
Modal: "Sessão anterior encontrada (25min, 83%). Restaurar?"
  [Sim] → restaura done_substatus e completion_percentage originais
  [Não] → abre modal de done manual (D3)
```

Isso elimina a necessidade de status UNDONE no TimeLog e de mecanismo de
retenção temporal.

### D3. Done manual (v sem timer) abre modal de substatus

Ao pressionar `v` sem timer ativo, o sistema abre um modal com Select das
opções de DoneSubstatus: FULL, PARTIAL, OVERDONE, EXCESSIVE. Mesma lógica
do CLI `habit done` que já oferece enum interativo.

Motivação: BR-HABITINSTANCE-002 exige done_substatus quando status=DONE.
Sem timer, não há cálculo automático de completion_percentage.

### D4. Done com timer ativo (v em hábito running) abre notificação

Ao pressionar `v` em hábito com timer ativo, o sistema abre modal informativo:

```plaintext
Modal: "Timer ativo para este hábito"
  [Parar timer e marcar done] → stop_timer + mark done com substatus calculado
  [Cancelar] → fecha modal, nenhuma ação
```

Resolve o gap do `TimerStopAndDoneRequest` sem handler.

### D5. Postpone (s) abre mesmo modal que edit (e)

Não há modal separado de postpone. A tecla `s` no tasks panel abre o mesmo
FormModal que `e`, com os mesmos campos (título, data, horário). A BR-TASK-008
(rastreamento de adiamento) é aplicada automaticamente pelo TaskService quando
a nova data é posterior à atual.

Referência de mercado: Todoist, TickTick e Things tratam postpone como
reschedule — um edit focado na data.

### D6. Skip (s no habits) sempre abre modal de SkipReason

A tecla `s` no habits panel abre modal com Select de SkipReason (HEALTH,
WORK, FAMILY, TRAVEL, WEATHER, LACK_RESOURCES, EMERGENCY, OTHER) e campo
opcional de nota. Mesma lógica do CLI `habit skip` que já oferece prompt
interativo (BR-SKIP-004).

O comportamento atual (SkipReason.OTHER hardcoded) é um placeholder que
viola BR-SKIP-001.

### D7. Tasks sem horário explícito: overdue baseado em data

Tasks criadas sem horário (scheduled_datetime com hora 00:00) são tratadas
como "dia inteiro". Não ficam overdue no mesmo dia — apenas a partir do dia
seguinte à data agendada. Tasks com horário explícito ficam overdue quando
o horário passa.

Nova regra: BR-TASK-011.

### D8. Timer único — bloquear início sem stop/cancel

BR-TIMER-001 define opções interativas (pausar atual + iniciar novo, cancelar

- iniciar novo, continuar). Para simplicidade da TUI, se o usuário tenta
  iniciar timer com outro ativo, o sistema exibe notificação de erro:

```plaintext
app.notify("Timer ativo. Pare ou cancele antes de iniciar novo.", severity="error")
```

Sem modal de opções por ora — o usuário usa `s` (stop) ou `c` (cancel) no
timer panel primeiro.

### D9. Criação sem rotina (n sem rotina ativa)

Quando o usuário pressiona `n` sem rotina ativa (independente do panel focado),
o sistema abre FormModal de criação de rotina com mensagem explicativa. Após
criar, retorna ao dashboard. O usuário precisa pressionar `n` novamente para
criar hábito.

Motivação: evitar fluxo encadeado complexo (criar rotina + criar hábito num
só fluxo).

### D10. Limites de exibição nos panels

Habits panel trunca em 12 items. Tasks panel trunca em 9 items. Valores
fixos por enquanto — configuráveis em screen de configurações futura.

### D11. ConfirmDialog retorna foco ao panel originador

BR-TUI-019 regra 8: "Ao fechar, foco retorna ao widget que abriu o modal."
Aplica-se a deleção (`x`), cancelamento de timer (`c`), e qualquer outro
ConfirmDialog.

### D12. Modals como padrão de interação

Toda ação que requer input ou confirmação do usuário deve usar modal
(FormModal ou ConfirmDialog). O sistema nunca executa ações destrutivas ou
que alteram estado silenciosamente. Princípio: "informar, nunca decidir"
estende-se para "perguntar antes de agir".

---

## Consequências

### Positivas

- Undo seguro com preservação de TimeLog
- Done manual adere a BR-HABITINSTANCE-002 (substatus obrigatório)
- Skip adere a BR-SKIP-001 (categorização obrigatória)
- Postpone reutiliza FormModal existente (DRY)
- Interação consistente via modals

### Negativas

- Aumento de modals pode gerar fricção para usuários avançados
  (mitigação futura: configuração para skip rápido sem modal)
- Undo + re-done com detecção de TimeLog adiciona complexidade
  ao handler de done

### Neutras

- Timer único sem opções interativas é simplificação temporária
- Limites fixos de exibição serão substituídos por configuração

---

## Referências

- ADR-037: Padrão de keybindings da TUI
- BR-HABITINSTANCE-001/002: Status e substatus
- BR-SKIP-001/002/004: Categorização de skip
- BR-TASK-007/008/009: Task lifecycle
- BR-TIMER-001/002/003: Timer states
- BR-TUI-019/020: ConfirmDialog e FormModal
