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

- [ ] Dashboard abre sem erro
- [ ] Agenda mostra mensagem de estado vazio
- [ ] HabitsPanel mostra placeholders
- [ ] TasksPanel mostra placeholders
- [ ] TimerPanel mostra estado idle ("Nenhum timer ativo" ou similar)
- [ ] MetricsPanel renderiza sem erro
- [ ] Status bar visível na parte inferior

**Notas:** _______________________________________________

---

## 2. Navegação Global

### 2.1. Troca de screens (1-5)

- [ ] `1` → Dashboard (tela inicial)
- [ ] `2` → Routines
- [ ] `3` → Habits
- [ ] `4` → Tasks
- [ ] `5` → Timer
- [ ] `1` → volta ao Dashboard

### 2.2. Help overlay

- [ ] `?` → abre help overlay com keybindings
- [ ] `?` novamente → fecha help overlay
- [ ] `Esc` → também fecha help overlay

### 2.3. Tab entre panels

- [ ] `Tab` → foco muda para o próximo panel (borda muda de cor)
- [ ] `Tab` repetido → cicla entre Habits, Tasks, Timer, Metrics
- [ ] Panel focado é identificável visualmente

### 2.4. Saída

- [ ] `Ctrl+Q` → sai da aplicação

**Notas:** _______________________________________________

---

## 3. Agenda Panel

### 3.1. Criação de rotina (pré-requisito para hábitos)

- [ ] Focar Agenda (Tab até chegar, ou clicar)
- [ ] `n` → abre FormModal de criação de rotina
- [ ] Preencher nome (ex: "Rotina Matinal") → `Enter` → rotina criada
- [ ] Agenda atualiza e mostra nome da rotina no header

### 3.2. Edição de rotina

- [ ] `e` com Agenda focada → abre FormModal de edição de rotina
- [ ] Nome pré-preenchido → alterar → `Enter` → nome atualizado

### 3.3. Deleção de rotina

- [ ] `x` com Agenda focada → abre ConfirmDialog
- [ ] `Enter` → confirma deleção, rotina removida
- [ ] Testar `Esc` no ConfirmDialog → cancela, rotina permanece

**Notas:** _______________________________________________

---

## 4. Habits Panel

**Pré-requisito:** rotina ativa criada (seção 3.1).

### 4.1. Navegação

- [ ] `j` ou `seta baixo` → cursor move para próximo item
- [ ] `i` ou `seta cima` → cursor move para item anterior
- [ ] Cursor visualmente destacado (cor ou indicador)

### 4.2. Criação de hábito

- [ ] Focar HabitsPanel (Tab)
- [ ] `n` → abre FormModal com 4 campos (título, horário, duração, recorrência)
- [ ] Preencher: título "Meditação", horário "08:00", duração "30"
- [ ] `Enter` → hábito criado, aparece no panel
- [ ] Criar segundo hábito (ex: "Leitura", "09:00", "60") → ambos visíveis

### 4.3. Criação sem rotina ativa (DT-040)

- [ ] Deletar a rotina (seção 3.3)
- [ ] Focar HabitsPanel → `n` → abre FormModal de criação de rotina (não de hábito)
- [ ] Criar rotina → focar HabitsPanel → `n` → agora abre FormModal de hábito

### 4.4. Edição de hábito

- [ ] Selecionar hábito com cursor → `e`
- [ ] FormModal abre com dados pré-preenchidos (título, horário, duração)
- [ ] Alterar título → `Enter` → título atualizado no panel

### 4.5. Deleção de hábito

- [ ] Selecionar hábito → `x`
- [ ] ConfirmDialog abre → `Enter` → hábito removido
- [ ] Testar `Esc` no ConfirmDialog → hábito permanece

### 4.6. Marcar como done — `v` (sem timer)

