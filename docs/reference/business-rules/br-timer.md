# Timer

O Timer fecha o loop de feedback do Atomic Habits. Planejar (Routine/Habit), executar (HabitInstance), e agora _medir_ — com precisão de segundos, quanto tempo o usuário realmente dedicou a cada atividade. James Clear escreve que "o que é medido é gerenciado", e o Timer torna essa medição automática e sem fricção: iniciar é um comando, pausar é outro, parar registra o tempo no banco.

O Timer opera sobre uma entidade única (um HabitInstance ou uma Task) e produz um TimeLog ao final: registro imutável com horário de início e fim reais. A diferença entre o tempo planejado (definido no Habit) e o tempo real (registrado pelo Timer) alimenta diretamente o cálculo de substatus da HabitInstance — o percentual de completude que determina se a execução foi FULL, PARTIAL, OVERDONE ou EXCESSIVE. Sem o Timer, o usuário precisaria informar manualmente a duração real ao marcar um hábito como concluído, o que introduz imprecisão e fricção.

O ciclo de vida do Timer inclui estados intermediários que refletem a realidade de uma sessão de trabalho: RUNNING (contando), PAUSED (interrupção temporária) e STOPPED (sessão encerrada e salva). O cancelamento descarta a sessão sem registro, útil quando o usuário inicia por engano ou decide que a atividade mudou de natureza. A visibilidade do timer ativo é global — ele aparece na status bar da TUI independente da screen, garantindo que o usuário nunca perca noção do tempo mesmo enquanto navega pelo sistema.

### BR-TIMER-001: Single Active Timer

**Descrição:** Apenas UM timer pode estar ATIVO (RUNNING ou PAUSED) por vez.

**Constraint:**

```python
active_timers = get_active_timers()  # status in [RUNNING, PAUSED]
assert len(active_timers) <= 1
```

**Comportamento:**

- Timer finalizado não bloqueia novo start
- Múltiplas sessões permitidas (start → stop → start)

**Erro:**

```bash
$ timer start Academia
[OK] Timer iniciado: Academia (00:00 / 01:30)

$ timer start Meditação
[ERROR] Timer já ativo: Academia (15min decorridos)

Opções:
  [1] Pausar Academia e iniciar Meditação
  [2] Cancelar Academia (reset) e iniciar Meditação
  [3] Continuar com Academia
```

**Testes:**

- `test_br_timer_001_only_one_active`
- `test_br_timer_001_error_if_already_running`
- `test_br_timer_001_stopped_not_blocking`

---

### BR-TIMER-002: Estados e Transições

**Descrição:** Timer possui 4 estados persistidos no banco (campo `status` em TimeLog).

**Estados:**

| Estado    | Descrição                              | Campos Afetados       |
| --------- | -------------------------------------- | --------------------- |
| RUNNING   | Timer contando tempo                   | status, start_time    |
| PAUSED    | Timer pausado temporariamente          | status, pause_start   |
| DONE      | Timer finalizado com stop (salva)      | status, end_time      |
| CANCELLED | Timer resetado (como se nunca iniciou) | status, cancel_reason |

**Máquina de Estados:**

```plaintext
[NO TIMER]
  │
  └─> start → RUNNING
              ├─> pause → PAUSED
              │            └─> resume → RUNNING
              ├─> stop → DONE
              └─> reset → CANCELLED
```

**Timer Ativo:** `status IN (RUNNING, PAUSED) AND end_time IS NULL`

**Comandos:**

| Comando | De             | Para      | Efeito                                   |
| ------- | -------------- | --------- | ---------------------------------------- |
| start   | NO TIMER       | RUNNING   | Cria timer, inicia contagem              |
| pause   | RUNNING        | PAUSED    | Pausa contagem, salva pause_start        |
| resume  | PAUSED         | RUNNING   | Retoma contagem, acumula paused_duration |
| stop    | RUNNING/PAUSED | DONE      | Salva sessão, atualiza instance          |
| reset   | RUNNING/PAUSED | CANCELLED | Cancela sessão, instance fica PENDING    |

**CLI Non-blocking:** Após `timer start`, terminal é liberado imediatamente. Usuário controla via comandos separados.

**Transições Inválidas:**

| Comando | Estado Atual | Erro                    |
| ------- | ------------ | ----------------------- |
| pause   | PAUSED       | "Timer already paused"  |
| resume  | RUNNING      | "Timer already running" |

**Comportamento:** Transições inválidas retornam `ValueError` com mensagem descritiva.

**Testes:**

