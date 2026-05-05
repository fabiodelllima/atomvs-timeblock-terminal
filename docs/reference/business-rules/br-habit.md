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

### BR-HABIT-005: Deleção de Habit (semântica de archive)

**Descrição:** A operação `delete_habit` arquiva o hábito sem destruir histórico. Para hard delete, ver `purge_habit` em BR-HABIT-006.

**Justificativa:** O ATOMVS é orientado a rastreabilidade longitudinal de hábitos. Streaks, completude histórica, tempo gasto e padrões de adesão dependem da preservação de `HabitInstance` e `TimeLog`. Hard delete destruiria silenciosamente exatamente os dados que sustentam o produto. Ver ADR-057 (Archive Lifecycle para Habit) para a decisão arquitetural completa, incluindo as alternativas consideradas e rejeitadas.

**Comportamento:**

1. `archived_at` é definido como `utcnow()` no registro do `Habit`
2. `HabitInstance` e `TimeLog` permanecem intactos no banco
3. Hábito não aparece em listagens padrão (dashboard, `habit list`, geração de instâncias)
4. Streaks calculados sobre `TimeLog` continuam corretos para o histórico até o arquivamento
5. Operação é reversível via `restore_habit`

**Sem cascade físico:**

```python
instances: list[HabitInstance] = Relationship(
    back_populates="habit",
    cascade_delete=True  # Mantido para suportar BR-HABIT-006 (purge), NÃO disparado em delete_habit
)
```

A flag `cascade_delete=True` é preservada para que `purge_habit` (BR-HABIT-006) tenha comportamento previsível, mas **não é acionada** pelo fluxo de `delete_habit` — este apenas marca `archived_at`.

**Testes:**

- `test_br_habit_005_delete_sets_archived_at`
- `test_br_habit_005_preserves_instances_after_archive`
- `test_br_habit_005_preserves_timelogs_after_archive`
- `test_br_habit_005_archived_excluded_from_default_listing`

**Referência cruzada:** BR-HABIT-006 detalha o ciclo completo de archive/purge/restore, incluindo as queries afetadas.

### BR-HABIT-006: Archive Lifecycle

**Descrição:** Habit suporta três operações de ciclo de vida explícitas: archive (soft delete, padrão), purge (hard delete administrativo) e restore (reverte archive). Modela alinhamento com BR-ROUTINE-006 e BR-TASK-009, eliminando a divergência histórica em que `Habit` era o único domínio do trio sem suporte a arquivamento.

**Schema:**

```python
class Habit(SQLModel, table=True):
    # ... campos existentes ...
    archived_at: datetime | None = Field(default=None)
```

Migration: `migration_004_habit_archive.py` adiciona coluna `archived_at TIMESTAMP DEFAULT NULL` na tabela `habits` via `ALTER TABLE ADD COLUMN`. Idempotente (verifica via `PRAGMA table_info`). Backfill: NULL para todos os existentes (todos ativos).

**Operações:**

| Operação       | Método                               | Comando CLI             | Affordance TUI                |
| -------------- | ------------------------------------ | ----------------------- | ----------------------------- |
| Archive (soft) | `delete_habit(id)`                   | `habit delete <id>`     | Dashboard tecla `d` (default) |
| Purge (hard)   | `purge_habit(id)`                    | `habit purge <id>`      | Não exposto na TUI            |
| Restore        | `restore_habit(id)`                  | `habit restore <id>`    | Não exposto na TUI            |
| Listar ativos  | `list_habits()`                      | `habit list`            | Default                       |
| Listar todos   | `list_habits(include_archived=True)` | `habit list --all`      | —                             |
| Listar arquiv. | `list_archived_habits()`             | `habit list --archived` | —                             |

**Comportamento de listagens:**

1. `list_habits()` filtra `archived_at IS NULL` (padrão de uso)
2. `get_habit(id)` **não** filtra — operações administrativas precisam acessar arquivados
3. `HabitInstanceService.generate_instances` recusa habit arquivado (retorna `[]`); call sites que iteram sobre coleções de habits filtram `archived_at IS NULL` antes de invocar
4. Dashboard loader (`tui/screens/dashboard/loader.py`) filtra `archived_at IS NULL` em todas as queries de exibição

**Comportamento de purge:**

```bash
$ habit purge 7
[WARN] Esta operação é irreversível. Será destruído:
       - Habit "Leitura matinal" (id=7)
       - 142 HabitInstance associadas
       - 89 TimeLog associados
Confirmar destruição? (digite "purge" para confirmar): purge
[OK] Habit, instances e time logs destruídos permanentemente.
```

A confirmação requer digitação literal da palavra "purge" (não apenas Y/N) para impedir disparos acidentais. O comando lista contagens reais antes de pedir confirmação.

**Comportamento de restore:**

```bash
$ habit restore 7
[OK] Habit "Leitura matinal" reativado. Próximas instâncias serão geradas no próximo ciclo de generate_instances.
```

`restore_habit` zera `archived_at` e o hábito volta às listagens. Instâncias futuras voltam a ser geradas no próximo ciclo. Instâncias passadas que existiam permanecem como estavam.

**Cenários BDD (em `tests/bdd/features/habit_archive.feature`):**

```gherkin
Feature: Habit Archive Lifecycle

  Scenario: Archive preserves history
    Given a habit with 30 days of TimeLog history
    When I delete the habit
    Then the habit is marked as archived
    And all 30 TimeLog entries remain intact
    And the streak calculation for the past period remains correct

  Scenario: Archived habit excluded from listing
    Given an archived habit
    When I list habits
    Then the archived habit is not shown
    When I list habits with --all flag
    Then the archived habit appears with archive timestamp

  Scenario: Purge requires explicit confirmation
    Given an archived habit with associated instances and timelogs
    When I run "habit purge" command
    Then I am prompted to type the word "purge" literally
    When I type "y" instead of "purge"
    Then the operation is aborted
    And no data is destroyed
```

**Testes (em `tests/unit/test_services/test_habit_service.py`):**

Classe `TestBRHabit006Archive`:

- `test_br_habit_006_delete_sets_archived_at`
- `test_br_habit_006_archive_preserves_instances`
- `test_br_habit_006_archive_preserves_timelogs`
- `test_br_habit_006_list_habits_excludes_archived_by_default`
- `test_br_habit_006_list_habits_include_archived_returns_all`
- `test_br_habit_006_get_habit_returns_archived`
- `test_br_habit_006_restore_clears_archived_at`
- `test_br_habit_006_purge_destroys_cascade`
- `test_br_habit_006_generate_instances_skips_archived`

**Referências:**

- ADR-057 (decisão arquitetural)
- BR-ROUTINE-006 (precedente para Routine)
- BR-TASK-009 (precedente para Task)
- Issue #61 (originalmente reportada como bug de cascade FK, reescopada para esta feature na Sessão 28)