- [ ] Selecionar hábito pendente → `v`
- [ ] FormModal de substatus abre (Select com: Completo, Parcial, Além do esperado, Excessivo)
- [ ] Selecionar opção (default: Completo)
- [ ] `Tab` até botão Confirmar → `Enter` → hábito marcado como done
- [ ] Indicador visual muda (cor, ícone)

### 4.7. Skip — `s`

- [ ] Selecionar hábito pendente → `s`
- [ ] FormModal de skip abre (Select com 8 motivos + Input opcional para nota)
- [ ] Selecionar motivo → `Tab` até Input de nota → escrever nota (opcional)
- [ ] `Enter` no Input → hábito marcado como not_done/skipped
- [ ] Indicador visual muda

### 4.8. Undo — `u`

- [ ] Selecionar hábito done ou skipped → `u`
- [ ] Status volta para pending imediatamente (sem modal)
- [ ] Indicador visual restaurado

### 4.9. Conflito de horários

- [ ] Criar dois hábitos com horários sobrepostos (ex: 08:00-10:00 e 09:00-11:00)
- [ ] Ambos são criados (sistema informa, não bloqueia — "informar, nunca decidir")

**Notas:** _______________________________________________

---

## 5. Tasks Panel

### 5.1. Navegação

- [ ] `j` ou `seta baixo` → próxima task
- [ ] `i` ou `seta cima` → task anterior

### 5.2. Criação de task

- [ ] Focar TasksPanel → `n`
- [ ] FormModal abre com campos: título, data (opcional), horário (opcional)
- [ ] Preencher título → `Enter` → task criada com data de hoje

### 5.3. Edição de task

- [ ] Selecionar task → `e`
- [ ] FormModal abre com dados pré-preenchidos → alterar → `Enter` → atualizado

### 5.4. Deleção de task

- [ ] Selecionar task → `x`
- [ ] ConfirmDialog → `Enter` → task removida

### 5.5. Completar — `v`

- [ ] Selecionar task pendente → `v`
- [ ] Task marcada como completed (sem modal — ação direta)
- [ ] Task aparece na seção "recentes" com status completed

### 5.6. Postpone (adiar) — `s`

- [ ] Selecionar task pendente → `s`
- [ ] FormModal de edição abre com dados pré-preenchidos (mesma tela que `e`)
- [ ] Alterar data/horário → `Enter` → task atualizada com nova data

### 5.7. Cancelar — `c`

- [ ] Selecionar task → `c`
- [ ] Task marcada como cancelled (sem modal — ação direta)
- [ ] Task aparece na seção "recentes" com status cancelled

### 5.8. Reabrir — `u`

- [ ] Selecionar task cancelled → `u`
- [ ] Task volta para pending (sem modal — ação direta)

**Notas:** _______________________________________________

---

## 6. Timer Panel

**Pré-requisito:** rotina com hábito criado (seções 3.1 e 4.2).

### 6.1. Iniciar timer — `t` no HabitsPanel

- [ ] Focar HabitsPanel → selecionar hábito pendente → `t`
- [ ] TimerPanel atualiza: mostra nome do hábito, cronômetro rodando
- [ ] Status do hábito muda para "running"

### 6.2. Pausar / Resumir — `space` no TimerPanel

- [ ] Focar TimerPanel → `space` → timer pausa (ícone/cor muda)
- [ ] `space` novamente → timer resume

### 6.3. Parar timer — `s` no TimerPanel

- [ ] Focar TimerPanel (com timer ativo) → `s`
- [ ] Timer para, hábito marcado como done automaticamente
- [ ] Substatus calculado automaticamente (partial/full/overdone/excessive)
- [ ] TimerPanel volta para estado idle

### 6.4. Cancelar timer — `c` no TimerPanel

- [ ] Iniciar timer → focar TimerPanel → `c`
- [ ] ConfirmDialog: "Cancelar timer ativo? A sessão será descartada."
- [ ] `Enter` → timer cancelado, hábito volta para pending
- [ ] `Esc` → timer continua rodando

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