- `test_br_timer_002_start_creates_running`
- `test_br_timer_002_pause_from_running`
- `test_br_timer_002_resume_from_paused`
- `test_br_timer_002_stop_creates_done`
- `test_br_timer_002_reset_creates_cancelled`
- `test_br_timer_002_status_persists_in_db`
- `test_br_timer_002_cannot_pause_when_paused`
- `test_br_timer_002_cannot_resume_when_running`

---

### BR-TIMER-003: Stop vs Reset

**Descrição:** `stop` e `reset` finalizam timer com comportamentos diferentes.

**stop:**

- Muda status para DONE
- Preenche end_time e duration_seconds
- Atualiza HabitInstance (status=DONE, calcula substatus)
- Permite start novamente (nova sessão)

**reset:**

- Muda status para CANCELLED
- Preenche cancel_reason (opcional via --reason)
- HabitInstance permanece PENDING
- Sessão não conta nos relatórios

**Reset de sessão específica:**

```bash
# Reset timer ativo (RUNNING ou PAUSED)
timer reset
timer reset --reason "Iniciei habit errado"

# Reset sessão já finalizada (DONE)
timer reset --session <TIMELOG_ID>
timer reset --session <TIMELOG_ID> --reason "Contabilizei no habit errado"
```

**Validações reset --session:**

| Cenário             | Comportamento                 |
| ------------------- | ----------------------------- |
| Sessão não existe   | Erro: "Sessão não encontrada" |
| Sessão já CANCELLED | Erro: "Sessão já cancelada"   |
| Sessão DONE         | Permite cancelar              |

**Modelo TimeLog - campos relacionados:**

| Campo         | Tipo | Descrição                         |
| ------------- | ---- | --------------------------------- |
| status        | enum | RUNNING/PAUSED/DONE/CANCELLED     |
| notes         | str  | Anotações do usuário sobre sessão |
| cancel_reason | str  | Motivo do reset (só se CANCELLED) |

**Testes:**

- `test_br_timer_003_stop_saves_session`
- `test_br_timer_003_stop_updates_instance`
- `test_br_timer_003_reset_cancels_active`
- `test_br_timer_003_reset_keeps_pending`
- `test_br_timer_003_reset_with_reason`
- `test_br_timer_003_reset_specific_session`
- `test_br_timer_003_reset_already_cancelled_error`

---

### BR-TIMER-004: Múltiplas Sessóes

**Descrição:** Usuário pode fazer múltiplas sessões do mesmo habit no mesmo dia.

**Workflow:**

```python
# Sessão 1 (manhá)
timer1 = start_timer(instance_id=42)
timer1.stop()  # SALVA (60min)

# Sessão 2 (tarde)
timer2 = start_timer(instance_id=42)
timer2.stop()  # SALVA (30min)

# Total: 90min (acumulado)
```

**Substatus:** Calculado sobre tempo acumulado de todas sessões.

**Testes:**

- `test_br_timer_004_multiple_sessions`
- `test_br_timer_004_accumulates_duration`

---

### BR-TIMER-005: Cálculo de Completion

**Descrição:** Completion percentage calculado ao parar timer.

**Formula:**

```python
total_actual = sum(session.duration for session in sessions)
completion = (total_actual / expected_duration) * 100
```

**Testes:**

- `test_br_timer_005_completion_formula`
- `test_br_timer_005_multiple_sessions_accumulated`

---

### BR-TIMER-006: Pause Tracking

**Descrição:** Sistema rastreia pausas via campo acumulado `paused_duration`.

**Fluxo:**

```plaintext
10:00 - start_timer()
10:30 - pause_timer()
10:45 - resume_timer()  # paused_duration = 15min
11:00 - stop_timer()    # duration = 60min - 15min = 45min
```

**Cálculo:**

```python
effective_duration = total_duration - paused_duration
```

**Testes:**

- `test_br_timer_006_pause_tracking`
- `test_br_timer_006_multiple_pauses`
- `test_br_timer_006_effective_duration`

---

### BR-TIMER-007: Log Manual

**Descrição:** Usuário pode registrar tempo manualmente sem usar timer.

**Comando:**

```bash
habit log INSTANCE_ID --start 07:00 --end 08:30
# ou
habit log INSTANCE_ID --duration 90
```

**Validações:**

- start < end
- duration > 0

**Testes:**

- `test_br_timer_007_manual_log_times`
- `test_br_timer_007_manual_log_duration`

---

### BR-TIMER-008: Listagem de TimeLogs

**Descrição:** Sistema permite listar timelogs com filtros opcionais.

**Filtros Disponíveis:**

- `habit_instance_id`: Filtra por instância específica
- `date_start`: Data inicial do período
- `date_end`: Data final do período

