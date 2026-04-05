# Routine

A Routine é a unidade organizacional de mais alto nível no TimeBlock Planner. Ela representa o plano ideal de uma semana — o desenho intencional de como o usuário quer distribuir seu tempo entre os hábitos que compõem sua identidade. No vocabulário do Atomic Habits, criar uma rotina é um ato de _environment design_: ao posicionar blocos de tempo fixos para exercício, estudo, trabalho profundo e descanso, o usuário está construindo o ambiente temporal onde bons hábitos se tornam o caminho de menor resistência.

Cada rotina agrupa um conjunto de hábitos recorrentes e define o contexto operacional do sistema. Apenas uma rotina pode estar ativa por vez, funcionando como um "modo" que determina quais hábitos aparecem na agenda diária e na TUI. Trocar de rotina é trocar de contexto de vida: a rotina de dias úteis cede lugar à rotina de férias, que por sua vez pode dar espaço a uma rotina de preparação para provas. Essa troca é sempre explícita e consciente — o sistema nunca altera a rotina ativa automaticamente.

É fundamental distinguir a Routine das instâncias que ela gera. A Routine é imutável no sentido conceitual: ela expressa a _intenção_ do usuário, o cenário ideal onde tudo acontece no horário planejado. A realidade do dia a dia se materializa nas HabitInstances, que podem ser ajustadas, adiadas ou puladas sem comprometer o plano original. Quando uma segunda-feira caótica obriga o usuário a reorganizar toda a manhã, suas instâncias mudam mas sua Routine permanece intacta — e na terça-feira, o sistema apresenta novamente o plano ideal como ponto de partida. Essa separação entre intenção e execução é o que permite ao sistema servir simultaneamente como planejador e como registro honesto da realidade.

### BR-ROUTINE-001: Single Active Constraint

**Descrição:** Apenas UMA rotina pode estar ativa por vez. Ativar uma rotina desativa automaticamente todas as outras.

**Regras:**

1. Campo `is_active` é booleano (não NULL)
2. Apenas 1 rotina com `is_active = True` por vez
3. Ativar rotina A desativa automaticamente rotina B
4. Criar rotina NÃO ativa automaticamente (requer `activate()`)
5. Primeira rotina criada e ativada automaticamente
6. Deletar rotina ativa não deixa nenhuma ativa

**Implementação:**

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

**Descrição:** Todo Habit DEVE pertencer a exatamente UMA rotina. Campo `routine_id` é obrigatório (NOT NULL).

**Modelo:**

```python
class Habit(SQLModel, table=True):
    routine_id: int = Field(
        foreign_key="routines.id",
        ondelete="RESTRICT"  # Bloqueia delete com habits
    )
```

**Relacionamento:**

```plaintext
Routine (1) ----< Habits (N)
```

**Regras:**

1. `routine_id` obrigatório (NOT NULL)
2. Foreign key válida (rotina deve existir)
3. Habit não pode existir sem rotina
4. Deletar rotina com habits é bloqueado (RESTRICT)

**Testes:**

- `test_br_routine_002_habit_requires_routine`
- `test_br_routine_002_foreign_key_valid`
- `test_br_routine_002_delete_routine_with_habits_blocked`

---

### BR-ROUTINE-003: Task Independent of Routine

**Descrição:** Task NÃO pertence a rotina. É entidade independente.

**Regras:**

1. Task NÃO possui campo `routine_id`
2. Task visível independente de rotina ativa
3. `task list` mostra todas tasks (não filtra por rotina)
4. Deletar rotina NÃO afeta tasks

**Justificativa:** Tasks são eventos pontuais que não fazem parte de rotinas recorrentes.

**Testes:**

- `test_br_routine_003_task_no_routine_field`
- `test_br_routine_003_task_list_independent`
- `test_br_routine_003_delete_routine_keeps_tasks`

---

### BR-ROUTINE-004: Activation Cascade

**Descrição:** Ativar rotina define contexto padrão para comandos `habit`.

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

### BR-ROUTINE-005: Validação de Nome

**Descrição:** Nome da rotina deve atender requisitos de validação.

**Regras:**

1. Nome não pode ser vazio (após trim)
2. Nome deve ter 1-200 caracteres
3. Nome deve ser único (case-insensitive)

**Validação:**

```python
name = name.strip()
if not name:
    raise ValueError("Nome da rotina não pode ser vazio")
if len(name) > 200:
    raise ValueError("Nome não pode ter mais de 200 caracteres")
```

**Testes:**

- `test_br_routine_005_empty_name_error`
- `test_br_routine_005_max_length`
- `test_br_routine_005_unique_name`

---

### BR-ROUTINE-006: Soft Delete e Purge

**Descrição:** Rotinas podem ser desativadas (soft delete) ou removidas permanentemente (purge).

**Soft Delete (padrão):**

```bash
$ routine delete 1
[WARN] Desativar rotina "Rotina Matinal"?
       - 8 hábitos permanecem vinculados
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
[ERROR] Não é possível deletar rotina com hábitos
```

**Testes:**

- `test_br_routine_006_soft_delete_default`
- `test_br_routine_006_purge_empty_routine`
- `test_br_routine_006_purge_with_habits_blocked`
