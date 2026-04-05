# Task

A Task é o complemento pontual dos Habits recorrentes. Enquanto hábitos representam identidade e repetição ("sou alguém que lê todos os dias"), tasks representam compromissos únicos e finitos ("dentista dia 25 às 14h", "entregar relatório até sexta"). São os eventos que não fazem parte do plano ideal da semana, mas que precisam ocupar espaço na agenda e competir por atenção com os blocos de hábitos.

A independência estrutural da Task em relação à Routine é uma decisão deliberada de design. Uma tarefa de trabalho não pertence à "Rotina Matinal" nem à "Rotina Noturna" — ela existe por si só, visível independente de qual rotina está ativa. Trocar de rotina não esconde tarefas pendentes. Deletar uma rotina não afeta tarefas. Essa separação garante que compromissos pontuais nunca desapareçam acidentalmente ao reorganizar hábitos recorrentes.

O modelo de Task evoluiu de um checkbox simples para uma entidade com lifecycle rastreável (ADR-036). O status é derivado de timestamps — `completed_datetime`, `cancelled_datetime` e `scheduled_datetime` — sem enum explícito, seguindo a mesma filosofia de auditabilidade do restante do domínio. Quatro estados são derivados por precedência fixa: CANCELLED, COMPLETED, OVERDUE e PENDING (BR-TASK-007). Adiamentos são rastreados via `original_scheduled_datetime` (imutável, fixado na criação) e `postponement_count` (incrementado a cada reagendamento para data posterior), permitindo análise de padrões de procrastinação (BR-TASK-008). Cancelamento opera como soft delete — o registro permanece no banco com `cancelled_datetime` preenchido, preservando dados para métricas (BR-TASK-009). A partir desses timestamps, métricas como tempo até conclusão, taxa de pontualidade e frequência de adiamento são calculadas sob demanda (BR-TASK-010).

Não há prioridade, não há subtarefas, não há dependências. O TimeBlock Planner não é um gerenciador de projetos. Tasks existem para que eventos pontuais possam ser posicionados na linha do tempo ao lado dos hábitos, criando uma visão completa do dia — e para que o sistema possa detectar conflitos entre tasks e hábitos da rotina.

### BR-TASK-001: Estrutura de Task

**Descrição:** Task é evento pontual não-recorrente. Funciona como checkbox com data/hora.

**Campos:**

```python
class Task(SQLModel, table=True):
    id: int | None
    title: str                           # 1-200 chars
    scheduled_datetime: datetime         # Quando executar
    completed_datetime: datetime | None  # Quando foi concluido
    description: str | None              # Texto opcional
    color: str | None                    # Cor hexadecimal
    tag_id: int | None                   # FK opcional para Tag
```

**Características:**

- NÃO tem status enum (usa completed_datetime)
- NÃO tem priority
- NÃO tem timer
- NÃO tem deadline separado
- NÃO pertence a routine

**Testes:**

- `test_br_task_001_create_basic`
- `test_br_task_001_title_required`

---

### BR-TASK-002: Conclusão de Task

**Descrição:** Task é marcada como concluída via `completed_datetime`.

**Estados:**

- `completed_datetime = None` → Pendente
- `completed_datetime = datetime` → Concluida

**Comando:**

```bash
$ task complete 42
[OK] Task "Dentista" marcada como concluída
```

**Comportamento:**

- Sistema registra timestamp atual
- Task sai da lista de pendentes
- Aparece em histórico

**Testes:**

- `test_br_task_002_complete_sets_datetime`
- `test_br_task_002_pending_no_datetime`

---

### BR-TASK-003: Independência de Routine

**Descrição:** Tasks são independentes de routines.

**Regras:**

1. Task não tem campo routine_id
2. `task list` mostra todas tasks
3. Mudar rotina ativa não afeta tasks
4. Deletar rotina não afeta tasks

**Testes:**

- `test_br_task_003_no_routine_field`
- `test_br_task_003_list_all_tasks`
- `test_br_task_003_routine_change_no_effect`

---

### BR-TASK-004: Visualização e Listagem

**Descrição:** Tasks podem ser listadas com filtros.

**Filtros:**

- Por status (pendentes, concluídas)
- Por data (hoje, semana, mes)
- Por tag

**Ordenação:** Cronológica por scheduled_datetime

**Comandos:**

```bash
task list              # Pendentes
task list --today      # Hoje
task list --completed  # Concluidas
task list --all        # Todas
```

**Testes:**

