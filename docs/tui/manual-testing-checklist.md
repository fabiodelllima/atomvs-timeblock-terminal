# ATOMVS Time Planner Terminal — Checklist de Teste Manual da Dashboard

**Versão:** 1.0.0

**Referência:** ADR-037 (Padrão de Keybindings), ADR-034 (Dashboard-first CRUD)

---

## Instruções

Iniciar a aplicação com `atomvs tui` ou `python -m timeblock tui`.
Marcar cada item com [x] após validar. Anotar observações na coluna de notas.

**Pré-requisito:** nenhuma rotina ou dado existente (base limpa).
Para resetar: `rm ~/.local/share/atomvs/atomvs.db` antes de iniciar.

---

## 1. Primeiro Acesso (estado vazio)

- [x] Dashboard abre sem erro
- [ ] Agenda mostra mensagem de estado vazio
- [ ] HabitsPanel mostra placeholders
- [ ] TasksPanel mostra placeholders
- [x] TimerPanel mostra estado idle ("Nenhum timer ativo" ou similar)
- [x] MetricsPanel renderiza sem erro
- [ ] Status bar visível na parte inferior

**Notas:** _______________________________________________

---

## 2. Navegação Global

### 2.1. Troca de screens (1-5)

- [x] `1` → Dashboard (tela inicial)
- [x] `2` → Routines
- [x] `3` → Habits
- [x] `4` → Tasks
- [x] `5` → Timer
- [x] `1` → volta ao Dashboard

### 2.2. Help overlay

- [ ] `?` → abre help overlay com keybindings
- [ ] `?` novamente → fecha help overlay
- [ ] `Esc` → também fecha help overlay

### 2.3. Tab entre panels

- [x] `Tab` → foco muda para o próximo panel (borda muda de cor)
- [x] `Tab` repetido → cicla entre Habits, Tasks, Timer, Metrics
- [x] Panel focado é identificável visualmente

### 2.4. Saída

- [x] `Ctrl+Q` → sai da aplicação

**Notas:** _______________________________________________

---

## 3. Agenda Panel

### 3.1. Criação de rotina (pré-requisito para hábitos)

- [x] Focar Agenda (Tab até chegar, ou clicar)
- [x] `n` → abre FormModal de criação de rotina
- [x] Preencher nome (ex: "Rotina Matinal") → `Enter` → rotina criada
- [x] Agenda atualiza e mostra nome da rotina no header
- [ ] Atualiza Habits e Tasks conforme altera de Rotina para outra

### 3.2. Edição de rotina

- [x] `e` com Agenda focada → abre FormModal de edição de rotina
- [x] Nome pré-preenchido → alterar → `Enter` → nome atualizado

### 3.3. Deleção de rotina

- [ ] `x` com Agenda focada → abre ConfirmDialog
- [ ] `Enter` → confirma deleção, rotina removida
- [ ] Testar `Esc` no ConfirmDialog → cancela, rotina permanece

**Notas:** _______________________________________________

---

## 4. Habits Panel

**Pré-requisito:** rotina ativa criada (seção 3.1).

### 4.1. Navegação

- [x] `j` ou `seta baixo` → cursor move para próximo item
- [x] `i` ou `seta cima` → cursor move para item anterior
- [x] Cursor visualmente destacado (cor ou indicador)

### 4.2. Criação de hábito

- [x] Focar HabitsPanel (Tab)
- [ ] `n` → abre FormModal com 4 campos (título, horário, duração, recorrência)
- [ ] Preencher: título "Meditação", horário "08:00", duração "30"
- [ ] `Enter` → hábito criado, aparece no panel
- [ ] Criar segundo hábito (ex: "Leitura", "09:00", "60") → ambos visíveis

### 4.3. Criação sem rotina ativa (DT-040)

- [ ] Deletar a rotina (seção 3.3)
- [ ] Focar HabitsPanel → `n` → abre FormModal de criação de rotina (não de hábito)
- [x] Criar rotina → focar HabitsPanel → `n` → agora abre FormModal de hábito

### 4.4. Edição de hábito

