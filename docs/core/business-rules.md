# Business Rules - TimeBlock Organizer

**Versao:** 3.0.0
**Data:** 28 de Novembro de 2025
**Status:** Consolidado (SSOT)

---

## Indice

1. [Introducao e Fundamentos](#1-introducao-e-fundamentos)
2. [Conceitos do Dominio](#2-conceitos-do-dominio)
3. [Routine](#3-routine)
4. [Habit](#4-habit)
5. [HabitInstance](#5-habitinstance)
6. [Skip](#6-skip)
7. [Streak](#7-streak)
8. [Task](#8-task)
9. [Timer](#9-timer)
10. [Event Reordering](#10-event-reordering)
11. [Validacoes Globais](#11-validacoes-globais)

---

## 1. Introducao e Fundamentos

### 1.1. O Que Sao Regras de Negocio?

Regras de negocio sao politicas, restricoes e logicas que definem comportamento do sistema:

- **O que e permitido:** Operacoes validas
- **O que e obrigatorio:** Campos e operacoes mandatorios
- **Como o sistema reage:** Comportamento automatico
- **O que e calculado:** Derivacoes automaticas
- **Como conflitos sao resolvidos:** Logica de resolucao

### 1.2. Hierarquia de Regras

**Nivel 1 - Estruturais (Sempre Aplicadas):**

- Garantem integridade estrutural
- Viola-las torna sistema inconsistente
- Ex: "Todo HabitInstance deve ter um Habit pai"

**Nivel 2 - Dominio (Operacoes Normais):**

- Implementam logica de time blocking
- Podem ser sobrescritas com justificativa
- Ex: "Eventos nao devem conflitar"

**Nivel 3 - Preferencia (Sugestoes):**

- Guiam comportamento padrao
- Facilmente ignoradas
- Ex: "Sugerir cor padrao baseada em categoria"

### 1.3. Principios Fundamentais

**Adaptabilidade:** Sistema se adapta a realidade do usuario. Quando algo atrasa, informa e permite reorganizacao.

**Preservacao de Intencao:** Mudancas manuais preservam intencao original. Se planejou 30min de meditacao, duracao e mantida mesmo que horario mude.

**Transparencia:** Toda mudanca e explicavel e reversivel. Usuario sempre tem controle final.

**Simplicidade Progressiva:** Funcionalidade basica simples, sofisticacao quando necessario.

**Controle do Usuario:** Sistema NUNCA altera agenda automaticamente. Apenas detecta, informa e sugere.

---

## 2. Conceitos do Dominio

### 2.1. Entidades Principais

| Entidade          | Descricao                                              |
| ----------------- | ------------------------------------------------------ |
| **Routine**       | Template semanal que agrupa habitos relacionados       |
| **Habit**         | Evento recorrente, template do "ideal"                 |
| **HabitInstance** | Ocorrencia real em data especifica, o "real"           |
| **Task**          | Evento pontual nao-recorrente (checkbox com data/hora) |
| **Timer**         | Rastreador de tempo ativo                              |
| **TimeLog**       | Registro de tempo efetivamente gasto                   |
| **Tag**           | Categoria para organizar habits e tasks                |

### 2.2. Diagrama Conceitual

```
Routine (Morning Routine)
├── Habit (Meditation 7:00-7:30 Daily)
│   ├── HabitInstance (21/10 - DONE)
│   │   └── TimeLog (7:15-7:40)
│   └── HabitInstance (22/10 - PENDING)
│
└── Habit (Workout 7:30-8:30 Weekdays)
    ├── HabitInstance (21/10 - DONE)
    │   └── TimeLog (8:00-9:00)
    └── HabitInstance (22/10 - PENDING)

Task (Dentista 14:30 - independente de routine)
```

### 2.3. Glossario

| Termo                | Definicao                                               |
| -------------------- | ------------------------------------------------------- |
| **Conflito**         | Dois eventos ocupam mesmo intervalo de tempo            |
| **Event Reordering** | Processo de reorganizar eventos quando um atrasa        |
| **Streak**           | Dias consecutivos com habito DONE                       |
| **Skip**             | Pular habito conscientemente (com ou sem justificativa) |
| **Substatus**        | Qualificacao adicional de DONE ou NOT_DONE              |
| **Completion %**     | Percentual de tempo realizado vs planejado              |

---

## 3. Routine

### BR-ROUTINE-001: Single Active Constraint

**Descricao:** Apenas UMA rotina pode estar ativa por vez. Ativar uma rotina desativa automaticamente todas as outras.

**Regras:**

1. Campo `is_active` e booleano (nao NULL)
2. Apenas 1 rotina com `is_active = True` por vez
3. Ativar rotina A desativa automaticamente rotina B
4. Criar rotina NAO ativa automaticamente (requer `activate()`)
5. Primeira rotina criada e ativada automaticamente
6. Deletar rotina ativa nao deixa nenhuma ativa

**Implementacao:**

```python
def activate_routine(routine_id: int, session: Session) -> Routine:
    # 1. Desativar TODAS as rotinas
    session.query(Routine).update({"is_active": False})

    # 2. Ativar apenas a escolhida
    routine = session.get(Routine, routine_id)
    routine.is_active = True
    session.commit()
    return routine
```

**CLI:**

```bash
$ routine activate "Rotina Trabalho"
[INFO] Rotina "Rotina Matinal" desativada
[OK] Rotina "Rotina Trabalho" ativada
```

**Testes:**

- `test_br_routine_001_only_one_active`
- `test_br_routine_001_activate_deactivates_others`
- `test_br_routine_001_create_not_auto_active`
- `test_br_routine_001_first_routine_auto_active`

---

### BR-ROUTINE-002: Habit Belongs to Routine

**Descricao:** Todo Habit DEVE pertencer a exatamente UMA rotina. Campo `routine_id` e obrigatorio (NOT NULL).

**Modelo:**

```python
class Habit(SQLModel, table=True):
    routine_id: int = Field(
        foreign_key="routines.id",
        ondelete="RESTRICT"  # Bloqueia delete com habits
    )
```

**Relacionamento:**

```
Routine (1) ----< Habits (N)
```

**Regras:**

1. `routine_id` obrigatorio (NOT NULL)
2. Foreign key valida (rotina deve existir)
3. Habit nao pode existir sem rotina
4. Deletar rotina com habits e bloqueado (RESTRICT)

**Testes:**

- `test_br_routine_002_habit_requires_routine`
- `test_br_routine_002_foreign_key_valid`
- `test_br_routine_002_delete_routine_with_habits_blocked`

---

### BR-ROUTINE-003: Task Independent of Routine

**Descricao:** Task NAO pertence a rotina. E entidade independente.

**Regras:**

1. Task NAO possui campo `routine_id`
2. Task visivel independente de rotina ativa
3. `task list` mostra todas tasks (nao filtra por rotina)
4. Deletar rotina NAO afeta tasks

**Justificativa:** Tasks sao eventos pontuais que nao fazem parte de rotinas recorrentes.

**Testes:**

- `test_br_routine_003_task_no_routine_field`
- `test_br_routine_003_task_list_independent`
- `test_br_routine_003_delete_routine_keeps_tasks`

---

### BR-ROUTINE-004: Activation Cascade

**Descricao:** Ativar rotina define contexto padrao para comandos `habit`.

**Regras:**

1. `habit list` mostra apenas habits da rotina ativa
2. `habit create` cria na rotina ativa por default
3. Erro claro se nenhuma rotina ativa
4. Flag `--all` permite ver habits de todas rotinas

**First Routine Flow:**

```bash
$ habit create --title "Academia"
[ERROR] Nenhuma rotina existe

Deseja criar uma rotina agora? (S/n): s
Nome da rotina: Rotina Matinal
[OK] Rotina "Rotina Matinal" criada e ativada

Continuar criando habito "Academia"? (S/n): s
[OK] Habito "Academia" criado na rotina "Rotina Matinal"
```

**Comandos Afetados por Contexto:**

```bash
habit list         # Lista apenas da rotina ativa
habit create       # Cria na rotina ativa
habit list --all   # Lista de TODAS rotinas
```

**Comandos Independentes:**

```bash
routine list       # Mostra TODAS rotinas
task list          # Mostra TODAS tasks
```

**Testes:**

- `test_br_routine_004_habit_list_active_context`
- `test_br_routine_004_habit_create_active_context`
- `test_br_routine_004_error_no_active_routine`
- `test_br_routine_004_all_flag`
- `test_br_routine_004_first_routine_flow`

---

### BR-ROUTINE-005: Validacao de Nome

**Descricao:** Nome da rotina deve atender requisitos de validacao.

**Regras:**

1. Nome nao pode ser vazio (apos trim)
2. Nome deve ter 1-200 caracteres
3. Nome deve ser unico (case-insensitive)

**Validacao:**

```python
name = name.strip()
if not name:
    raise ValueError("Nome da rotina nao pode ser vazio")
if len(name) > 200:
    raise ValueError("Nome nao pode ter mais de 200 caracteres")
```

**Testes:**

- `test_br_routine_005_empty_name_error`
- `test_br_routine_005_max_length`
- `test_br_routine_005_unique_name`

---

### BR-ROUTINE-006: Soft Delete e Purge

**Descricao:** Rotinas podem ser desativadas (soft delete) ou removidas permanentemente (purge).

**Soft Delete (padrao):**

```bash
$ routine delete 1
[WARN] Desativar rotina "Rotina Matinal"?
       - 8 habitos permanecem vinculados
       - Rotina pode ser reativada depois
Confirmar? (s/N): s
[OK] Rotina "Rotina Matinal" desativada
```

**Hard Delete (--purge):**

```bash
# Sem habits - funciona
$ routine delete 1 --purge
[OK] Rotina deletada permanentemente

# Com habits - bloqueado
$ routine delete 1 --purge
[ERROR] Nao e possivel deletar rotina com habitos
```

**Testes:**

- `test_br_routine_006_soft_delete_default`
- `test_br_routine_006_purge_empty_routine`
- `test_br_routine_006_purge_with_habits_blocked`

---

## 4. Habit

### BR-HABIT-001: Estrutura de Habito

**Descricao:** Habit e template de evento recorrente vinculado a Routine.

**Campos:**

```python
class Habit(SQLModel, table=True):
    id: int | None
    routine_id: int                    # FK obrigatorio
    title: str                         # 1-200 chars
    scheduled_start: time              # Horario inicio
    scheduled_end: time                # Horario fim
    recurrence: Recurrence             # Padrao recorrencia
    color: str | None                  # Cor hexadecimal
    tag_id: int | None                 # FK opcional para Tag
```

**Validacoes:**

- Title vazio apos trim → ValueError
- Title > 200 chars → ValueError
- start >= end → ValueError

**Testes:**

- `test_br_habit_001_title_required`
- `test_br_habit_001_title_max_length`
- `test_br_habit_001_start_before_end`

---

### BR-HABIT-002: Padroes de Recorrencia

**Descricao:** Habit define quando se repete usando enum Recurrence.

**Enum Recurrence:**

```python
class Recurrence(Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    WEEKDAYS = "WEEKDAYS"      # Seg-Sex
    WEEKENDS = "WEEKENDS"      # Sab-Dom
    EVERYDAY = "EVERYDAY"      # Todos os dias
```

**Exemplos:**

```bash
habit create --title "Academia" --repeat WEEKDAYS
habit create --title "Meditacao" --repeat EVERYDAY
habit create --title "Revisao" --repeat FRIDAY
```

**Testes:**

- `test_br_habit_002_recurrence_weekdays`
- `test_br_habit_002_recurrence_everyday`
- `test_br_habit_002_invalid_recurrence`

---

### BR-HABIT-003: Geracao de Instancias

**Descricao:** Sistema gera HabitInstances durante criacao do habito com `--generate N`.

**Comando:**

```bash
habit create --title "Academia" --start 07:00 --end 08:30 \
  --repeat WEEKDAYS --generate 3
```

**Parametros:**

- `--generate N`: Gerar instancias para proximos N meses
- Se omitido: nao gera instancias automaticamente

**Comportamento:**

- Data inicio: hoje (`date.today()`)
- Data fim: hoje + N meses (`relativedelta`)
- Respeita padrao de recorrencia
- Nao duplica instancias existentes

**Validacoes:**

- N deve ser inteiro positivo
- Recomendado: 1-12 meses

**Testes:**

- `test_br_habit_003_generate_on_create`
- `test_br_habit_003_generate_respects_recurrence`
- `test_br_habit_003_no_duplicate_instances`
- `test_br_habit_003_create_without_generate`

---

### BR-HABIT-004: Modificacao de Habito

**Descricao:** Modificar Habit afeta apenas instancias futuras (PENDING).

**Comando:**

```bash
habit update ID --start 08:00 --end 09:30
```

**Comportamento:**

1. Usuario modifica Habit (ex: muda horario)
2. Sistema identifica instancias PENDING com date >= hoje
3. Atualiza essas instancias
4. Instancias DONE/NOT_DONE nao mudam

**Testes:**

- `test_br_habit_004_update_affects_future_only`
- `test_br_habit_004_preserves_completed`

---

### BR-HABIT-005: Delecao de Habito

**Descricao:** Deletar Habit deleta instancias futuras mas preserva historico.

**Comportamento:**

1. Instancias PENDING sao deletadas
2. Instancias DONE/NOT_DONE sao preservadas (para reports)
3. Habit e removido

**Cascade:**

```python
instances: list[HabitInstance] = Relationship(
    back_populates="habit",
    cascade_delete=True  # Deleta instancias automaticamente
)
```

**Testes:**

- `test_br_habit_005_delete_removes_future`
- `test_br_habit_005_preserves_history`

---

## 5. HabitInstance

### BR-HABITINSTANCE-001: Status Principal

**Descricao:** HabitInstance possui 3 status principais.

**Enum Status:**

```python
class Status(str, Enum):
    PENDING = "pending"      # Agendado, nao iniciado
    DONE = "done"            # Realizado
    NOT_DONE = "not_done"    # Nao realizado
```

**Transicoes:**

```plaintext
PENDING
  ├─> DONE (via timer stop ou log manual)
  └─> NOT_DONE (via skip ou timeout)

DONE → [FINAL]
NOT_DONE → [FINAL]
```

**Testes:**

- `test_br_habitinstance_001_valid_status`
- `test_br_habitinstance_001_transitions`

---

### BR-HABITINSTANCE-002: Substatus Obrigatorio

**Descricao:** Status finais requerem substatus correspondente.

**DoneSubstatus (quando DONE):**

```python
class DoneSubstatus(str, Enum):
    FULL = "full"            # 90-110% da meta
    PARTIAL = "partial"      # <90% da meta
    OVERDONE = "overdone"    # 110-150% da meta
    EXCESSIVE = "excessive"  # >150% da meta
```

**NotDoneSubstatus (quando NOT_DONE):**

```python
class NotDoneSubstatus(str, Enum):
    SKIPPED_JUSTIFIED = "skipped_justified"
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"
    IGNORED = "ignored"      # Timeout sem acao
```

**Regras de Consistencia:**

1. DONE requer done_substatus preenchido
2. NOT_DONE requer not_done_substatus preenchido
3. PENDING nao pode ter substatus
4. Substatus sao mutuamente exclusivos

**Validacao:**

```python
def validate_status_consistency(self) -> None:
    if self.status == Status.DONE:
        if self.done_substatus is None:
            raise ValueError("done_substatus obrigatorio quando status=DONE")
        if self.not_done_substatus is not None:
            raise ValueError("not_done_substatus deve ser None quando status=DONE")
    # ... similar para NOT_DONE e PENDING
```

**Testes:**

- `test_br_habitinstance_002_done_requires_substatus`
- `test_br_habitinstance_002_not_done_requires_substatus`
- `test_br_habitinstance_002_pending_no_substatus`
- `test_br_habitinstance_002_mutually_exclusive`

---

### BR-HABITINSTANCE-003: Completion Thresholds

**Descricao:** DoneSubstatus e calculado baseado em completion percentage.

**Thresholds:**

| Completion | Substatus | Feedback                |
| ---------- | --------- | ----------------------- |
| > 150%     | EXCESSIVE | [WARN] Ultrapassou meta |
| 110-150%   | OVERDONE  | [INFO] Acima da meta    |
| 90-110%    | FULL      | [OK] Perfeito           |
| < 90%      | PARTIAL   | Abaixo da meta          |

**Formula:**

```python
completion = (actual_duration / expected_duration) * 100
```

**Testes:**

- `test_br_habitinstance_003_threshold_full`
- `test_br_habitinstance_003_threshold_partial`
- `test_br_habitinstance_003_threshold_overdone`
- `test_br_habitinstance_003_threshold_excessive`

---

### BR-HABITINSTANCE-004: Timeout Automatico

**Descricao:** Instancia PENDING sem acao apos prazo e marcada como IGNORED.

**Regra:**

- Instancia PENDING > 48h apos scheduled_start
- Automaticamente: NOT_DONE + IGNORED

**Property:**

```python
@property
def is_overdue(self) -> bool:
    if self.status != Status.PENDING:
        return False
    now = datetime.now()
    scheduled = datetime.combine(self.date, self.scheduled_start)
    return now > scheduled
```

**Nota:** Timeout automatico esta documentado mas ainda nao implementado no MVP. Property `is_overdue` apenas verifica atraso.

**Testes:**

- `test_br_habitinstance_004_is_overdue_pending`
- `test_br_habitinstance_004_not_overdue_done`

---

### BR-HABITINSTANCE-005: Edicao de Instancia

**Descricao:** Usuario pode editar horario de uma HabitInstance especifica.

**Comando:**

```bash
habit edit INSTANCE_ID --start 08:00 --end 09:30
```

**Comportamento:**

- Novo horario aplicado apenas aquela instancia
- Outras instancias mantem horario do template
- Nao afeta Habit (template)

**Testes:**

- `test_br_habitinstance_005_edit_single`
- `test_br_habitinstance_005_preserves_template`

---

## 6. Skip

### BR-SKIP-001: Categorizacao de Skip

**Descricao:** Skip de habit deve ser categorizado usando enum SkipReason.

**Enum SkipReason:**

```python
class SkipReason(str, Enum):
    HEALTH = "saude"              # Saude (doenca, consulta)
    WORK = "trabalho"             # Trabalho (reuniao, deadline)
    FAMILY = "familia"            # Familia (evento, emergencia)
    TRAVEL = "viagem"             # Viagem/Deslocamento
    WEATHER = "clima"             # Clima (chuva, frio)
    LACK_RESOURCES = "falta_recursos"  # Falta de recursos
    EMERGENCY = "emergencia"      # Emergencias
    OTHER = "outro"               # Outros
```

**Comando:**

```bash
habit skip INSTANCE_ID --reason HEALTH --note "Consulta medica"
```

**Testes:**

- `test_br_skip_001_valid_reasons`
- `test_br_skip_001_with_note`

---

### BR-SKIP-002: Campos de Skip

**Descricao:** HabitInstance possui campos para rastrear skip.

**Campos:**

```python
skip_reason: SkipReason | None    # Categoria (obrigatorio se justified)
skip_note: str | None             # Nota opcional (max 500 chars)
```

**Regras:**

1. SKIPPED_JUSTIFIED requer skip_reason
2. SKIPPED_UNJUSTIFIED nao tem skip_reason
3. skip_note e sempre opcional

**Validacao:**

```python
if self.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED:
    if self.skip_reason is None:
        raise ValueError("skip_reason obrigatorio para SKIPPED_JUSTIFIED")
else:
    if self.skip_reason is not None:
        raise ValueError("skip_reason so permitido com SKIPPED_JUSTIFIED")
```

**Testes:**

- `test_br_skip_002_justified_requires_reason`
- `test_br_skip_002_unjustified_no_reason`
- `test_br_skip_002_note_optional`

---

### BR-SKIP-003: Prazo para Justificar

**Descricao:** Usuario tem 48h apos horario planejado para justificar skip.

**Comportamento:**

- Dentro de 48h: pode adicionar/editar justificativa
- Apos 48h: instancia marcada como IGNORED automaticamente
- IGNORED nao pode receber justificativa retroativa

**Nota:** Timeout automatico documentado, implementacao pendente.

**Testes:**

- `test_br_skip_003_within_deadline`
- `test_br_skip_003_after_deadline_ignored`

---

### BR-SKIP-004: CLI Prompt Interativo

**Descricao:** Ao dar skip, CLI oferece prompt interativo para categorizar.

**Fluxo:**

```bash
$ habit skip 42

Por que voce esta pulando Academia hoje?

[1] Saude
[2] Trabalho
[3] Familia
[4] Viagem
[5] Clima
[6] Falta de recursos
[7] Emergencia
[8] Outro
[9] Sem justificativa

Escolha [1-9]: _
```

**Comportamento:**

- Opcoes 1-8: SKIPPED_JUSTIFIED + skip_reason
- Opcao 9: SKIPPED_UNJUSTIFIED + skip_reason=None

**Testes:**

- `test_br_skip_004_interactive_justified`
- `test_br_skip_004_interactive_unjustified`

---

## 7. Streak

### BR-STREAK-001: Algoritmo de Calculo

**Descricao:** Streak conta dias consecutivos com `status = DONE`, do mais recente para tras.

**Algoritmo:**

```python
def calculate_streak(habit_id: int) -> int:
    instances = get_instances_by_date(habit_id)  # Ordem cronologica
    streak = 0

    for instance in reversed(instances):  # Mais recente primeiro
        if instance.status == Status.DONE:
            streak += 1
        elif instance.status == Status.NOT_DONE:
            break  # Para no primeiro NOT_DONE
        # PENDING nao conta nem quebra

    return streak
```

**Regras:**

1. Direcao: presente → passado
2. Conta: apenas DONE (qualquer substatus)
3. Para: no primeiro NOT_DONE
4. Ignora: PENDING (futuro)

**Testes:**

- `test_br_streak_001_counts_done`
- `test_br_streak_001_stops_at_not_done`
- `test_br_streak_001_ignores_pending`

---

### BR-STREAK-002: Condicoes de Quebra

**Descricao:** Streak SEMPRE quebra quando `status = NOT_DONE`, independente do substatus.

**Todos quebram:**

| Substatus           | Quebra? | Impacto Psicologico |
| ------------------- | ------- | ------------------- |
| SKIPPED_JUSTIFIED   | Sim     | Baixo               |
| SKIPPED_UNJUSTIFIED | Sim     | Medio               |
| IGNORED             | Sim     | Alto                |

**Filosofia (Atomic Habits - James Clear):**

- Consistencia > Perfeicao
- "Nunca pule dois dias seguidos"
- Skip consciente ainda e quebra
- Diferenciamos impacto psicologico, nao o fato da quebra

**Testes:**

- `test_br_streak_002_breaks_on_skipped_justified`
- `test_br_streak_002_breaks_on_skipped_unjustified`
- `test_br_streak_002_breaks_on_ignored`

---

### BR-STREAK-003: Condicoes de Manutencao

**Descricao:** Streak SEMPRE mantem quando `status = DONE`, independente do substatus.

**Todos mantem:**

| Substatus | Mantem? | Feedback      |
| --------- | ------- | ------------- |
| FULL      | Sim     | [OK] Perfeito |
| PARTIAL   | Sim     | Encorajador   |
| OVERDONE  | Sim     | Info          |
| EXCESSIVE | Sim     | Warning       |

**Filosofia:** "Melhor feito que perfeito"

**Testes:**

- `test_br_streak_003_maintains_on_full`
- `test_br_streak_003_maintains_on_partial`
- `test_br_streak_003_maintains_on_overdone`

---

### BR-STREAK-004: Dias Sem Instancia

**Descricao:** Dias sem instancia nao quebram streak.

**Exemplo:**

- Habit e WEEKDAYS (seg-sex)
- Hoje e sabado (sem instancia)
- Streak continua valido

**Regra:** Apenas instancias NOT_DONE quebram streak. Ausencia de instancia e neutra.

**Testes:**

- `test_br_streak_004_weekend_no_break`
- `test_br_streak_004_gap_no_break`

---

## 8. Task

### BR-TASK-001: Estrutura de Task

**Descricao:** Task e evento pontual nao-recorrente. Funciona como checkbox com data/hora.

**Campos:**

```python
class Task(SQLModel, table=True):
    id: int | None
    title: str                         # 1-200 chars
    scheduled_datetime: datetime       # Quando executar
    completed_datetime: datetime | None  # Quando foi concluido
    description: str | None            # Texto opcional
    color: str | None                  # Cor hexadecimal
    tag_id: int | None                 # FK opcional para Tag
```

**Caracteristicas:**

- NAO tem status enum (usa completed_datetime)
- NAO tem priority
- NAO tem timer
- NAO tem deadline separado
- NAO pertence a routine

**Testes:**

- `test_br_task_001_create_basic`
- `test_br_task_001_title_required`

---

### BR-TASK-002: Conclusao de Task

**Descricao:** Task e marcada como concluida via `completed_datetime`.

**Estados:**

- `completed_datetime = None` → Pendente
- `completed_datetime = datetime` → Concluida

**Comando:**

```bash
$ task complete 42
[OK] Task "Dentista" marcada como concluida
```

**Comportamento:**

- Sistema registra timestamp atual
- Task sai da lista de pendentes
- Aparece em historico

**Testes:**

- `test_br_task_002_complete_sets_datetime`
- `test_br_task_002_pending_no_datetime`

---

### BR-TASK-003: Independencia de Routine

**Descricao:** Tasks sao independentes de routines.

**Regras:**

1. Task nao tem campo routine_id
2. `task list` mostra todas tasks
3. Mudar rotina ativa nao afeta tasks
4. Deletar rotina nao afeta tasks

**Testes:**

- `test_br_task_003_no_routine_field`
- `test_br_task_003_list_all_tasks`
- `test_br_task_003_routine_change_no_effect`

---

### BR-TASK-004: Visualizacao e Listagem

**Descricao:** Tasks podem ser listadas com filtros.

**Filtros:**

- Por status (pendentes, concluidas)
- Por data (hoje, semana, mes)
- Por tag

**Ordenacao:** Cronologica por scheduled_datetime

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

### BR-TASK-005: Atualizacao de Task

**Descricao:** Task pendente pode ser atualizada.

**Campos Atualizaveis:**

- title
- description
- scheduled_datetime
- color
- tag_id

**Restricao:** Task concluida nao pode ser editada.

**Testes:**

- `test_br_task_005_update_pending`
- `test_br_task_005_update_completed_error`

---

### BR-TASK-006: Simplicidade Mantida

**Descricao:** Tasks sao intencionalmente simples no MVP.

**NAO implementado:**

- Timer tracking
- Subtasks
- Dependencias entre tasks
- Priorizacao explicita
- Checklist interno

**Justificativa:** Foco do TimeBlock esta em habitos e rotinas. Tasks sao complemento para atividades pontuais.

---

## 9. Timer

### BR-TIMER-001: Single Active Timer

**Descricao:** Apenas UM timer pode estar ATIVO (RUNNING ou PAUSED) por vez.

**Constraint:**

```python
active_timers = get_active_timers()  # status in [RUNNING, PAUSED]
assert len(active_timers) <= 1
```

**Comportamento:**

- Timer finalizado nao bloqueia novo start
- Multiplas sessoes permitidas (start → stop → start)

**Erro:**

```bash
$ timer start Academia
[OK] Timer iniciado: Academia (00:00 / 01:30)

$ timer start Meditacao
[ERROR] Timer ja ativo: Academia (15min decorridos)

Opcoes:
  [1] Pausar Academia e iniciar Meditacao
  [2] Cancelar Academia (reset) e iniciar Meditacao
  [3] Continuar com Academia
```

**Testes:**

- `test_br_timer_001_only_one_active`
- `test_br_timer_001_error_if_already_running`
- `test_br_timer_001_stopped_not_blocking`

---

### BR-TIMER-002: Estados e Transicoes

**Descricao:** Timer possui estados RUNNING e PAUSED.

**Maquina de Estados:**

```
[NO TIMER]
  │
  └─> start → RUNNING
              ├─> pause → PAUSED
              │            └─> resume → RUNNING
              ├─> stop → [SALVA] → [NO TIMER]
              └─> reset → [CANCELA] → [NO TIMER]
```

**Comandos:**

| Comando | De             | Para     | Efeito             |
| ------- | -------------- | -------- | ------------------ |
| start   | NO TIMER       | RUNNING  | Cria timer         |
| pause   | RUNNING        | PAUSED   | Pausa contagem     |
| resume  | PAUSED         | RUNNING  | Retoma contagem    |
| stop    | RUNNING/PAUSED | NO TIMER | Salva e marca DONE |
| reset   | RUNNING/PAUSED | NO TIMER | Cancela sem salvar |

**Testes:**

- `test_br_timer_002_start_creates_running`
- `test_br_timer_002_pause_from_running`
- `test_br_timer_002_resume_from_paused`
- `test_br_timer_002_stop_saves`
- `test_br_timer_002_reset_cancels`

---

### BR-TIMER-003: Stop vs Reset

**Descricao:** `stop` e `reset` finalizam timer com comportamentos diferentes.

**stop:**

- Fecha sessao atual e SALVA no banco
- Marca instance como DONE
- Calcula completion percentage
- Permite start novamente (nova sessao)

**reset:**

- Cancela timer atual SEM salvar
- Instance continua PENDING
- Usado quando iniciou habit errado

**Testes:**

- `test_br_timer_003_stop_saves_session`
- `test_br_timer_003_reset_no_save`
- `test_br_timer_003_reset_keeps_pending`

---

### BR-TIMER-004: Multiplas Sessoes

**Descricao:** Usuario pode fazer multiplas sessoes do mesmo habit no mesmo dia.

**Workflow:**

```python
# Sessao 1 (manha)
timer1 = start_timer(instance_id=42)
timer1.stop()  # SALVA (60min)

# Sessao 2 (tarde)
timer2 = start_timer(instance_id=42)
timer2.stop()  # SALVA (30min)

# Total: 90min (acumulado)
```

**Substatus:** Calculado sobre tempo acumulado de todas sessoes.

**Testes:**

- `test_br_timer_004_multiple_sessions`
- `test_br_timer_004_accumulates_duration`

---

### BR-TIMER-005: Calculo de Completion

**Descricao:** Completion percentage calculado ao parar timer.

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

**Descricao:** Sistema rastreia pausas via campo acumulado `paused_duration`.

**Fluxo:**

```
10:00 - start_timer()
10:30 - pause_timer()
10:45 - resume_timer()  # paused_duration = 15min
11:00 - stop_timer()    # duration = 60min - 15min = 45min
```

**Calculo:**

```python
effective_duration = total_duration - paused_duration
```

**Testes:**

- `test_br_timer_006_pause_tracking`
- `test_br_timer_006_multiple_pauses`
- `test_br_timer_006_effective_duration`

---

### BR-TIMER-007: Log Manual

**Descricao:** Usuario pode registrar tempo manualmente sem usar timer.

**Comando:**

```bash
habit log INSTANCE_ID --start 07:00 --end 08:30
# ou
habit log INSTANCE_ID --duration 90
```

**Validacoes:**

- start < end
- duration > 0

**Testes:**

- `test_br_timer_007_manual_log_times`
- `test_br_timer_007_manual_log_duration`
- `test_br_timer_007_validates_times`

---

## 10. Event Reordering

### BR-REORDER-001: Definicao de Conflito

**Descricao:** Conflito ocorre quando dois eventos tem sobreposicao temporal no mesmo dia.

**Deteccao:**

```
Evento A: [T1, T2]
Evento B: [T3, T4]
Conflito se: (T1 < T4) AND (T3 < T2)
```

**Eventos Monitorados:**

- HabitInstances
- Tasks

**Testes:**

- `test_br_reorder_001_detects_overlap`
- `test_br_reorder_001_no_conflict_adjacent`

---

### BR-REORDER-002: Escopo Temporal

**Descricao:** Deteccao de conflitos ocorre dentro do mesmo dia (00:00-23:59).

**Regra:** Eventos de dias diferentes NAO podem conflitar, mesmo que horarios se sobreponham numericamente.

**Testes:**

- `test_br_reorder_002_same_day_only`
- `test_br_reorder_002_different_days_no_conflict`

---

### BR-REORDER-003: Apresentacao de Conflitos

**Descricao:** Sistema apresenta conflitos de forma clara ao usuario.

**Quando Apresentar:**

1. Apos criar/ajustar evento que resulta em conflito
2. Quando usuario solicita visualizacao de conflitos
3. Antes de iniciar timer, se houver conflitos

**Formato:**

```
Conflito detectado:
  - Academia: 07:00-08:00
  - Reuniao: 07:30-08:30
  Sobreposicao: 30 minutos
```

**Testes:**

- `test_br_reorder_003_presents_conflicts`
- `test_br_reorder_003_shows_overlap_duration`

---

### BR-REORDER-004: Conflitos Nao Bloqueiam

**Descricao:** Conflitos sao informativos, NAO impeditivos.

**Comportamento:**

- Timer start com conflito: apenas avisa, pergunta confirmacao
- Criar evento com conflito: apenas avisa, permite criar

```bash
$ timer start Academia
[WARN] Conflito detectado:
  - Academia: 07:00-08:00
  - Reuniao: 07:00-08:30

Iniciar timer mesmo assim? [Y/n]: y
[OK] Timer iniciado
```

**Testes:**

- `test_br_reorder_004_conflict_warning_only`
- `test_br_reorder_004_allows_with_confirmation`

---

### BR-REORDER-005: Persistencia de Conflitos

**Descricao:** Conflitos NAO sao persistidos no banco. Sao calculados dinamicamente.

**Justificativa:** Conflitos sao resultado de relacao temporal entre eventos. Como eventos podem mudar, conflitos devem ser recalculados.

**Testes:**

- `test_br_reorder_005_calculated_dynamically`
- `test_br_reorder_005_no_conflict_table`

---

### BR-REORDER-006: Algoritmo de Reordenamento

**Descricao:** Algoritmo de sugestao de reordenamento NAO esta no MVP.

**Status Atual:**

- Sistema detecta conflitos
- Sistema apresenta conflitos
- Sistema NAO sugere novos horarios automaticamente

**Futuro:** Algoritmo Simple Cascade planejado para v2.0.

---

## 11. Validacoes Globais

### BR-VAL-001: Validacao de Horarios

**Regras:**

- `start_time < end_time`
- `duration_minutes > 0`
- Horarios dentro do dia (00:00 - 23:59)

**Testes:**

- `test_br_val_001_start_before_end`
- `test_br_val_001_positive_duration`

---

### BR-VAL-002: Validacao de Datas

**Regras:**

- Data nao anterior a 2025-01-01
- Sem limite de data futura
- Formato ISO 8601

**Testes:**

- `test_br_val_002_min_date`
- `test_br_val_002_iso_format`

---

### BR-VAL-003: Validacao de Strings

| Campo       | Limite       |
| ----------- | ------------ |
| title       | 1-200 chars  |
| description | 0-2000 chars |
| name        | 1-200 chars  |
| note        | 0-500 chars  |

**Comportamento:** Trim de espacos antes da validacao.

**Testes:**

- `test_br_val_003_title_limits`
- `test_br_val_003_trim_whitespace`

---

## Referencias

- **ADRs:** `docs/decisions/`
- **Livro:** "Atomic Habits" - James Clear
- **Service Layer:** `cli/src/timeblock/services/`
- **Models:** `cli/src/timeblock/models/`
- **Enums:** `cli/src/timeblock/models/enums.py`

---

**Documento consolidado em:** 28 de Novembro de 2025
**Total de regras:** 45 BRs
**Este e o SSOT para regras de negocio**
