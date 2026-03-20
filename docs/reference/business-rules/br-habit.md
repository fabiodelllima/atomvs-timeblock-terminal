# Habit

O Habit é o template que materializa a identidade do usuário em blocos de tempo recorrentes. Onde a Routine define o agrupamento ("minha rotina matinal"), o Habit define a ação específica ("academia das 7h às 8h, dias úteis"). Na filosofia do Atomic Habits, hábitos baseados em identidade são mais duráveis do que hábitos baseados em objetivos. O usuário não "precisa se exercitar" — ele _é_ alguém que se exercita. O campo `title` deveria refletir isso: "Exercício" em vez de "Perder peso".

Cada Habit pertence obrigatoriamente a uma Routine e define três propriedades fundamentais: _o que_ (título), _quando se repete_ (recorrência — dias específicos, dias úteis, todos os dias) e _por quanto tempo_ (horário início/fim). A recorrência é o mecanismo que transforma intenção em sistema: não é necessário decidir diariamente se vai meditar, porque o sistema já posicionou o bloco no horário certo em todos os dias da semana. Essa previsibilidade reduz o custo cognitivo da decisão, que segundo James Clear é o principal inimigo da consistência.

O Habit funciona como _fábrica_ de HabitInstances. Ao criar um hábito com recorrência WEEKDAYS e solicitar geração de instâncias para 3 meses, o sistema produz automaticamente uma instância concreta para cada dia útil no período. Modificar o Habit afeta apenas instâncias futuras (PENDING) — as já executadas preservam o registro histórico fiel. Essa separação entre template e ocorrência é a base de toda a rastreabilidade do sistema.

### BR-HABIT-001: Estrutura de Habito

**Descrição:** Habit é template de evento recorrente vinculado a Routine.

**Campos:**

```python
class Habit(SQLModel, table=True):
    id: int | None
    routine_id: int                    # FK obrigatório
    title: str                         # 1-200 chars
    scheduled_start: time              # Horário inicio
    scheduled_end: time                # Horário fim
    recurrence: Recurrence             # Padrão recorrência
    color: str | None                  # Cor hexadecimal
    tag_id: int | None                 # FK opcional para Tag
```

**Validações:**

- Title vazio após trim → ValueError
- Title > 200 chars → ValueError
- start >= end → ValueError

**Testes:**

- `test_br_habit_001_title_required`
- `test_br_habit_001_title_max_length`
- `test_br_habit_001_start_before_end`

---

### BR-HABIT-002: Padrões de Recorrência

**Descrição:** Habit define quando se repete usando enum Recurrence.

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
habit create --title "Meditação" --repeat EVERYDAY
habit create --title "Revisão" --repeat FRIDAY
```

**Testes:**

- `test_br_habit_002_recurrence_weekdays`
- `test_br_habit_002_recurrence_everyday`
- `test_br_habit_002_invalid_recurrence`

---

### BR-HABIT-003: Geração de Instâncias

**Descrição:** Sistema gera HabitInstances durante criação do habito com `--generate N`.

**Comando:**

```bash
habit create --title "Academia" --start 07:00 --end 08:30 \
  --repeat WEEKDAYS --generate 3
```

**Parâmetros:**

- `--generate N`: Gerar instâncias para próximos N meses
- Se omitido: não gera instâncias automaticamente

**Comportamento:**

- Data inicio: hoje (`date.today()`)
- Data fim: hoje + N meses (`relativedelta`)
- Respeita padrão de recorrência
- Não duplica instâncias existentes

**Validações:**

- N deve ser inteiro positivo
- Recomendado: 1-12 meses

**Testes:**

- `test_br_habit_003_generate_on_create`
- `test_br_habit_003_generate_respects_recurrence`
- `test_br_habit_003_no_duplicate_instances`
- `test_br_habit_003_create_without_generate`

---

### BR-HABIT-004: Modificação de Habito

**Descrição:** Modificar Habit afeta apenas instâncias futuras (PENDING).

**Comando:**

```bash
habit update ID --start 08:00 --end 09:30
```

**Comportamento:**

1. Usuário modifica Habit (ex: muda horário)
2. Sistema identifica instâncias PENDING com date >= hoje
3. Atualiza essas instâncias
4. Instâncias DONE/NOT_DONE não mudam

**Testes:**

- `test_br_habit_004_update_affects_future_only`
- `test_br_habit_004_preserves_completed`

---

### BR-HABIT-005: Deleção de Habito

**Descrição:** Deletar Habit deleta instâncias futuras mas preserva histórico.

**Comportamento:**

1. Instâncias PENDING são deletadas
2. Instâncias DONE/NOT_DONE são preservadas (para reports)
3. Habit é removido

**Cascade:**

```python
instances: list[HabitInstance] = Relationship(
    back_populates="habit",
    cascade_delete=True  # Deleta instâncias automaticamente
)
```

**Testes:**

- `test_br_habit_005_delete_removes_future`
- `test_br_habit_005_preserves_history`