- `test_br_task_004_list_pending`
- `test_br_task_004_filter_today`
- `test_br_task_004_filter_completed`

---

### BR-TASK-005: Atualização de Task

**Descrição:** Task pode ser atualizada conforme seu estado.

**Campos Atualizáveis (Task Pendente):**

- title
- description
- scheduled_datetime
- color
- tag_id

**Campos Atualizáveis (Task Concluída):**

- Apenas reversão de status (voltar para pendente)

**Reversão de Status:**

```bash
# Via flag explícita
task edit ID --status pending

# Via comando de atalho
task uncheck ID
task reopen ID
```

**Comportamento da Reversão:**

- Remove `completed_datetime` (= None)
- Task volta para lista de pendentes
- Permite edição completa novamente

**Erro ao Editar Concluída:**

```plaintext
[ERROR] Tarefa já concluída. Use --status pending para reabrir antes de editar.
```

**Testes:**

- `test_br_task_005_update_pending`
- `test_br_task_005_update_completed_only_status`
- `test_br_task_005_reopen_allows_edit`

---

### BR-TASK-006: Simplicidade Mantida

**Descrição:** Tasks são intencionalmente simples no MVP.

**NÃO implementado:**

- Timer tracking
- Subtasks
- Dependencias entre tasks
- Priorização explícita
- Checklist interno

**Justificativa:** Foco do TimeBlock está em hábitos e rotinas. Tasks são complemento para atividades pontuais.

---

### BR-TASK-007: Task Lifecycle — Derivação de Status (NOVA 14/03/2026)

**Descrição:** O status de uma Task é derivado de seus timestamps, sem campo enum explícito. A ordem de avaliação é determinística e com precedência fixa.

**Decisão arquitetural:** ADR-036

**Derivação (em ordem de precedência):**

1. `cancelled_datetime is not None` => CANCELLED
2. `completed_datetime is not None` => COMPLETED
3. `scheduled_datetime < now()` => OVERDUE
4. Caso contrário => PENDING

**Regras:**

1. Cancelamento tem precedência absoluta — mesmo que `completed_datetime` esteja preenchido, `cancelled_datetime` prevalece
2. A derivação é pura (sem side effects) e determinística (mesmos inputs => mesmo output)
3. Nenhum campo `status` é armazenado — o status é sempre calculado na leitura
4. A implementação deve ser um `@property` ou função utilitária, nunca lógica espalhada

**Testes:**

- `test_br_task_007_pending_status_derivation`
- `test_br_task_007_completed_status_derivation`
- `test_br_task_007_cancelled_status_derivation`
- `test_br_task_007_overdue_status_derivation`
- `test_br_task_007_cancelled_overrides_completed`

---

### BR-TASK-008: Rastreamento de Adiamento (NOVA 14/03/2026)

**Descrição:** Cada adiamento de task é rastreado para análise posterior de padrões comportamentais. O adiamento é ortogonal ao status — uma task pode estar em qualquer status e ter histórico de adiamentos.

**Decisão arquitetural:** ADR-036

**Campos:**

```python
original_scheduled_datetime: datetime  # Imutável, fixado na criação
postponement_count: int = 0            # Incrementado a cada adiamento
```

**Regras:**

1. `original_scheduled_datetime` é definido na criação da task com o valor de `scheduled_datetime` e nunca é alterado depois
2. `postponement_count` é incrementado quando `scheduled_datetime` é atualizado para uma data **posterior** à atual
3. Reagendar para data **anterior** (antecipação) não incrementa o contador
4. Reagendar para a mesma data/hora não incrementa o contador
5. O delta `scheduled_datetime - original_scheduled_datetime` fornece o adiamento total em dias

**Métricas derivadas:**

```python
was_postponed    = postponement_count > 0
days_postponed   = (scheduled_datetime - original_scheduled_datetime).days
avg_postponement = days_postponed / postponement_count  # se count > 0
```

**Testes:**

- `test_br_task_008_original_datetime_set_on_creation`
- `test_br_task_008_original_datetime_immutable_on_update`
- `test_br_task_008_postponement_count_increments_on_later_date`
- `test_br_task_008_postponement_count_unchanged_on_earlier_date`
- `test_br_task_008_postponement_count_unchanged_on_same_date`
- `test_br_task_008_days_postponed_calculation`

---

### BR-TASK-009: Cancelamento Soft Delete (NOVA 14/03/2026)

**Descrição:** Cancelar uma task registra o timestamp sem remover o registro do banco, preservando dados para métricas e histórico.