**Comportamento:**

- Sem filtros: retorna todos os timelogs
- Com filtros: aplica AND entre filtros fornecidos
- Nenhum resultado: retorna lista vazia (nunca None)
- Ordenação: por start_time ascendente

**Testes:**

- `test_br_timer_008_list_all`
- `test_br_timer_008_filter_by_instance`
- `test_br_timer_008_filter_by_date_range`
- `test_br_timer_008_returns_empty_list`
- `test_br_timer_007_validates_times`

---

### BR-TIMER-009: Registro de Motivo de Pausa (NOVA 21/03/2026)

**Descrição:** Quando o usuário dá resume após uma pausa, a TUI deve oferecer um modal opcional para registrar o que foi feito durante o intervalo. O registro é classificado por tags de atividade, permitindo mapeamento de padrões de procrastinação e uso de tempo entre blocos.

**Regras:**

1. Ao pressionar resume (após pause), exibir modal com campo de descrição e select de tag
2. Tags de pausa são pré-definidas: foco_perdido, descanso, urgencia, alimentacao, higiene, redes_sociais, outro
3. O modal é opcional — usuário pode pular clicando "Continuar sem registrar"
4. Se registrado, o motivo é salvo como `PauseNote` vinculado ao `TimeLog` atual
5. Cada `TimeLog` pode ter múltiplos `PauseNote` (uma pausa pode acontecer várias vezes)
6. O timer resume imediatamente após fechar o modal (com ou sem registro)
7. Métricas de pausa são agregáveis por tag para análise de padrões (ex: 40% foco_perdido, 30% redes_sociais)

**Modelo de dados proposto:**

```python
PauseNote:
  id: int (PK)
  time_log_id: int (FK → time_log.id)
  tag: PauseTag (enum)
  description: str | None
  created_at: datetime
```

**Testes:**

- `test_br_timer_009_resume_shows_pause_modal`
- `test_br_timer_009_skip_modal_resumes_immediately`
- `test_br_timer_009_pause_note_saved_with_tag`
- `test_br_timer_009_multiple_pauses_multiple_notes`
- `test_br_timer_009_metrics_aggregate_by_tag`

---

### BR-TIMER-010: Rastreamento de Atividade Durante Pausa

**Descrição:** Quando o usuário dá resume após uma pausa, o sistema oferece um modal para registrar o que foi feito durante o intervalo. Diferente de BR-TIMER-009 (que categoriza o _motivo_ da pausa), esta regra rastreia a _atividade realizada_ durante o intervalo — alinhado com o princípio de Atomic Habits (CLEAR, 2018, Cap. 16) de tornar o uso do tempo visível e rastreável.

**Fases:**

Fase 1 (v1.8.0): registro descritivo. Fase 2 (futuro, atrás de feature toggle): atribuição retroativa de tempo.

**Regras — Fase 1:**

1. Ao pressionar resume, exibir modal com três opções: (a) selecionar outro habit da rotina ativa, (b) selecionar uma task pendente, (c) nota livre (campo de texto)
2. O modal é opcional — "Continuar sem registrar" fecha e resume imediatamente
3. Registro salvo como `PauseLog` com campo `note: str | None` (novo campo)
4. Cada `TimeLog` pode ter múltiplos `PauseLog` (múltiplas pausas por sessão)
5. O timer resume imediatamente após fechar o modal
6. AgendaPanel NÃO é alterado na Fase 1

**Regras — Fase 2 (atrás de toggle, ADR-048):**

7. Se o usuário selecionou habit/task, o tempo da pausa pode ser atribuído retroativamente como sessão daquele item
8. Blocos atribuídos aparecem no AgendaPanel com indicador visual de "sessão durante pausa"
9. Depende de ADR-041 (AgendaPanel redesign) para renderização dos blocos

**Modelo de dados — alteração em PauseLog:**

```python
PauseLog:
  id: int (PK)
  timelog_id: int (FK -> time_log.id)
  pause_start: datetime
  pause_end: datetime | None
  note: str | None          # NOVO — texto livre ou nome do item selecionado
  activity_type: str | None # NOVO — "habit", "task", "free", None
  activity_id: int | None   # NOVO — FK para habit_instance ou task (Fase 2)
  created_at: datetime
```

**Testes:**

- `test_br_timer_010_resume_shows_activity_modal`
- `test_br_timer_010_skip_modal_resumes_immediately`
- `test_br_timer_010_note_saved_to_pauselog`
- `test_br_timer_010_select_habit_saves_reference`
- `test_br_timer_010_select_task_saves_reference`
- `test_br_timer_010_multiple_pauses_multiple_logs`