- [x] Selecionar hábito com cursor → `e`
- [x] FormModal abre com dados pré-preenchidos (título, horário, duração)
- [ ] Alterar título → `Enter` → título atualizado no panel

### 4.5. Deleção de hábito

- [x] Selecionar hábito → `x`
- [ ] ConfirmDialog abre → `Enter` → hábito removido
- [x] Testar `Esc` no ConfirmDialog → hábito permanece

### 4.6. Marcar como done — `v` (sem timer)

- [x] Selecionar hábito pendente → `v`
- [x] FormModal de substatus abre (Select com: Completo, Parcial, Além do esperado, Excessivo)
- [x] Selecionar opção (default: Completo)
- [x] `Tab` até botão Confirmar → `Enter` → hábito marcado como done
- [x] Indicador visual muda (cor, ícone)

### 4.7. Skip — `s`

- [x] Selecionar hábito pendente → `s`
- [x] FormModal de skip abre (Select com 8 motivos + Input opcional para nota)
- [x] Selecionar motivo → `Tab` até Input de nota → escrever nota (opcional)
- [ ] `Enter` no Input → hábito marcado como not_done/skipped
- [x] Indicador visual muda

### 4.8. Undo — `u`

- [x] Selecionar hábito done ou skipped → `u`
- [x] Status volta para pending imediatamente (sem modal)
- [x] Indicador visual restaurado

### 4.9. Conflito de horários

- [ ] Criar dois hábitos com horários sobrepostos (ex: 08:00-10:00 e 09:00-11:00)
- [ ] Ambos são criados (sistema informa, não bloqueia — "informar, nunca decidir")

**Notas:** _______________________________________________

---

## 5. Tasks Panel

### 5.1. Navegação

- [x] `j` ou `seta baixo` → próxima task
- [x] `i` ou `seta cima` → task anterior

### 5.2. Criação de task

- [x] Focar TasksPanel → `n`
- [x] FormModal abre com campos: título, data (opcional), horário (opcional)
- [x] Preencher título → `Enter` → task criada com data de hoje

### 5.3. Edição de task

- [x] Selecionar task → `e`
- [x] FormModal abre com dados pré-preenchidos → alterar → `Enter` → atualizado

### 5.4. Deleção de task

- [x] Selecionar task → `x`
- [x] ConfirmDialog → `Enter` → task removida

### 5.5. Completar — `v`

- [x] Selecionar task pendente → `v`
- [x] Task marcada como completed (sem modal — ação direta)
- [x] Task aparece na seção "recentes" com status completed

### 5.6. Postpone (adiar) — `s`

- [x] Selecionar task pendente → `s`
- [x] FormModal de edição abre com dados pré-preenchidos (mesma tela que `e`)
- [x] Alterar data/horário → `Enter` → task atualizada com nova data

### 5.7. Cancelar — `c`

- [x] Selecionar task → `c`
- [x] Task marcada como cancelled (sem modal — ação direta)
- [x] Task aparece na seção "recentes" com status cancelled

### 5.8. Reabrir — `u`

- [x] Selecionar task cancelled → `u`
- [x] Task volta para pending (sem modal — ação direta)

**Notas:** _______________________________________________

---

## 6. Timer Panel

**Pré-requisito:** rotina com hábito criado (seções 3.1 e 4.2).

### 6.1. Iniciar timer — `t` no HabitsPanel

- [x] Focar HabitsPanel → selecionar hábito pendente → `t`
- [x] TimerPanel atualiza: mostra nome do hábito, cronômetro rodando
- [ ] Status do hábito muda para "running"

### 6.2. Pausar / Resumir — `space` no TimerPanel

- [ ] Focar TimerPanel → `space` → timer pausa (ícone/cor muda)
- [x] `space` novamente → timer resume

### 6.3. Parar timer — `s` no TimerPanel

- [x] Focar TimerPanel (com timer ativo) → `s`
- [x] Timer para, hábito marcado como done automaticamente
- [x] Substatus calculado automaticamente (partial/full/overdone/excessive)
- [x] TimerPanel volta para estado idle

### 6.4. Cancelar timer — `c` no TimerPanel