**Decisão arquitetural:** ADR-036

**Campo:**

```python
cancelled_datetime: datetime | None = None
```

**Regras:**

1. `task delete` seta `cancelled_datetime = datetime.now()` (soft delete)
2. Task cancelada sai da lista de pendentes mas permanece no banco
3. Task cancelada aparece no dashboard por 24h com status CANCELLED e strikethrough
4. Reverter cancelamento é possível zerando `cancelled_datetime` (via `task reopen`)
5. Hard delete (remoção permanente) disponível via `task purge` — operação futura, não implementada no MVP

**Impacto em operações:**

| Operação                | Comportamento                     |
| ----------------------- | --------------------------------- |
| `task list`             | Omite canceladas                  |
| `task list --all`       | Inclui canceladas                 |
| `task list --cancelled` | Apenas canceladas                 |
| Dashboard (TUI)         | Mostra canceladas das últimas 24h |

**Testes:**

- `test_br_task_009_cancel_sets_datetime`
- `test_br_task_009_cancel_preserves_record`
- `test_br_task_009_cancelled_excluded_from_pending`
- `test_br_task_009_cancelled_included_in_all`
- `test_br_task_009_reopen_clears_cancelled_datetime`

---

### BR-TASK-010: Métricas de Task Lifecycle (NOVA 14/03/2026)

**Descrição:** O sistema calcula métricas a partir dos timestamps do lifecycle para análise de produtividade e padrões comportamentais.

**Decisão arquitetural:** ADR-036

**Métricas por task:**

```python
# Tempo até conclusão (apenas tasks COMPLETED)
time_to_completion = completed_datetime - original_scheduled_datetime

# Pontualidade
completed_on_time = completed_datetime.date() <= original_scheduled_datetime.date()
days_late = max(0, (completed_datetime.date() - original_scheduled_datetime.date()).days)

# Adiamento (qualquer status)
was_postponed = postponement_count > 0
total_days_postponed = (scheduled_datetime - original_scheduled_datetime).days
```

**Métricas agregadas (período configurável):**

```python
# Taxas
completion_rate = completed_count / total_count
cancellation_rate = cancelled_count / total_count
on_time_rate = on_time_count / completed_count

# Adiamento
avg_postponement_count = sum(postponement_counts) / total_count
avg_days_postponed = sum(days_postponed) / postponed_count
most_postponed_tasks = top_n(tasks, key=postponement_count)

# Tempo
avg_time_to_completion = mean(time_to_completions)
```

**Regras:**

1. Métricas são calculadas sob demanda (query), não armazenadas
2. Período padrão: últimos 7 dias e últimos 30 dias
3. Tasks sem `original_scheduled_datetime` (migração) usam `scheduled_datetime` como fallback
4. Tasks PENDING/OVERDUE contribuem para contagem total mas não para métricas de conclusão
5. Estas métricas alimentam o futuro MetricsPanel (DT-017)

**Testes:**

- `test_br_task_010_time_to_completion_calculation`
- `test_br_task_010_on_time_detection`
- `test_br_task_010_days_late_calculation`
- `test_br_task_010_completion_rate`
- `test_br_task_010_cancellation_rate`
- `test_br_task_010_postponement_aggregates`
- `test_br_task_010_migration_fallback_original_datetime`

---

### BR-TASK-011: Tasks Sem Horario Explicito (NOVA 15/03/2026)

**Descricao:** Tasks criadas sem horario (scheduled_datetime com hora e minuto ambos zero) sao tratadas como "dia inteiro" e seguem regra de overdue diferente.

**Decisao arquitetural:** ADR-038 D7

**Regras:**

1. Task com `hour == 0 and minute == 0` e considerada "sem horario explicito"
2. Task sem horario explicito nao fica overdue no mesmo dia da data agendada
3. Task sem horario explicito fica overdue a partir do dia seguinte (`date < today`)
4. Task com horario explicito fica overdue quando `scheduled_datetime < now()`
5. Exibicao no dashboard: tasks sem horario mostram `"--:--"` no campo time
6. FormModal de edicao limpa `"--:--"` para string vazia no campo de horario

**Testes:**

- `test_br_task_011_no_time_not_overdue_same_day`
- `test_br_task_011_no_time_overdue_next_day`
- `test_br_task_011_with_time_overdue_after_hour`
- `test_br_task_011_display_no_time_shows_dashes`
- `test_br_task_011_edit_clears_dashes`