- [x] Iniciar timer → focar TimerPanel → `c`
- [x] ConfirmDialog: "Cancelar timer ativo? A sessão será descartada."
- [x] `Enter` → timer cancelado, hábito volta para pending
- [x] `Esc` → timer continua rodando

### 6.5. Done com timer ativo — `v` no HabitsPanel

- [ ] Iniciar timer → focar HabitsPanel → `v` no hábito running
- [ ] ConfirmDialog: "Parar timer e marcar como concluído?"
- [ ] `Enter` → timer para, hábito marcado done com substatus calculado

### 6.6. Timer bloqueio (um timer por vez)

- [ ] Com timer ativo no hábito A → tentar `t` no hábito B
- [ ] Segundo timer não inicia (um timer por vez — BR-TIMER-001)

**Notas:** _______________________________________________

---

## 7. Metrics Panel

- [ ] MetricsPanel renderiza sem erro com dados vazios
- [ ] Com hábitos done, panel atualiza (funcionalidade parcial — xfail em testes)

**Notas:** _______________________________________________

---

## 8. Modais — Validação Cruzada

### 8.1. FormModal

- [ ] `Tab` navega entre campos
- [ ] `Enter` em campo Input submete o formulário
- [ ] `Tab` até botão Confirmar + `Enter` submete (importante para formulários Select-only)
- [ ] `Esc` cancela e fecha sem persistir
- [ ] Validação inline: campo obrigatório vazio → mensagem de erro
- [ ] Validação inline: horário inválido (ex: "25:00") → mensagem de erro
- [ ] Validação inline: duração negativa ou zero → mensagem de erro

### 8.2. ConfirmDialog

- [ ] `Enter` → confirma ação
- [ ] `Esc` → cancela, nenhuma alteração persistida

**Notas:** _______________________________________________

---

## 9. Cenários Combinados

### 9.1. Fluxo completo do dia

- [ ] Criar rotina "Dia Produtivo"
- [ ] Criar 3 hábitos (Meditação 08:00/30min, Estudo 09:00/60min, Exercício 10:30/45min)
- [ ] Criar 2 tasks (Compras, Relatório)
- [ ] Iniciar timer no primeiro hábito → pausar → resumir → parar
- [ ] Marcar segundo hábito como done via `v` (sem timer)
- [ ] Skip terceiro hábito com motivo "Saúde"
- [ ] Completar primeira task
- [ ] Adiar segunda task para amanhã
- [ ] Verificar: 2 done, 1 skip, 1 task completed, 1 task pendente com nova data

### 9.2. Undo completo

- [ ] Marcar hábito done → `u` → volta pending
- [ ] Skip hábito → `u` → volta pending
- [ ] Cancelar task → `u` → volta pending

### 9.3. Cancelamento de modais

- [ ] `n` em HabitsPanel → `Esc` → nenhum hábito criado
- [ ] `e` em hábito → `Esc` → nenhuma alteração
- [ ] `x` em hábito → `Esc` → hábito permanece
- [ ] `v` em hábito → `Esc` no FormModal → status permanece pending
- [ ] `s` em hábito → `Esc` no FormModal → status permanece pending

**Notas:** _______________________________________________

---

## Resultado

| Seção                  | Total  | Passou | Falhou | N/A |
| ---------------------- | ------ | ------ | ------ | --- |
| 1. Primeiro Acesso     | 7      |        |        |     |
| 2. Navegação Global    | 12     |        |        |     |
| 3. Agenda Panel        | 8      |        |        |     |
| 4. Habits Panel        | 19     |        |        |     |
| 5. Tasks Panel         | 12     |        |        |     |
| 6. Timer Panel         | 11     |        |        |     |
| 7. Metrics Panel       | 2      |        |        |     |
| 8. Modais              | 9      |        |        |     |
| 9. Cenários Combinados | 14     |        |        |     |
| **TOTAL**              | **94** |        |        |     |

**Testador:** _______________________________________________

**Data do teste:** _______________________________________________

**Versão testada:** _______________________________________________

**Observações gerais:** _______________________________________________

---

**Data:** 17/03/2026
