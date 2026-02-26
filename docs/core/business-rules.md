# Business Rules - TimeBlock Organizer

**Versão:** 3.0.0

**Data:** 28 de Novembro de 2025

**Status:** Consolidado (SSOT)

---

## Sumário

1. [Introdução e Fundamentos](#1-introdução-e-fundamentos)
2. [Conceitos do Domínio](#2-conceitos-do-domínio)
3. [Routine](#3-routine)
4. [Habit](#4-habit)
5. [HabitInstance](#5-habitinstance)
6. [Skip](#6-skip)
7. [Streak](#7-streak)
8. [Task](#8-task)
9. [Timer](#9-timer)
10. [Event Reordering](#10-event-reordering)
11. [Validações Globais](#11-validações-globais)
12. [CLI](#12-cli)
13. [Tag](#13-tag)
14. [TUI](#14-tui)

---

## 1. Introdução e Fundamentos

### 1.1. O Que São Regras de Negócio?

Regras de negócio são políticas, restrições e lógicas que definem comportamento do sistema:

- **O que é permitido:** Operações válidas
- **O que é obrigatório:** Campos e operações mandatórios
- **Como o sistema reage:** Comportamento automático
- **O que é calculado:** Derivações automáticas
- **Como conflitos são resolvidos:** Lógica de resolução

### 1.2. Hierarquia de Regras

**Nível 1 - Estruturais (Sempre Aplicadas):**

- Garantem integridade estrutural
- Viola-las torna sistema inconsistente
- Ex: "Todo HabitInstance deve ter um Habit pai"

**Nível 2 - Domínio (Operações Normais):**

- Implementam lógica de time blocking
- Podem ser sobrescritas com justificativa
- Ex: "Eventos não devem conflitar"

**Nível 3 - Preferência (Sugestões):**

- Guiam comportamento padrão
- Facilmente ignoradas
- Ex: "Sugerir cor padrão baseada em categoria"

### 1.3. Princípios Fundamentais

**Adaptabilidade:** Sistema se adapta a realidade do usuário. Quando algo atrasa, informa e permite reorganização.

**Preservação de Intenção:** Mudanças manuais preservam intenção original. Se planejou 30min de meditação, duração é mantida mesmo que horário mude.

**Transparência:** Toda mudança é explicável e reversível. Usuário sempre tem controle final.

**Simplicidade Progressiva:** Funcionalidade básica simples, sofisticação quando necessário.

**Controle do Usuário:** Sistema NUNCA altera agenda automaticamente. Apenas detecta, informa e sugere.

### 1.4. Filosofia: Atomic Habits

**Base teórica:** "Atomic Habits" de James Clear (2018)

#### O Que São Hábitos Atômicos

**Definição:** Uma prática ou rotina regular que é:

1. **Pequena** - Fácil de fazer
2. **Específica** - Claramente definida
3. **Parte de um sistema maior** - Compõe com outros hábitos

**A Matemática dos Hábitos:**

- Melhora de 1% ao dia: 1.01^365 = 37.78x melhor em um ano
- Piora de 1% ao dia: 0.99^365 = 0.03x (quase zero)

TimeBlock torna essa matemática visível e acionável.

**Por que "Atômico":**

- Átomo = Menor unidade que mantém propriedades do sistema
- HabitInstance = Menor unidade que mantém propriedades do hábito

#### As Quatro Leis

| Lei                   | Princípio       | Implementação TimeBlock       |
| --------------------- | --------------- | ----------------------------- |
| 1. Torne Óbvio        | Notar o hábito  | Agenda visual, horários fixos |
| 2. Torne Atraente     | Querer fazer    | Streaks, progresso visível    |
| 3. Torne Fácil        | Reduzir fricção | Recorrência automática        |
| 4. Torne Satisfatório | Recompensa      | Feedback imediato, relatórios |

#### Lei 1: Torne Óbvio (Cue)

**Princípio:** Você precisa notar o hábito antes de fazê-lo.

**Implementação:**

```
┌──────────────────────────────────┐
│  HOJE - 03 Nov 2025              │
├──────────────────────────────────┤
│ 07:00-08:00  Exercício Matinal   │ ← ÓBVIO
│ 09:00-10:00  Deep Work           │
│ 15:00-15:30  Leitura             │
└──────────────────────────────────┘
```

**Técnicas:**

- Agenda visual: Hábitos aparecem no seu dia
- Implementation Intention: "Quando for [HORA], eu vou [HÁBITO]"
- Rotina diária: Consistência cria pistas ambientais

#### Lei 2: Torne Atraente (Craving)

**Princípio:** Você precisa querer fazer o hábito.

**Implementação:**

**1. Progresso Visível:**

```
Exercício Matinal:
████████████████░░░░  15/20 dias este mês (75%)
```

**2. Streak Tracking:**

```
Sequência atual: 7 dias
Melhor sequência: 23 dias
```

Cada dia completado reforça a identidade: "Sou uma pessoa que se exercita".

#### Lei 3: Torne Fácil (Response)

**Princípio:** Reduza fricção para começar.

**Implementação:**

**1. Regra dos Dois Minutos:**

```python
habit = Habit(
    title="Escrever",
    scheduled_start=time(9, 0),
    scheduled_end=time(9, 2)  # Apenas 2 minutos!
)
```

**2. Recorrência Automática:**

```python
habit = Habit(
    title="Meditação",
    recurrence=Recurrence.EVERYDAY
)
# TimeBlock gera instâncias automaticamente
# Você só marca: feito ou não feito
```

**3. Event Reordering:**

Quando conflito surge, sistema detecta e informa:

```
CONFLITO DETECTADO:
┌─────────────────────────────────────┐
│ 09:00  Reunião inesperada (nova)    │
│ 09:00  Leitura (planejada)          │ ← Conflito!
└─────────────────────────────────────┘
```

Sistema remove fricção: você decide, não precisa repensar toda agenda.

#### Lei 4: Torne Satisfatório (Reward)

**Princípio:** Recompensa imediata reforça hábito.

**Implementação:**

**1. Gratificação Visual Instantânea:**

```
[ ] Exercício 7:00-8:00

 ↓ (ao completar)

[✓] Exercício 7:00-8:00  ← Dopamina!
```

**2. Relatórios de Progresso:**

```
SEMANA 1: ███████ 7/7 dias (100%)
SEMANA 2: ██████░ 6/7 dias (86%)
SEMANA 3: ███████ 7/7 dias (100%)
```

**3. Identity Reinforcement:**

Cada instância completada reforça: "Sou o tipo de pessoa que [FAZ ISSO]"

#### Arquitetura Conceitual

```
┌──────────────────────────────────────────────┐
│              ATOMIC HABITS                   │
│                                              │
│  Cue → Craving → Response → Reward           │
│   ↓       ↓         ↓         ↓              │
│  Óbvio  Atraente  Fácil   Satisfatório       │
└──────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────┐
│             TIMEBLOCK SYSTEM                 │
│                                              │
│  Habit → HabitInstance → Completion →        │
│           (scheduled)      (tracked)         │
│                ↓                             │
│        EventReordering                       │
│       (remove friction)                      │
└──────────────────────────────────────────────┘
```

#### Componentes e Princípios

**1. Habit (Template) - Identity-based habits:**

```python
class Habit:
    """Não é apenas uma tarefa, é quem você é."""
    title: str  # "Exercício" não "Preciso me exercitar"
    recurrence: Recurrence  # Sistema, não objetivo
    routine_id: int  # Parte de identidade maior
```

Identidade > Objetivos:

- "Exercício" → identidade: "Sou atleta"
- "Preciso me exercitar" → objetivo: "Quero estar em forma"

**2. HabitInstance (Átomo) - Smallest actionable unit:**

```python
class HabitInstance:
    """Um átomo: menor unidade do sistema."""
    date: date  # Hoje, específico
    scheduled_start: time  # Hora exata
    scheduled_end: time  # Duração definida
    status: Status  # Rastreável
```

Você não "cria um hábito" (abstrato), você "faz hoje às 7h" (concreto).

**3. TimeLog (Feedback) - Measurement = visibility = improvement:**

```python
class TimeLog:
    """Track para feedback."""
    start_time: datetime
    end_time: datetime
    habit_instance_id: int
```

"O que é medido é gerenciado"

#### Exemplo Prático: Construir Hábito de Leitura

**Objetivo:** Ler 30min/dia

**1. Torne Óbvio:**

```bash
timeblock habit create "Leitura" \
  --start 21:00 \
  --duration 30 \
  --recurrence EVERYDAY
```

Aparece na agenda todo dia, mesmo horário.

**2. Torne Atraente:**

- Lista de livros interessantes preparada
- Local confortável (sofá favorito)
- Chá quente como ritual

**3. Torne Fácil:**

- Apenas 30min (pequeno)
- Horário fixo (sem decisão)
- Livro já na mesinha (sem fricção)

**4. Torne Satisfatório:**

```bash
timeblock habit complete <instance_id>
```

Marca concluído, vê progresso visual.

**Resultado após 30 dias:**

```
Leitura Diária:
███████████████████████████░░░ 27/30 dias (90%)
Sequência atual: 12 dias
Livros completados: 2
```

#### Referências

- **Livro:** "Atomic Habits" - James Clear (2018), ISBN 978-0735211292
- **Site:** <https://jamesclear.com/atomic-habits>
- **Conceitos:** Aggregation of marginal gains, Identity-based habits, Two-Minute Rule, Habit stacking

---

## 2. Conceitos do Domínio

O modelo de domínio organiza o gerenciamento de tempo em torno de três conceitos centrais: Routines (templates semanais que agrupam hábitos relacionados), Habits (templates de eventos recorrentes que representam o planejamento ideal) e HabitInstances (ocorrências concretas em datas específicas que rastreiam a execução real). Tasks complementam o sistema como eventos independentes e não-recorrentes. As entidades Timer e TimeLog fornecem capacidades de rastreamento de tempo, enquanto Tags oferecem categorização visual.

### 2.1. Entidades Principais

| Entidade          | Descrição                                              |
| ----------------- | ------------------------------------------------------ |
| **Routine**       | Template semanal que agrupa hábitos relacionados       |
| **Habit**         | Evento recorrente, template do "ideal"                 |
| **HabitInstance** | Ocorrência real em data específica, o "real"           |
| **Task**          | Evento pontual não-recorrente (checkbox com data/hora) |
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

### 2.3. Glossário

| Termo                | Definição                                               |
| -------------------- | ------------------------------------------------------- |
| **Conflito**         | Dois eventos ocupam mesmo intervalo de tempo            |
| **Event Reordering** | Processo de reorganizar eventos quando um atrasa        |
| **Streak**           | Dias consecutivos com habito DONE                       |
| **Skip**             | Pular habito conscientemente (com ou sem justificativa) |
| **Substatus**        | Qualificação adicional de DONE ou NOT_DONE              |
| **Completion %**     | Percentual de tempo realizado vs planejado              |

---

## 3. Routine

A Routine é a unidade organizacional de mais alto nível no TimeBlock Organizer. Ela representa o plano ideal de uma semana — o desenho intencional de como o usuário quer distribuir seu tempo entre os hábitos que compõem sua identidade. No vocabulário do Atomic Habits, criar uma rotina é um ato de _environment design_: ao posicionar blocos de tempo fixos para exercício, estudo, trabalho profundo e descanso, o usuário está construindo o ambiente temporal onde bons hábitos se tornam o caminho de menor resistência.

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

```
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

---

## 4. Habit

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

---

## 5. HabitInstance

A HabitInstance é o átomo do TimeBlock Organizer — a menor unidade acionável do sistema. Cada instância representa uma oportunidade concreta e específica de executar um hábito: "Leitura, dia 20 de fevereiro, das 21:00 às 22:00". Enquanto o Habit expressa a intenção recorrente, a HabitInstance captura a realidade de um único dia. É nela que o ciclo de feedback se completa: o usuário planeja (Habit), executa (HabitInstance), mede (Timer/TimeLog) e avalia (substatus).

O ciclo de vida de uma instância segue três estados principais: PENDING (aguardando execução), DONE (concluída) e NOT*DONE (não realizada). Mas a riqueza do modelo está nos substatus que qualificam \_como* cada transição aconteceu. Uma instância DONE pode ser FULL (tempo completo), PARTIAL (tempo reduzido), OVERDONE (ligeiramente acima) ou EXCESSIVE (muito acima do planejado). Uma instância NOT_DONE pode ser SKIPPED (pulada conscientemente, com justificativa) ou IGNORED (expirou sem ação). Essa granularidade transforma um simples checkbox em um registro nuanceado que permite ao usuário identificar padrões e ajustar sua rotina com dados reais.

O cálculo de substatus é automático e baseado no percentual de completude: a razão entre o tempo real de execução e o tempo planejado. Se a meditação planejada para 30 minutos durou 25 minutos, o percentual é 83% e o substatus é PARTIAL. Essa automação libera o usuário de avaliações subjetivas — o sistema calcula, o usuário decide o que fazer com a informação. Cada HabitInstance mantém referência ao seu Habit pai, data específica e horários (que podem diferir do template se o usuário fez ajustes pontuais naquele dia), preservando a separação entre plano e execução.

### BR-HABITINSTANCE-001: Status Principal

**Descrição:** HabitInstance possui 3 status principais.

**Enum Status:**

```python
class Status(str, Enum):
    PENDING = "pending"      # Agendado, não iniciado
    DONE = "done"            # Realizado
    NOT_DONE = "not_done"    # Não realizado
```

**Transições:**

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

### BR-HABITINSTANCE-002: Substatus Obrigatório

**Descrição:** Status finais requerem substatus correspondente.

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
    IGNORED = "ignored"      # Timeout sem ação
```

**Regras de Consistência:**

1. DONE requer done_substatus preenchido
2. NOT_DONE requer not_done_substatus preenchido
3. PENDING não pode ter substatus
4. Substatus são mutuamente exclusivos

**Validação:**

```python
def validate_status_consistency(self) -> None:
    if self.status == Status.DONE:
        if self.done_substatus is None:
            raise ValueError("done_substatus obrigatório quando status=DONE")
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

**Descrição:** DoneSubstatus é calculado baseado em completion percentage.

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

### BR-HABITINSTANCE-004: Timeout Automático

**Descrição:** Instancia PENDING sem ação após prazo é marcada como IGNORED.

**Regra:**

- Instancia PENDING > 48h após scheduled_start
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

**Nota:** Timeout automático está documentado mas ainda não implementado no MVP. Property `is_overdue` apenas verifica atraso.

**Testes:**

- `test_br_habitinstance_004_is_overdue_pending`
- `test_br_habitinstance_004_not_overdue_done`

---

### BR-HABITINSTANCE-005: Edição de Instancia

**Descrição:** Usuário pode editar horário de uma HabitInstance específica.

**Comando:**

```bash
habit edit INSTANCE_ID --start 08:00 --end 09:30
```

**Comportamento:**

- Novo horário aplicado apenas àquela instância
- Outras instâncias mantêm horário do template
- Não afeta Habit (template)

**Testes:**

- `test_br_habitinstance_005_edit_single`
- `test_br_habitinstance_005_preserves_template`

### BR-HABITINSTANCE-006: Listagem de Instâncias

**Descrição:** Sistema permite listar instâncias com filtros opcionais.

**Filtros Disponíveis:**

- `habit_id`: Filtra por hábito específico
- `date_start`: Data inicial do período
- `date_end`: Data final do período

**Comportamento:**

- Sem filtros: retorna todas as instâncias
- Com filtros: aplica AND entre filtros fornecidos
- Nenhum resultado: retorna lista vazia (nunca None)
- Ordenação: por data ascendente

**Testes:**

- `test_br_habitinstance_006_list_all`
- `test_br_habitinstance_006_filter_by_habit`
- `test_br_habitinstance_006_filter_by_date_range`
- `test_br_habitinstance_006_returns_empty_list`

---

---

## 6. Skip

O Skip é o mecanismo que transforma ausência em informação. Na maioria dos sistemas de rastreamento de hábitos, não fazer algo é simplesmente um vazio — um dia sem marcação que pode significar esquecimento, preguiça, doença ou uma decisão racional. O TimeBlock Organizer distingue entre "não fiz porque escolhi não fazer" (Skip) e "não fiz porque ignorei" (Ignored), e dentro do Skip, diferencia _por que_ o usuário optou por pular.

As categorias de SkipReason cobrem os motivos mais comuns: saúde, trabalho, família, viagem, clima, falta de recursos, emergência e outros. Quando o usuário pula um hábito conscientemente e registra o motivo, está gerando dados que o sistema pode usar para identificar padrões. Se toda segunda-feira o hábito "Corrida" é skipado com motivo "Trabalho", talvez a segunda não seja o melhor dia para correr — e a rotina deveria ser ajustada. Uma nota opcional permite contexto adicional: "Reunião de emergência" ou "Gripe, repouso médico".

Essa filosofia se conecta diretamente com o princípio de transparência do sistema. Pular conscientemente não é falhar — é adaptar-se com honestidade. O registro de skips preserva a integridade da cadeia de hábitos: um skip com justificativa não quebra o streak (dependendo da configuração), enquanto uma instância ignorada (que expirou sem ação do usuário) quebra. Essa distinção incentiva o usuário a manter o sistema atualizado mesmo nos dias em que não consegue executar o plano, porque há uma recompensa tangível: a preservação do streak e a geração de dados úteis.

### BR-SKIP-001: Categorização de Skip

**Descrição:** Skip de habit deve ser categorizado usando enum SkipReason.

**Enum SkipReason:**

```python
class SkipReason(str, Enum):
    HEALTH = "saude"                   # Saude (doenca, consulta)
    WORK = "trabalho"                  # Trabalho (reuniao, deadline)
    FAMILY = "familia"                 # Familia (evento, emergencia)
    TRAVEL = "viagem"                  # Viagem/Deslocamento
    WEATHER = "clima"                  # Clima (chuva, frio)
    LACK_RESOURCES = "falta_recursos"  # Falta de recursos
    EMERGENCY = "emergencia"           # Emergencias
    OTHER = "outro"                    # Outros
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

**Descrição:** HabitInstance possui campos para rastrear skip.

**Campos:**

```python
skip_reason: SkipReason | None    # Categoria (obrigatório se justified)
skip_note: str | None             # Nota opcional (max 500 chars)
```

**Regras:**

1. SKIPPED_JUSTIFIED requer skip_reason
2. SKIPPED_UNJUSTIFIED não tem skip_reason
3. skip_note é sempre opcional

**Validação:**

```python
if self.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED:
    if self.skip_reason is None:
        raise ValueError("skip_reason obrigatório para SKIPPED_JUSTIFIED")
else:
    if self.skip_reason is not None:
        raise ValueError("skip_reason só permitido com SKIPPED_JUSTIFIED")
```

**Testes:**

- `test_br_skip_002_justified_requires_reason`
- `test_br_skip_002_unjustified_no_reason`
- `test_br_skip_002_note_optional`

---

### BR-SKIP-003: Prazo para Justificar

**Descrição:** Usuário tem 48h após horário planejado para justificar skip.

**Comportamento:**

- Dentro de 48h: pode adicionar/editar justificativa
- Apos 48h: instância marcada como IGNORED automaticamente
- IGNORED pode receber justificativa retroativa (recuperação)

**Nota:** Timeout automático documentado, implementação pendente.

**Testes:**

- `test_br_skip_003_within_deadline`
- `test_br_skip_003_after_deadline_ignored`

---

### BR-SKIP-004: CLI Prompt Interativo

**Descrição:** Ao dar skip, CLI oferece prompt interativo para categorizar.

**Fluxo:**

```bash
$ habit skip 42

Por que você esta pulando Academia hoje?

[1] Saúde
[2] Trabalho
[3] Família
[4] Viagem
[5] Clima
[6] Falta de recursos
[7] Emergência
[8] Outro
[9] Sem justificativa

Escolha [1-9]: _
```

**Comportamento:**

- Opções 1-8: SKIPPED_JUSTIFIED + skip_reason
- Opção 9: SKIPPED_UNJUSTIFIED + skip_reason=None

**Testes:**

- `test_br_skip_004_interactive_justified`
- `test_br_skip_004_interactive_unjustified`

---

## 7. Streak

O Streak é a métrica motivacional central do TimeBlock Organizer. Ele conta dias consecutivos em que o hábito foi executado (status DONE), e sua simples existência cria um poderoso incentivo psicológico: quanto maior a sequência, maior o custo percebido de quebrá-la. Jerry Seinfeld popularizou esse conceito como "don't break the chain" — marque um X no calendário todo dia, e a corrente de Xs se torna a motivação.

O cálculo de streak no TimeBlock é intencionalmente justo com o usuário. A contagem só considera dias em que o hábito tinha instância agendada: se o hábito é WEEKDAYS e hoje é sábado, a ausência de execução no fim de semana não quebra a cadeia. Da mesma forma, instâncias SKIPPED com justificativa são tratadas como neutras — o dia não conta como executado, mas também não interrompe a sequência. Apenas instâncias com status NOT_DONE e substatus IGNORED (o usuário simplesmente não apareceu) quebram o streak. Essa lógica reflete a filosofia de que a vida acontece e adaptações conscientes não deveriam ser punidas.

O sistema mantém dois valores: o streak atual (corrente em andamento) e o melhor streak histórico (recorde pessoal). A visualização na TUI usa esses valores no card de Métricas do Dashboard e no painel de detalhes da tela de Rotinas, criando um loop de feedback imediato que conecta a ação diária ao progresso de longo prazo.

### BR-STREAK-001: Algoritmo de Cálculo

**Descrição:** Streak conta dias consecutivos com `status = DONE`, do mais recente para trás.

**Algoritmo:**

```python
def calculate_streak(habit_id: int) -> int:
    instances = get_instances_by_date(habit_id)  # Ordem cronológica
    streak = 0

    for instance in reversed(instances):  # Mais recente primeiro
        if instance.status == Status.DONE:
            streak += 1
        elif instance.status == Status.NOT_DONE:
            break  # Para no primeiro NOT_DONE
        # PENDING não conta nem quebra

    return streak
```

**Regras:**

1. Direção: presente → passado
2. Conta: apenas DONE (qualquer substatus)
3. Para: no primeiro NOT_DONE
4. Ignora: PENDING (futuro)

**Testes:**

- `test_br_streak_001_counts_done`
- `test_br_streak_001_stops_at_not_done`
- `test_br_streak_001_ignores_pending`

---

### BR-STREAK-002: Condições de Quebra

**Descrição:** Streak SEMPRE quebra quando `status = NOT_DONE`, independente do substatus.

**Todos quebram:**

| Substatus           | Quebra? | Impacto Psicológico |
| ------------------- | ------- | ------------------- |
| SKIPPED_JUSTIFIED   | Sim     | Baixo               |
| SKIPPED_UNJUSTIFIED | Sim     | Medio               |
| IGNORED             | Sim     | Alto                |

**Filosofia (Atomic Habits - James Clear):**

- Consistência > Perfeição
- "Nunca pule dois dias seguidos"
- Skip consciente ainda é quebra
- Diferenciamos impacto psicológico, não o fato da quebra

**Testes:**

- `test_br_streak_002_breaks_on_skipped_justified`
- `test_br_streak_002_breaks_on_skipped_unjustified`
- `test_br_streak_002_breaks_on_ignored`

---

### BR-STREAK-003: Condições de Manutenção

**Descrição:** Streak SEMPRE mantêm quando `status = DONE`, independente do substatus.

**Todos mantêm:**

| Substatus | Mantém? | Feedback      |
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

**Descrição:** Dias sem instância não quebram streak.

**Exemplo:**

- Habit é WEEKDAYS (seg-sex)
- Hoje é sábado (sem instância)
- Streak continua válido

**Regra:** Apenas instâncias NOT_DONE quebram streak. Ausência de instância é neutra.

**Testes:**

- `test_br_streak_004_weekend_no_break`
- `test_br_streak_004_gap_no_break`

---

## 8. Task

A Task é o complemento pontual dos Habits recorrentes. Enquanto hábitos representam identidade e repetição ("sou alguém que lê todos os dias"), tasks representam compromissos únicos e finitos ("dentista dia 25 às 14h", "entregar relatório até sexta"). São os eventos que não fazem parte do plano ideal da semana, mas que precisam ocupar espaço na agenda e competir por atenção com os blocos de hábitos.

A independência estrutural da Task em relação à Routine é uma decisão deliberada de design. Uma tarefa de trabalho não pertence à "Rotina Matinal" nem à "Rotina Noturna" — ela existe por si só, visível independente de qual rotina está ativa. Trocar de rotina não esconde tarefas pendentes. Deletar uma rotina não afeta tarefas. Essa separação garante que compromissos pontuais nunca desapareçam acidentalmente ao reorganizar hábitos recorrentes.

O modelo de Task é intencionalmente simples: título, data/hora, descrição opcional e um estado binário derivado (pendente se `completed_datetime` é nulo, concluída se preenchido). Não há prioridade, não há subtarefas, não há dependências. Essa simplicidade é proposital: o TimeBlock Organizer não é um gerenciador de projetos. Tasks existem para que eventos pontuais possam ser posicionados na linha do tempo ao lado dos hábitos, criando uma visão completa do dia — e para que o sistema possa detectar conflitos entre tasks e hábitos da rotina.

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

```
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

## 9. Timer

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

```
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

```
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

## 10. Event Reordering

O Event Reordering trata do problema mais frequente no uso diário de time blocking: o que acontece quando a realidade diverge do plano. Um hábito atrasou quinze minutos, uma reunião invadiu o horário da leitura, o almoço se estendeu. Em um sistema rígido, esses desvios gerariam erros ou bloqueios. O TimeBlock Organizer adota a abordagem oposta: conflitos são permitidos, detectados, apresentados e — crucialmente — nunca resolvidos automaticamente.

Essa filosofia reflete o princípio de Controle do Usuário: o sistema informa, o usuário decide. Quando dois eventos ocupam o mesmo intervalo de tempo, o sistema detecta a sobreposição e a apresenta visualmente (blocos lado a lado na timeline, borda vermelha), mas não move nenhum evento. Não sugere novos horários. Não aplica regras de prioridade. A razão é simples: o sistema não tem informação suficiente para tomar essa decisão. Só o usuário sabe se a reunião que invadiu o horário de leitura é mais importante que a leitura, ou se prefere encurtar ambas, ou se vai compensar no dia seguinte.

Conflitos são calculados dinamicamente por comparação temporal entre eventos, não armazenados como entidade separada. Isso garante que, ao ajustar o horário de uma instância, os conflitos se recalculam automaticamente. O algoritmo de sugestão de reordenamento automático (Simple Cascade) está planejado para v2.0, mas seguirá o mesmo princípio: o sistema _sugerirá_, nunca _imporá_.

### BR-REORDER-001: Definição de Conflito

**Descrição:** Conflito ocorre quando dois eventos tem sobreposição temporal no mesmo dia.

**Detecção:**

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

**Descrição:** Detecção de conflitos ocorre dentro do mesmo dia (00:00-23:59).

**Regra:** Eventos de dias diferentes NÃO podem conflitar, mesmo que horários se sobreponham numericamente.

**Testes:**

- `test_br_reorder_002_same_day_only`
- `test_br_reorder_002_different_days_no_conflict`

---

### BR-REORDER-003: Apresentação de Conflitos

**Descrição:** Sistema apresenta conflitos de forma clara ao usuário.

**Quando Apresentar:**

1. Apos criar/ajustar evento que resulta em conflito
2. Quando usuário solicita visualização de conflitos
3. Antes de iniciar timer, se houver conflitos

**Formato:**

```
Conflito detectado:
  - Academia: 07:00-08:00
  - Reuniao: 07:30-08:30
  Sobreposição: 30 minutos
```

**Testes:**

- `test_br_reorder_003_presents_conflicts`
- `test_br_reorder_003_shows_overlap_duration`

---

### BR-REORDER-004: Conflitos Não Bloqueiam

**Descrição:** Conflitos são informativos, NÃO impeditivos.

**Comportamento:**

- Timer start com conflito: apenas avisa, pergunta confirmação
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

**Descrição:** Conflitos NÃO são persistidos no banco. São calculados dinamicamente.

**Justificativa:** Conflitos são resultado de relação temporal entre eventos. Como eventos podem mudar, conflitos devem ser recalculados.

**Testes:**

- `test_br_reorder_005_calculated_dynamically`
- `test_br_reorder_005_no_conflict_table`

---

### BR-REORDER-006: Algoritmo de Reordenamento

**Descrição:** Algoritmo de sugestão de reordenamento NÃO está no MVP.

**Status Atual:**

- Sistema detecta conflitos
- Sistema apresenta conflitos
- Sistema NÃO sugere novos horários automaticamente

**Futuro:** Algoritmo Simple Cascade planejado para v2.0.

---

## 11. Validações Globais

As Validações Globais são restrições estruturais que garantem integridade dos dados independente do domínio. Correspondem ao Nível 1 da hierarquia de regras (seção 1.2): violá-las torna o sistema inconsistente, e por isso são aplicadas incondicionalmente em todas as operações de escrita. Um horário de início posterior ao de fim, uma duração negativa ou um título vazio são erros que nenhuma lógica de domínio deveria permitir, independente do contexto.

Essas validações operam na camada de services (antes de chegar ao banco) e na camada de models (restrições de tipo e formato). A duplicidade é intencional: a validação no service garante feedback imediato e mensagens legíveis para o usuário, enquanto a validação no model serve como última linha de defesa contra bugs na camada superior. Erros de validação são sempre exibidos inline na TUI e com mensagem clara na CLI, indicando exatamente qual campo falhou e qual é o formato esperado.

### BR-VAL-001: Validação de Horários

**Regras:**

- `start_time < end_time`
- `duration_minutes > 0`
- Horários dentro do dia (00:00 - 23:59)

**Testes:**

- `test_br_val_001_start_before_end`
- `test_br_val_001_positive_duration`

---

### BR-VAL-002: Validação de Datas

**Regras:**

- Data não anterior a 2025-01-01
- Sem limite de data futura
- Formato ISO 8601

**Testes:**

- `test_br_val_002_min_date`
- `test_br_val_002_iso_format`

---

### BR-VAL-003: Validação de Strings

| Campo       | Limite       |
| ----------- | ------------ |
| title       | 1-200 chars  |
| description | 0-2000 chars |
| name        | 1-200 chars  |
| note        | 0-500 chars  |

**Comportamento:** Trim de espaços antes da validação.

**Testes:**

- `test_br_val_003_title_limits`
- `test_br_val_003_trim_whitespace`

---

## 12. CLI

A CLI (Command Line Interface) é a interface primária do TimeBlock Organizer e a única que existia antes da TUI. Toda funcionalidade do sistema é acessível via comandos no terminal, seguindo o padrão resource-first definido no ADR-005: o substantivo vem antes do verbo (`habit create`, `routine activate`, `task list`). Esse padrão torna os comandos previsíveis e autodescritivos — um usuário que sabe usar `habit create` adivinha corretamente que `habit list`, `habit edit` e `habit delete` existem.

A CLI serve dois públicos com necessidades distintas. Para uso interativo diário, ela oferece atalhos, flags curtas e outputs formatados com Rich. Para automação e scripts, ela garante códigos de saída consistentes, outputs parseáveis e comportamento determinístico (sem prompts interativos quando o input é completo). As regras desta seção formalizam comportamentos que cruzam domínios: validação de flags dependentes (se informou `--start`, deve informar `--end`), formatos de data/hora aceitos e padrões de output entre comandos.

### BR-CLI-001: Validação de Flags Dependentes

**Descrição:** Flags que dependem de outras devem ser validadas antes da execução do comando.

**Pares Obrigatórios:**

| Flag Principal | Requer  | Comando Afetado |
| -------------- | ------- | --------------- |
| --start        | --end   | habit create    |
| --end          | --start | habit create    |
| --from         | --to    | report \*       |
| --to           | --from  | report \*       |

**Comportamento:**

- Se apenas uma flag do par for fornecida: ERROR
- Mensagem clara indicando a dependência

**Exemplo de Erro:**

```bash
$ habit create --title "Academia" --start 07:00
[ERROR] --start requer --end (e vice-versa)
```

**Testes:**

- `test_br_cli_001_start_requires_end`
- `test_br_cli_001_end_requires_start`
- `test_br_cli_001_from_requires_to`
- `test_br_cli_001_to_requires_from`

---

### BR-CLI-002: Formatos de Datetime Aceitos

**Descrição:** Sistema aceita múltiplos formatos de data e hora para flexibilidade do usuário.

**Formatos de Datetime (--datetime):**

| Formato          | Exemplo          |
| ---------------- | ---------------- |
| YYYY-MM-DD HH:MM | 2025-12-25 14:30 |
| YYYY-MM-DD HHhMM | 2025-12-25 14h30 |
| YYYY-MM-DD HHh   | 2025-12-25 14h   |
| DD-MM-YYYY HH:MM | 25-12-2025 14:30 |
| DD-MM-YYYY HHhMM | 25-12-2025 14h30 |
| DD-MM-YYYY HHh   | 25-12-2025 14h   |
| DD/MM/YYYY HH:MM | 25/12/2025 14:30 |
| DD/MM/YYYY HHhMM | 25/12/2025 14h30 |
| DD/MM/YYYY HHh   | 25/12/2025 14h   |

**Formatos de Date (--date, --from, --to):**

| Formato    | Exemplo    |
| ---------- | ---------- |
| YYYY-MM-DD | 2025-12-25 |
| DD-MM-YYYY | 25-12-2025 |
| DD/MM/YYYY | 25/12/2025 |

**Comportamento:**

- Parser tenta cada formato em ordem
- Primeiro match válido é usado
- Formato inválido: ERROR com mensagem "Veja formatos aceitos com --help"

**Testes:**

- `test_br_cli_002_datetime_iso_format`
- `test_br_cli_002_datetime_brazilian_format`
- `test_br_cli_002_date_multiple_formats`

### BR-CLI-003: Padronização de Idioma

**Descrição:** Todas as mensagens, helps e textos exibidos ao usuário devem estar em Português Brasileiro (PT-BR).

**Referência:** ADR-018-language-standards.md

**Escopo:**

| Elemento             | Idioma Obrigatório | Exemplo                     |
| -------------------- | ------------------ | --------------------------- |
| Mensagens de erro    | PT-BR              | "Erro ao criar evento"      |
| Mensagens de sucesso | PT-BR              | "Hábito criado com sucesso" |
| Help de comandos     | PT-BR              | help="Título do hábito"     |
| Help de flags        | PT-BR              | help="Hora início (HH:MM)"  |
| Prompts interativos  | PT-BR              | "Confirmar? [S/n]"          |
| Docstrings CLI       | PT-BR              | """Cria um novo hábito."""  |

**Exceções (permitido inglês):**

| Elemento                     | Motivo                |
| ---------------------------- | --------------------- |
| Nomes de variáveis           | Padrão de código      |
| Nomes de funções/classes     | Padrão de código      |
| Tipos em commits             | Conventional commits  |
| Termos técnicos sem tradução | Ex: "timer", "status" |

**Estado Atual:** PARCIALMENTE IMPLEMENTADO (ver DT-006 em roadmap.md)

**Testes:**

- `test_br_cli_003_error_messages_ptbr`
- `test_br_cli_003_success_messages_ptbr`
- `test_br_cli_003_help_texts_ptbr`

---

## 13. Tag

Tags são um sistema leve de categorização visual que complementa a organização por rotina. Enquanto a Routine agrupa hábitos por contexto de vida (matinal, noturna, férias) e a recorrência define _quando_ acontecem, a Tag permite agrupar hábitos e tasks por _natureza_: saúde, estudo, trabalho, lazer. Um hábito de corrida na rotina matinal e um hábito de musculação na rotina noturna podem compartilhar a mesma tag "Fitness", criando uma dimensão transversal de organização.

O modelo é deliberadamente mínimo: uma tag tem uma cor (obrigatória, com default amarelo) e um nome (opcional — uma tag pode ser puramente cromática). Cada hábito ou task pode ter no máximo uma tag. A simplicidade é intencional: tags não são folders, projetos ou hierarquias. São um canal visual rápido que permite ao usuário identificar categorias de atividade na timeline e nos relatórios sem adicionar complexidade ao modelo de dados. Deletar uma tag não afeta os hábitos e tasks associados — apenas remove a cor, setando o campo para nulo.

### BR-TAG-001: Estrutura de Tag

**Descrição:** Tag é entidade para categorização de habits e tasks.

**Campos:**

```python
class Tag(SQLModel, table=True):
    id: int | None
    name: str | None           # Opcional (pode ser apenas cor)
    color: str                 # Obrigatório, default "#fbd75b" (amarelo)
```

**Regras:**

1. `color` é obrigatório (NOT NULL)
2. `color` tem default amarelo (#fbd75b)
3. `name` é opcional (pode criar tag apenas com cor)
4. `name` se presente: 1-200 chars, único (case-insensitive)

**Validação de Cor:**

- Formato hexadecimal: #RRGGBB ou #RGB
- Nomes CSS aceitos: red, blue, green, etc.

**Testes:**

- `test_br_tag_001_color_required`
- `test_br_tag_001_color_default_yellow`
- `test_br_tag_001_name_optional`
- `test_br_tag_001_name_unique`

---

### BR-TAG-002: Associação com Eventos

**Descrição:** Tags podem ser associadas a Habits e Tasks.

**Relacionamento:**

```
Tag (1) ----< Habits (N)
Tag (1) ----< Tasks (N)
```

**Regras:**

1. Habit pode ter 0 ou 1 tag (tag_id nullable)
2. Task pode ter 0 ou 1 tag (tag_id nullable)
3. Deletar tag NÃO deleta habits/tasks associados
4. Deletar tag seta tag_id = NULL nos associados

**Testes:**

- `test_br_tag_002_habit_optional_tag`
- `test_br_tag_002_task_optional_tag`
- `test_br_tag_002_delete_tag_nullifies`

---

## 14. TUI

A TUI (Terminal User Interface) é a segunda interface do TimeBlock Organizer, projetada para o uso interativo diário que a CLI, por sua natureza sequencial, não consegue atender com a mesma fluidez. Consultar a agenda, marcar hábitos como concluídos, iniciar um timer e verificar métricas são operações que no CLI exigem múltiplos comandos separados; na TUI, estão a um ou dois keybindings de distância, visíveis simultaneamente na mesma tela.

A TUI foi implementada com o framework Textual (ADR-031), que utiliza Rich internamente — uma dependência que o projeto já possui para a formatação do output da CLI. A decisão arquitetural mais importante é que a TUI compartilha 100% da camada de services com a CLI: nenhuma lógica de negócio é duplicada. A TUI é exclusivamente interface — captura input do usuário, chama o service apropriado com uma session de banco de dados efêmera (session-per-action), e exibe o resultado com widgets estilizados. Se um service funciona na CLI, funciona na TUI; se uma regra de negócio muda, muda em um único lugar.

O design visual segue um sistema Material-like com paleta de cores definida em TCSS (arquivo único, single source of truth), cards com bordas arredondadas, spacing consistente e hierarquia visual clara entre texto primário, secundário e metadados. A TUI opera em cinco screens navegáveis por sidebar (Dashboard, Routines, Habits, Tasks, Timer), cada uma com keybindings específicos documentados nas BRs a seguir. O Dashboard concentra a visão do dia com alta densidade informacional; a tela de Rotinas exibe a semana completa em grade temporal; as demais screens oferecem CRUD completo com formulários inline.

**Referências:** ADR-006 (decisão original), ADR-031 (implementação), ADR-007 (service layer)

---

### BR-TUI-001: Entry Point Detection

**Descrição:** O binário `timeblock` sem argumentos abre a TUI. Com argumentos, executa CLI normalmente. Se Textual não está instalado, exibe mensagem de orientação.

**Regras:**

1. `timeblock` (sem args) → Abre TUI
2. `timeblock <qualquer-arg>` → Executa CLI (Typer)
3. `timeblock --help` → Help da CLI (tem argumento)
4. Se Textual não instalado e sem args → Mensagem orientando instalação
5. CLI NUNCA depende de Textual (import condicional)

**Implementação:**

```python
import sys

def main():
    if len(sys.argv) <= 1:
        try:
            from timeblock.tui.app import TimeBlockApp
            TimeBlockApp().run()
        except ImportError:
            print("[WARN] TUI requer 'textual'.")
            print("       Instale: pip install timeblock-organizer[tui]")
            print("       Uso CLI: timeblock --help")
    else:
        app()  # Typer
```

**Testes:**

- `test_br_tui_001_no_args_launches_tui`
- `test_br_tui_001_with_args_launches_cli`
- `test_br_tui_001_help_uses_cli`
- `test_br_tui_001_fallback_without_textual`

---

### BR-TUI-002: Screen Navigation

**Descrição:** A TUI possui 5 screens navegáveis por sidebar. Navegação por keybindings numéricos ou mnemônicos. Apenas uma screen ativa por vez.

**Regras:**

1. Screens disponíveis: Dashboard, Routines, Habits, Tasks, Timer
2. Screen inicial ao abrir: Dashboard
3. Keybindings numéricos: `1`=Dashboard, `2`=Routines, `3`=Habits, `4`=Tasks, `5`=Timer
4. Keybindings mnemônicos: `d`=Dashboard, `r`=Routines, `h`=Habits, `t`=Tasks, `m`=Timer (de "medidor")
5. Sidebar exibe todas as screens com indicador da screen ativa
6. Navegação preserva estado da screen anterior (não reseta dados em edição)

**Testes:**

- `test_br_tui_002_initial_screen_is_dashboard`
- `test_br_tui_002_numeric_keybinding_navigation`
- `test_br_tui_002_mnemonic_keybinding_navigation`
- `test_br_tui_002_sidebar_shows_active_screen`

---

### BR-TUI-003: Dashboard Screen

**Descrição:** O Dashboard exibe visão completa e interativa do dia corrente com alta densidade informacional. Layout híbrido composto por: header bar com contexto resumido, agenda vertical estilo Google Calendar com blocos de tempo proporcionais, e grid de cards (hábitos, tarefas, timer, métricas). Serve como ponto de entrada principal e painel de controle diário.

**Referências:** ADR-031 seção 4, BR-TUI-008 (visual), BR-TUI-009 (services)

**Regras:**

1. **Header Bar:** barra compacta (3 linhas) exibe rotina ativa, progresso do dia (X/Y hábitos + barra visual + percentual), contagem de tarefas pendentes, timer ativo (se houver) e data atual. Se não há rotina ativa, exibe "[Sem rotina]" com orientação para criar/ativar
2. **Agenda do Dia (timeline vertical):** coluna esquerda do conteúdo. Régua de tempo com granularidade de 30 minutos (06:00, 06:30, 07:00, ..., 22:00) e blocos proporcionais à duração — um bloco de 30min ocupa 1 slot visual, um de 1h ocupa 2 slots, etc. Cada bloco exibe: nome do evento, status com cor, duração formatada (Xmin para < 60, Xh ou XhYY para >= 60). Marcador `▸` indica slot atual. Blocos concluídos usam `░` ($success), ativo usa `▓` ($primary-light), pendentes usam `┄` ($muted), skipados usam `╌` ($warning). Horários livres entre blocos exibem `┈ livre ┈` centralizado. Conflitos (overlaps) renderizam blocos lado a lado divididos por `│`
3. **Card Hábitos:** lista instâncias do dia com indicador de status (✓ done, ▶ running, ✗ skipped, ! missed, · pending), nome, horário início–fim, duração real/planejada e sparkline de esforço relativo (◼◼◼). Título inclui contador X/Y. Quick actions: `enter`=done (solicita duração), `s`=skip (solicita categoria), `g`=navegar para screen Habits
4. **Card Tarefas:** lista tarefas pendentes com indicador de prioridade (!! overdue+alta, ! alta, ▪ média, · baixa), nome, prioridade, deadline abreviado. Tarefas vencidas destacadas em $error com marcador `venc.`. Quick actions: `enter`=detalhes, `c`=concluir, `g`=navegar para screen Tasks
5. **Card Timer:** display centralizado com tempo decorrido, evento associado e status (▶ RUNNING, ⏸ PAUSED, ⏹ IDLE). Resumo do dia: sessões concluídas, tempo total acumulado, média por sessão. Keybindings contextuais (exibe apenas ações válidas para o estado atual). Se idle, exibe último timer concluído com horário
6. **Card Métricas:** streak atual e melhor streak, barras de completude 7d e 30d com percentual. Histórico semanal com barra de progresso + dot matrix por hábito (✓/·) por dia. Dia atual destacado com `← hoje`. Cores das barras: verde (≥ 80%), amarelo (50–79%), vermelho (< 50%). Filtro de período alternável com `f` (7d → 14d → 30d)
7. **Layout:** três colunas — sidebar fixa (22 chars), agenda do dia (coluna central, scroll vertical), cards em grid (coluna direita, 2 cards empilhados por subcoluna)
8. **Navegação entre zonas:** `Tab`/`Shift+Tab` navegam entre zonas focáveis (Agenda → Hábitos → Tarefas → Timer → Métricas → cicla). Cada zona tem keybindings próprios. `g` em qualquer zona navega para a screen completa correspondente
9. **Refresh:** dados atualizados ao entrar na screen (on_focus) e após qualquer quick action. Timer atualiza header e card Timer a cada segundo quando ativo
10. **Responsividade:** 3 breakpoints — ≥120 cols (completo: 3 colunas, agenda + cards), 80–119 cols (compacto: agenda reduzida, cards com conteúdo truncado), <80 cols (minimal: layout 1 coluna, agenda oculta, cards empilhados verticalmente)

**Mockup de referência:** `docs/tui/dashboard-mockup-v3.md`

**Composição de widgets:**

```python
class DashboardScreen(Screen):
    """Dashboard principal com layout híbrido."""

    def compose(self) -> ComposeResult:
        yield HeaderBar(id="header-bar")
        with Horizontal(id="content"):
            yield AgendaWidget(id="agenda")
            with Vertical(id="cards"):
                yield HabitListWidget(id="habits-today")
                yield TaskListWidget(id="tasks-pending")
            with Vertical(id="cards-right"):
                yield TimerDisplayWidget(id="timer-display")
                yield MetricsPanelWidget(id="metrics-panel")
```

**Testes:**

- `test_br_tui_003_header_shows_routine_and_progress`
- `test_br_tui_003_header_shows_no_routine_message`
- `test_br_tui_003_header_shows_timer_active`
- `test_br_tui_003_header_shows_task_count`
- `test_br_tui_003_agenda_renders_day_blocks`
- `test_br_tui_003_agenda_shows_current_time_marker`
- `test_br_tui_003_agenda_block_colors_by_status`
- `test_br_tui_003_agenda_shows_free_slots`
- `test_br_tui_003_agenda_renders_conflict_side_by_side`
- `test_br_tui_003_agenda_running_block_with_projection`
- `test_br_tui_003_habits_list_with_status_and_time`
- `test_br_tui_003_habits_shows_effort_sparkline`
- `test_br_tui_003_habits_quick_done_action`
- `test_br_tui_003_habits_quick_skip_action`
- `test_br_tui_003_habits_go_to_screen`
- `test_br_tui_003_tasks_sorted_by_priority`
- `test_br_tui_003_tasks_overdue_highlighted`
- `test_br_tui_003_tasks_quick_complete_action`
- `test_br_tui_003_timer_shows_active_session`
- `test_br_tui_003_timer_shows_idle_with_last_session`
- `test_br_tui_003_timer_shows_session_summary`
- `test_br_tui_003_timer_contextual_keybindings`
- `test_br_tui_003_metrics_shows_streak`
- `test_br_tui_003_metrics_shows_weekly_history`
- `test_br_tui_003_metrics_dot_matrix_per_habit`
- `test_br_tui_003_metrics_period_filter`
- `test_br_tui_003_metrics_bar_colors_by_threshold`
- `test_br_tui_003_responsive_compact_layout`
- `test_br_tui_003_responsive_minimal_layout`
- `test_br_tui_003_tab_navigates_zones`
- `test_br_tui_003_refreshes_on_focus`
- `test_br_tui_003_refreshes_after_quick_action`
- `test_br_tui_003_timer_updates_every_second`

---

### BR-TUI-004: Global Keybindings (REVISADA 25/02/2026)

**Descrição:** Keybindings globais funcionam em qualquer screen. Ações exigem modificador Ctrl. Navegação pura não exige modificador. Ações destrutivas e irreversíveis exigem modal de confirmação.

**Política de modificador:**

```plaintext
SEM modificador (navegação pura, sem risco):
  Tab / Shift+Tab ...... navegar entre zonas/cards
  1-5 .................. trocar screen (numérico)
  d/r/h/t/m ............ trocar screen (mnemônico)
  Setas / j/k .......... navegar dentro do card
  ? .................... help overlay (leitura)
  Escape ............... fechar modal / voltar ao Dashboard

COM Ctrl (todas as ações):
  Ctrl+Q ............... sair da TUI [MODAL]
  Ctrl+Enter ........... confirmar / mark done [MODAL se irreversível]
  Ctrl+S ............... skip (hábito) / start (timer)
  Ctrl+P ............... pause/resume (timer)
  Ctrl+X ............... deletar item selecionado [MODAL]
  Ctrl+N ............... novo item (abre formulário)
  Ctrl+E ............... editar item selecionado
  Ctrl+K ............... complete task [MODAL]
  Ctrl+W ............... cancel timer [MODAL]

PROIBIDOS (reservados pelo OS):
  Ctrl+C ............... SIGINT (nunca capturar)
  Ctrl+Z ............... SIGTSTP (nunca capturar)
  Ctrl+D ............... EOF (nunca capturar)
```

**Modal de confirmação exigido em:**

- Ctrl+Q (sair, especialmente com timer ativo)
- Ctrl+X (deletar item)
- Ctrl+W (cancelar timer, descarta sessão)
- Ctrl+K (completar task, irreversível)
- Ctrl+Enter (mark done, quando hábito já done/overdone)

**Regras:**

1. Todas as ações exigem modificador Ctrl
2. Navegação pura (Tab, setas, números, ?, Escape) sem modificador
3. Ações destrutivas/irreversíveis exigem modal de confirmação
4. Modal exibe nome do item afetado e ação a ser executada
5. Modal responde apenas a Enter (confirmar) e Escape (cancelar)
6. Ctrl+C, Ctrl+Z, Ctrl+D nunca são capturados pela TUI
7. Se timer ativo e Ctrl+Q, modal informa que sessão será perdida
8. Keybindings de screen (CRUD) só funcionam na screen/zona ativa
9. Help overlay (?) lista todos os keybindings com modificadores

**Testes:**

- `test_br_tui_004_quit_requires_ctrl_q`
- `test_br_tui_004_plain_q_does_nothing`
- `test_br_tui_004_quit_shows_confirmation_modal`
- `test_br_tui_004_quit_with_timer_warns_session_loss`
- `test_br_tui_004_modal_only_responds_enter_escape`
- `test_br_tui_004_help_overlay_shows_ctrl_bindings`
- `test_br_tui_004_escape_closes_modal`
- `test_br_tui_004_escape_returns_to_dashboard`
- `test_br_tui_004_ctrl_c_not_captured`

---

### BR-TUI-005: CRUD Operations Pattern

**Descrição:** Todas as screens com CRUD seguem padrão consistente de interação. Create e Update usam formulários inline. Delete requer confirmação.

**Regras:**

1. `n` ou `a` → Novo item (abre formulário inline)
2. `e` → Editar item selecionado
3. `x` → Deletar item selecionado (abre confirmação)
4. `enter` → Ver detalhes do item selecionado
5. Confirmação de delete exibe nome do item e requer `y` explícito
6. Operações de escrita usam session-per-action (ADR-031)
7. Após operação bem-sucedida, lista atualizada automaticamente
8. Erros de validação exibidos inline (não modal)

**Testes:**

- `test_br_tui_005_create_opens_form`
- `test_br_tui_005_edit_opens_prefilled_form`
- `test_br_tui_005_delete_requires_confirmation`
- `test_br_tui_005_delete_confirmation_shows_name`
- `test_br_tui_005_successful_operation_refreshes_list`
- `test_br_tui_005_validation_error_shown_inline`

---

### BR-TUI-006: Timer Screen Live Display

**Descrição:** O Timer screen exibe contagem em tempo real com atualização a cada segundo. Suporta start, pause, resume, stop e cancel. Integra com TimerService existente.

**Regras:**

1. Display atualiza a cada 1 segundo (set_interval)
2. Keybindings de timer: `s`=start, `p`=pause/resume, `enter`=stop, `c`=cancel
3. Display mostra: tempo decorrido, evento associado, status (running/paused)
4. Pause congela display; resume retoma contagem
5. Stop salva sessão e exibe resumo
6. Cancel descarta sessão com confirmação
7. Timer ativo visível na status bar de qualquer screen

**Testes:**

- `test_br_tui_006_timer_display_updates`
- `test_br_tui_006_start_keybinding`
- `test_br_tui_006_pause_resume_toggle`
- `test_br_tui_006_stop_saves_session`
- `test_br_tui_006_cancel_requires_confirmation`
- `test_br_tui_006_active_timer_in_status_bar`

---

### BR-TUI-007: Footer Contextual (REVISADA 25/02/2026)

**Descrição:** Barra de rodapé persistente com três seções: rotina ativa (esquerda, persistente), keybindings da zona focada (centro, contextual) e timer + hora (direita, persistente). O header exibe informação (o quê), o footer exibe ações (o que fazer).

**Layout:**

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Rotina Matinal     │  Ctrl+Enter done  Ctrl+S skip    │ ▶ 47:23    14:32 │
└────────────────────────────────────────────────────────────────────────────┘
  c_left (1fr)         c_center (1fr)                     c_right (auto)
```

**Keybindings por zona focada:**

| Zona    | Footer center                                 |
| ------- | --------------------------------------------- |
| Agenda  | `Ctrl+Enter done  Ctrl+S skip`                |
| Hábitos | `Ctrl+Enter done  Ctrl+S skip`                |
| Tarefas | `Ctrl+K complete  Ctrl+Enter detalhe`         |
| Timer   | `Ctrl+S start  Ctrl+P pause  Ctrl+Enter stop` |
| Nenhum  | `Tab navegar  ? ajuda  Ctrl+Q sair`           |

**Regras:**

1. Posição: rodapé, largura total, 1 linha de altura
2. Seção esquerda: nome da rotina ativa. "[Sem rotina]" se nenhuma
3. Seção central: keybindings da zona/card focado. Atualiza em on_focus
4. Seção direita: timer elapsed (atualiza 1s) + hora HH:MM (atualiza 1min)
5. Tecla em Overlay0 #6C7086, label da ação em Subtext0 #A6ADC8
6. Timer exibe ícone de estado: ▶ (running, Mauve #CBA6F7), ⏸ (paused, Yellow #F9E2AF)
7. Se nenhum timer ativo, seção direita exibe apenas hora
8. Footer visível em todas as screens, não apenas no Dashboard

**Testes:**

- `test_br_tui_007_footer_shows_active_routine`
- `test_br_tui_007_footer_shows_no_routine`
- `test_br_tui_007_footer_shows_current_time`
- `test_br_tui_007_footer_keybindings_change_on_focus`
- `test_br_tui_007_footer_agenda_zone_keybindings`
- `test_br_tui_007_footer_habits_zone_keybindings`
- `test_br_tui_007_footer_tasks_zone_keybindings`
- `test_br_tui_007_footer_timer_zone_keybindings`
- `test_br_tui_007_footer_default_keybindings`
- `test_br_tui_007_footer_timer_updates_every_second`

---

### BR-TUI-003-R12: Viewport-Aware Truncation

**Descrição:** Cards não definem limite fixo de itens. A quantidade exibida é determinada pela altura disponível do viewport. Itens que excedem o viewport são indicados por overflow indicator.

**Regras:**

1. Máximo de itens visíveis = viewport_height do card - 2 (bordas)
2. Se total > visíveis, exibe `+N ▼` no rodapé interno, alinhado à direita
3. Cor do indicador: Overlay0 #6C7086
4. Scroll interno com j/k quando card está focado (Tab)
5. Item selecionado (cursor) indicado por fundo Surface0 #313244
6. Scroll mantém item selecionado visível (auto-scroll)

**Testes:**

- `test_br_tui_003_r12_no_fixed_item_limit`
- `test_br_tui_003_r12_overflow_indicator_shown`
- `test_br_tui_003_r12_overflow_count_correct`
- `test_br_tui_003_r12_scroll_with_jk`
- `test_br_tui_003_r12_selected_item_always_visible`

---

### BR-TUI-003-R13: Régua de Horário Adaptativa

**Descrição:** A agenda exibe range de horários baseado nos eventos do dia, com piso e teto para evitar espaço desperdiçado.

**Algoritmo:** `range_start = min(06, first_event_hour - 1)`, `range_end = max(22, last_event_hour + 1)`

**Regras:**

1. Range: `min(06, first_event - 1)` até `max(22, last_event + 1)`
2. Piso absoluto: 06:00 (não exibe antes das 06:00)
3. Teto absoluto: 23:00 (não exibe após 23:00)
4. Granularidade: 30 minutos = 1 linha
5. Se nenhum evento no dia, exibe 06:00-22:00

**Testes:**

- `test_br_tui_003_r13_range_adapts_to_events`
- `test_br_tui_003_r13_floor_06_ceiling_22`
- `test_br_tui_003_r13_early_event_extends_range`
- `test_br_tui_003_r13_no_events_default_range`
- `test_br_tui_003_r13_granularity_30min`

---

### BR-TUI-003-R14: Subtítulo do Card Hábitos

**Descrição:** O border_title do card Hábitos exibe dot matrix com contagem e percentual de completude do dia.

**Formato:** `●●●○○○ X/Y Z%` onde ● = done/running, ○ = pending/not_done

**Regras:**

1. X = instâncias com status done (qualquer substatus) + running
2. Y = total de instâncias agendadas para hoje
3. Z = percentual (X / Y \* 100), arredondado
4. Dot matrix: 1 dot por instância, ● preenchido, ○ vazio
5. Máximo de dots exibidos: min(Y, 10). Se Y > 10, exibe apenas X/Y Z%
6. Cor dos ● e do Z%: Green #A6E3A1 (>= 80%), Yellow #F9E2AF (50-79%), Red #F38BA8 (< 50%)
7. Cor dos ○: Overlay0 #6C7086

**Testes:**

- `test_br_tui_003_r14_dot_matrix_count`
- `test_br_tui_003_r14_percentage_calculation`
- `test_br_tui_003_r14_color_green_above_80`
- `test_br_tui_003_r14_color_yellow_50_to_79`
- `test_br_tui_003_r14_color_red_below_50`
- `test_br_tui_003_r14_max_10_dots`
- `test_br_tui_003_r14_running_counts_as_done`

---

### BR-TUI-003-R15: Auto-scroll na Agenda

**Descrição:** Ao abrir o dashboard, a agenda faz scroll automático para posicionar a hora atual no terço superior do viewport.

**Regras:**

1. Ao montar a screen (on_mount), agenda faz scroll para hora atual
2. Posição: hora atual no terço superior do viewport visível
3. Se hora atual está antes do primeiro evento, scroll para o topo
4. Se hora atual está após o último evento, scroll para o final
5. Scroll automático ocorre apenas no mount, não a cada refresh

**Testes:**

- `test_br_tui_003_r15_autoscroll_on_mount`
- `test_br_tui_003_r15_current_time_upper_third`
- `test_br_tui_003_r15_no_scroll_if_fits_viewport`

---

### BR-TUI-003-R16: Marcador de Hora Atual

**Descrição:** O slot correspondente à hora atual recebe marcador visual ▸ no início da linha, cor Mauve #CBA6F7.

**Regras:**

1. Marcador `▸` posicionado antes do horário no slot atual
2. Cor do marcador: Mauve #CBA6F7
3. Slot atual = slot de 30min que contém a hora corrente
4. Apenas 1 marcador visível por vez
5. Marcador atualiza a cada 30 minutos (quando slot muda)

**Testes:**

- `test_br_tui_003_r16_marker_on_current_slot`
- `test_br_tui_003_r16_marker_color_mauve`
- `test_br_tui_003_r16_only_one_marker`

---

### BR-TUI-003-R17: Indicador de Tempo Livre

**Descrição:** Gaps de 30 minutos ou mais entre blocos exibem indicador `┈ livre ┈` centralizado em Overlay0 #6C7086.

**Regras:**

1. Gap = tempo entre end de um bloco e start do próximo
2. Gaps >= 30 minutos exibem `┈ livre ┈` centralizado
3. Gaps < 30 minutos não exibem indicador (só espaço vazio)
4. Cor do indicador: Overlay0 #6C7086
5. Proporcionalidade mantida: gap de 1h = 2 linhas (indicador na primeira)

**Testes:**

- `test_br_tui_003_r17_gap_30min_shows_indicator`
- `test_br_tui_003_r17_gap_under_30min_no_indicator`
- `test_br_tui_003_r17_indicator_centered`
- `test_br_tui_003_r17_indicator_color_overlay0`

---

### BR-TUI-003-R18: Effort Bar nos Hábitos

**Descrição:** Cada hábito exibe barra de esforço proporcional ao tempo real dedicado versus planejado. Fórmula: `filled = round((actual / planned) * 5)`, clamp [0, 7].

**Regras:**

1. Base: 5 dots. Overflow: até 7 dots (+40% max)
2. Dot cheio: `●`, cor do status
3. Dot vazio: `·`, Overlay0 #6C7086
4. Not_done (qualquer substatus): `─────`, cor do status
5. Pending (sem registro): `·····`, Overlay0
6. Largura fixa: 5 chars (base) + até 2 chars (overflow)

**Testes:**

- `test_br_tui_003_r18_100_percent_5_dots`
- `test_br_tui_003_r18_80_percent_4_dots`
- `test_br_tui_003_r18_overflow_120_percent_6_dots`
- `test_br_tui_003_r18_max_overflow_7_dots`
- `test_br_tui_003_r18_not_done_dashes`
- `test_br_tui_003_r18_pending_empty_dots`

---

### BR-TUI-003-R19: Ordenação dos Hábitos

**Descrição:** Hábitos no card são ordenados cronologicamente pelo horário de início planejado.

**Regras:**

1. Ordenação: ascendente por `start_time` do hábito
2. Hábitos sem horário definido ficam no final
3. Hábito com status running é sempre visível (auto-scroll se necessário)
4. Empate em horário: ordem alfabética por nome

**Testes:**

- `test_br_tui_003_r19_sorted_by_start_time`
- `test_br_tui_003_r19_no_time_at_end`
- `test_br_tui_003_r19_running_always_visible`

---

### BR-TUI-003-R20: Ordenação das Tarefas

**Descrição:** Tarefas no card são ordenadas por urgência, com concluídas e canceladas agrupadas no final.

**Regras:**

1. Grupo 1 (topo): overdue, ordenado por data ascendente (mais atrasada primeiro)
2. Grupo 2: pendentes, ordenado por proximidade ascendente (mais próxima primeiro)
3. Grupo 3 (final): done, ordenado por data de conclusão descendente
4. Grupo 4 (final): cancelled, ordenado por data descendente

**Testes:**

- `test_br_tui_003_r20_overdue_first`
- `test_br_tui_003_r20_pending_by_proximity`
- `test_br_tui_003_r20_done_after_pending`
- `test_br_tui_003_r20_cancelled_last`

### BR-TUI-003-R21: Overflow nos Cards

**Descrição:** Quando itens excedem o viewport do card, um indicador `+N ▼` é exibido no rodapé interno. Alias de BR-TUI-003-R12 para rastreabilidade com o spec original.

**Regras:** Ver BR-TUI-003-R12 (Viewport-Aware Truncation).

**Testes:** Mesmos de BR-TUI-003-R12.

---

---

### BR-TUI-003-R22: Strikethrough em Done/Cancelled

**Descrição:** Tarefas concluídas e canceladas exibem nome com strikethrough via Rich markup `[strike]nome[/strike]`.

**Regras:**

1. Strikethrough aplicado apenas ao campo nome (c1)
2. Aplica-se a: status done (qualquer substatus) e cancelled
3. Cor do nome mantém a cor do status (Green para done, Overlay0 para cancelled)
4. Demais colunas sem strikethrough

**Testes:**

- `test_br_tui_003_r22_done_task_strikethrough`
- `test_br_tui_003_r22_cancelled_task_strikethrough`
- `test_br_tui_003_r22_pending_no_strikethrough`
- `test_br_tui_003_r22_only_name_column`

---

### BR-TUI-003-R23: Subtítulo do Card Tarefas

**Descrição:** O border_title do card Tarefas exibe contadores por status com cores semânticas. Contadores com valor 0 são omitidos.

**Formato:** `N pend. N done N canc. N over.`

**Cores:** pend.=Text #CDD6F4, done=Green #A6E3A1, canc.=Overlay0 #6C7086, over.=Red #F38BA8

**Regras:**

1. Contadores com valor 0 são omitidos
2. Overdue = tarefa pendente com data no passado
3. Atualiza após cada quick action e on_focus

**Testes:**

- `test_br_tui_003_r23_shows_pending_count`
- `test_br_tui_003_r23_shows_overdue_count`
- `test_br_tui_003_r23_omits_zero_counters`
- `test_br_tui_003_r23_correct_colors`

---

### BR-TUI-003-R24: Períodos da Agenda

**Descrição:** A agenda agrupa blocos em 3 períodos fixos com separadores visuais: Manhã (06:00-12:00), Tarde (12:00-18:00), Noite (18:00-23:00). Cada período exibe header com nome, rotina associada e progresso X/Y.

**Separador:** `── Manhã ─── Rotina Matinal ──── 3/4 ──────`

**Regras:**

1. Períodos fixos: Manhã (06:00-12:00), Tarde (12:00-18:00), Noite (18:00-23:00)
2. Períodos sem eventos são ocultos (não renderizam separador)
3. Separador exibe: nome do período + rotina associada + progresso X/Y
4. X = eventos done + running no período. Y = total de eventos no período
5. Cor do progresso: Green (>= 80%), Yellow (50-79%), Red (< 50%)
6. Cor do nome do período e traços: Subtext0 #A6ADC8
7. Cor do nome da rotina: Text #CDD6F4
8. Se nenhuma rotina associada ao período: "[Sem rotina]" em Overlay0
9. Na v1.7, períodos são fixos. Customização em v1.8+ (SettingsScreen)

**Testes:**

- `test_br_tui_003_r24_three_periods`
- `test_br_tui_003_r24_empty_period_hidden`
- `test_br_tui_003_r24_separator_shows_routine_name`
- `test_br_tui_003_r24_separator_shows_progress`
- `test_br_tui_003_r24_progress_color_by_threshold`
- `test_br_tui_003_r24_no_routine_shows_placeholder`

---

### BR-TUI-003-R25: Timer Card Compacto

**Descrição:** O card Timer no dashboard ocupa 2 linhas de conteúdo (sem ASCII art). ASCII art fica exclusivamente na TimerScreen dedicada.

**Regras:**

1. Card ocupa 4 linhas totais (borda + 2 conteúdo + borda)
2. Sem ASCII art no dashboard
3. Estado running: ícone ▶ + nome + sessão X/Y + elapsed (Mauve #CBA6F7, 1s update)
4. Estado paused: ícone ⏸ + nome + sessão X/Y + elapsed piscando (Yellow #F9E2AF)
5. Estado idle: última sessão (nome + duração + hora) + resumo do dia
6. Border_title direita: `▶ ativo` (Mauve) / `⏸ paused` (Yellow) / `⏹ idle` (Overlay0)
7. Linha 2 sempre: resumo do dia `Hoje: N sessões · XhYYm total`

**Testes:**

- `test_br_tui_003_r25_running_shows_elapsed`
- `test_br_tui_003_r25_running_session_count`
- `test_br_tui_003_r25_paused_shows_yellow`
- `test_br_tui_003_r25_idle_shows_last_session`
- `test_br_tui_003_r25_idle_shows_day_summary`
- `test_br_tui_003_r25_no_ascii_art`
- `test_br_tui_003_r25_border_title_reflects_state`

---

### BR-TUI-003-R26: Cores Temporais na Régua

**Descrição:** Os horários na régua da agenda usam cores que indicam contexto temporal.

**Regras:**

1. Horários passados: Subtext0 #A6ADC8 (dim)
2. Horário atual: Mauve #CBA6F7, bold
3. Horários futuros: Text #CDD6F4 (normal)
4. "Atual" = slot de 30min que contém datetime.now()
5. Atualização: a cada 30 minutos (quando slot muda)

**Testes:**

- `test_br_tui_003_r26_past_hours_subtext0`
- `test_br_tui_003_r26_current_hour_mauve_bold`
- `test_br_tui_003_r26_future_hours_text`

---

### BR-TUI-003-R27: Herança de Cor por Status

**Descrição:** Em todos os cards, o campo nome herda a cor do status do item. Mapeamento definido em `color-system.md` (SSOT para cores).

**Mapeamento:** done/full=Green #A6E3A1, done/partial=Rosewater #F5E0DC, done/overdone=Flamingo #F2CDCD, done/excessive=Peach #FAB387, not_done/justified=Yellow #F9E2AF, not_done/unjustified=Red #F38BA8, not_done/ignored=Maroon #EBA0AC, running=Mauve #CBA6F7, paused=Yellow #F9E2AF, pending=Overlay0 #6C7086, cancelled=Overlay0 #6C7086

**Regras:**

1. Campo nome em todos os cards herda cor do status/substatus
2. Nome bold se running ou paused
3. Nome strikethrough se done ou cancelled (apenas tarefas, ver R22)
4. Aplicável a: card Agenda, card Hábitos, card Tarefas

**Testes:**

- `test_br_tui_003_r27_done_name_green`
- `test_br_tui_003_r27_running_name_mauve_bold`
- `test_br_tui_003_r27_pending_name_overlay0`
- `test_br_tui_003_r27_not_done_unjustified_name_red`

---

### BR-TUI-003-R28: Mock Data como Fixture

**Descrição:** Dados de demonstração não são fallback do dashboard. Mock data existe apenas em fixtures de teste e no comando `atomvs demo`. Dashboard com banco vazio exibe estado vazio com orientação ao usuário.

**Regras:**

1. Dashboard com banco vazio exibe mensagem de orientação por card
2. Mock data hardcoded removido do `dashboard.py`
3. Mock data migrado para `tests/unit/test_tui/conftest.py` como fixtures
4. Comando `atomvs demo` cria rotina demo no banco (feature separada)
5. Mensagem de orientação indica ação concreta (keybinding ou comando CLI)
6. Cor da mensagem: Subtext0 #A6ADC8
7. Texto centralizado verticalmente no card

**Testes:**

- `test_br_tui_003_r28_empty_db_shows_orientation`
- `test_br_tui_003_r28_habits_empty_message`
- `test_br_tui_003_r28_tasks_empty_message`
- `test_br_tui_003_r28_timer_empty_message`
- `test_br_tui_003_r28_no_hardcoded_mock_data`

---

### BR-TUI-008: Visual Consistency (Material-like)

**Descrição:** A TUI segue design system Material-like com paleta de cores definida, cards com bordas, spacing consistente, hierarquia visual clara e layout responsivo com três breakpoints.

**Regras:**

1. Paleta definida em theme.tcss (single source of truth para cores)
2. Cards: borda arredondada, padding 1x2, margin 1
3. Status colors: verde/`$success` (done), amarelo/`$warning` (pending/skipped), vermelho/`$error` (missed/overdue), purple/`$primary-light` (running)
4. Texto primário: alto contraste sobre superfície (`$on-surface` sobre `$surface`)
5. Texto secundário: cor `$muted` para labels e metadados
6. Sidebar: largura fixa 22 caracteres, fundo `$surface-alt`
7. Tipografia: bold para títulos, normal para conteúdo, dim para metadados
8. Breakpoint completo (≥ 120 colunas): layout 3 colunas (sidebar + agenda + cards), timeline vertical completa, todos os cards visíveis, métricas com histórico semanal + dot matrix
9. Breakpoint compacto (80–119 colunas): agenda com menos horas visíveis, cards com conteúdo truncado (nomes até 10 chars), métricas reduzidas (3 dias de histórico)
10. Breakpoint minimal (< 80 colunas): layout 1 coluna (cards empilhados verticalmente), agenda oculta (substituída por barra de progresso simples no header), métricas apenas streak + completude 7d
11. Barras de progresso seguem esquema de cores por faixa: verde (`$success`) para ≥ 80%, amarelo (`$warning`) para 50–79%, vermelho (`$error`) para < 50%
12. Indicadores ASCII consistentes em toda a TUI: ✓ (done), ✗ (skip), ! (alta/missed), ▪ (média), · (baixa/pending), ▶ (running), ◼ (sparkline esforço)

**Paleta de referência:**

| Variável TCSS    | Cor     | Uso                         |
| ---------------- | ------- | --------------------------- |
| `$primary`       | #7C4DFF | Bordas, elementos de ênfase |
| `$primary-light` | #B388FF | Timer running, destaques    |
| `$surface`       | #1E1E2E | Fundo principal             |
| `$surface-alt`   | #2A2A3E | Cards, sidebar, elevação    |
| `$on-surface`    | #CDD6F4 | Texto principal             |
| `$success`       | #A6E3A1 | Done, concluído             |
| `$warning`       | #F9E2AF | Pending, skipped            |
| `$error`         | #F38BA8 | Missed, overdue, alta       |
| `$muted`         | #6C7086 | Labels, metadados, vazio    |

**Testes:**

- `test_br_tui_008_theme_file_exists`
- `test_br_tui_008_cards_have_consistent_style`
- `test_br_tui_008_status_colors_applied`
- `test_br_tui_008_progress_bar_color_thresholds`
- `test_br_tui_008_responsive_breakpoint_compact`
- `test_br_tui_008_responsive_breakpoint_minimal`
- `test_br_tui_008_ascii_indicators_consistent`

---

### BR-TUI-009: Service Layer Sharing

**Descrição:** A TUI consome os mesmos services que a CLI. Nenhuma lógica de negócio é duplicada na camada TUI. A TUI é exclusivamente UI: captura input, chama service, exibe resultado.

**Regras:**

1. TUI importa de `timeblock.services` (mesmo pacote que CLI)
2. TUI NUNCA acessa models/ORM diretamente (sempre via service)
3. Session criada por operação (session-per-action pattern)
4. Erros de service propagados e exibidos como notificação
5. Validações de negócio permanecem nos services (não na TUI)

**Testes:**

- `test_br_tui_009_uses_routine_service`
- `test_br_tui_009_uses_habit_service`
- `test_br_tui_009_uses_task_service`
- `test_br_tui_009_uses_timer_service`
- `test_br_tui_009_no_direct_model_access`

---

### BR-TUI-010: Habit Instance Actions

**Descrição:** A tela de Hábitos permite marcar instâncias como done ou skip com substatus, integrando com BR-HABITINSTANCE-001 e BR-SKIP-001.

**Regras:**

1. Lista instâncias do dia agrupadas por hábito
2. `enter` em instância pendente → Menu de ação (Done/Skip)
3. Done solicita duração real (minutos) para cálculo de substatus
4. Skip solicita categoria (SkipReason) e justificativa opcional
5. Instâncias já finalizadas (done/not_done) exibem status com cor
6. Substatus calculado automaticamente pelo HabitInstanceService (BR-HABITINSTANCE-002/003)

**Testes:**

- `test_br_tui_010_lists_today_instances`
- `test_br_tui_010_mark_done_asks_duration`
- `test_br_tui_010_mark_skip_asks_reason`
- `test_br_tui_010_shows_substatus_color`
- `test_br_tui_010_completed_instances_readonly`

### BR-TUI-011: Routines Screen

**Descrição:** A tela de Rotinas exibe a semana completa em formato de grade temporal (estilo Google Calendar weekly view), representando o plano ideal do usuário. Enquanto o Dashboard mostra o dia real com status de execução, a tela de Rotinas mostra a intenção: os templates de hábitos distribuídos na semana conforme sua recorrência. A grade permite visualizar, criar, editar e deletar hábitos diretamente no contexto temporal, além de gerenciar múltiplas rotinas.

**Referências:** ADR-031 seção 4, BR-TUI-005 (CRUD pattern), BR-TUI-008 (visual), BR-ROUTINE-001 (single active), BR-HABIT-001/002 (estrutura e recorrência)

**Regras:**

1. **Header Bar:** barra compacta exibe lista horizontal de rotinas com contagem de hábitos por rotina, indicador `▸` e `(ativa)` na rotina ativa, ação `+ Nova rotina` à direita e período da semana exibida (`Sem DD─DD Mês AAAA`). `Tab`/`Shift+Tab` navega entre rotinas no header; a grade atualiza para exibir os hábitos da rotina focada
2. **Grade Semanal:** ocupa toda a largura após a sidebar. 7 colunas (Seg─Dom) distribuídas horizontalmente com largura igual. Régua de horas (06:00─22:00) à esquerda, vertical. Cada hábito posicionado como bloco no dia e horário correspondentes à sua recorrência (BR-HABIT-002)
3. **Rendering de blocos:** cada hora = 2 linhas na grade. Blocos com duração ≤ 30min = 1 linha. Blocos com duração > 30min = múltiplas linhas, label na primeira. Nome truncado conforme largura da coluna. Cada hábito usa preenchimento distinto (████, ▒▒▒▒, ░░░░, ▓▓▓▓) como canal redundante de acessibilidade, combinado com a cor do hábito (`color`) em terminais que suportam
4. **Navegação na grade:** `←`/`→` navega entre dias (colunas), `↑`/`↓` ou `j`/`k` navega entre blocos no mesmo dia (pula para próximo hábito). `[`/`]` alterna semana anterior/próxima. `T` retorna à semana atual
5. **Painel de detalhes:** quando o cursor está sobre um bloco, ele ganha borda `$primary` e um painel lateral fixo exibe: nome, horário início─fim, duração, recorrência, cor, contagem de instâncias (pendentes/concluídas), streak atual e keybindings contextuais (`[e]` editar, `[x]` deletar, `[g]` ver instâncias). Painel atualiza em tempo real conforme o cursor se move
6. **CRUD contextual:** keybindings `n`/`e`/`x` operam sobre rotinas quando o foco está no header, e sobre hábitos quando o foco está na grade. Novo hábito abre formulário modal (título, horário, recorrência, cor). Após criar, o hábito aparece imediatamente na grade nos dias correspondentes. Segue padrões de BR-TUI-005 (confirmação em delete, refresh após operação, erros inline)
7. **Ativação de rotina:** `a` com foco em rotina no header ativa a rotina selecionada (BR-ROUTINE-001: desativa todas as outras). Mudança refletida no header (indicador `▸` move), na status bar e no dashboard
8. **Conflitos:** dois hábitos no mesmo horário/dia renderizam lado a lado na mesma célula, separados por `│`, com borda `$error`. Conflitos são exibidos mas nunca bloqueados (consistente com BR-REORDER-001)
9. **Rotina sem hábitos:** grade vazia com mensagem centralizada "Nenhum hábito nesta rotina. Pressione [n] para criar o primeiro."
10. **Responsividade:** ≥ 120 colunas: 7 dias visíveis simultaneamente, labels completos. 80─119 colunas: 5 dias visíveis (Seg─Sex), Sáb/Dom com scroll horizontal, nomes truncados em 6 chars. < 80 colunas: 3 dias visíveis, scroll horizontal, blocos sem label (apenas preenchimento + cor), painel de detalhes como overlay (ativado com `enter`, fechado com `escape`)
11. **Refresh:** dados atualizados ao entrar na screen (on_focus) e após qualquer operação CRUD. Troca de rotina no header recarrega a grade com os hábitos da rotina focada
12. **Navegação cross-screen:** `g` com bloco selecionado navega para a screen Habits com filtro no hábito selecionado (visão de instâncias). Keybinding de navegação global (`3`/`h`) vai para Habits sem filtro

**Mockup de referência:** `docs/tui/routines-weekly-mockup.md`

**Testes:**

- `test_br_tui_011_header_shows_routines_list`
- `test_br_tui_011_header_shows_active_indicator`
- `test_br_tui_011_header_shows_habit_count`
- `test_br_tui_011_header_shows_week_period`
- `test_br_tui_011_tab_switches_routine_in_header`
- `test_br_tui_011_grade_renders_seven_columns`
- `test_br_tui_011_grade_renders_hour_ruler`
- `test_br_tui_011_grade_places_habit_by_recurrence`
- `test_br_tui_011_grade_block_duration_proportional`
- `test_br_tui_011_grade_block_fill_patterns`
- `test_br_tui_011_grade_block_uses_habit_color`
- `test_br_tui_011_grade_truncates_long_names`
- `test_br_tui_011_navigate_days_left_right`
- `test_br_tui_011_navigate_blocks_up_down`
- `test_br_tui_011_navigate_week_prev_next`
- `test_br_tui_011_navigate_week_today`
- `test_br_tui_011_detail_panel_shows_on_focus`
- `test_br_tui_011_detail_panel_shows_habit_info`
- `test_br_tui_011_detail_panel_shows_instance_stats`
- `test_br_tui_011_detail_panel_shows_streak`
- `test_br_tui_011_detail_panel_updates_on_cursor_move`
- `test_br_tui_011_crud_context_header_operates_routine`
- `test_br_tui_011_crud_context_grade_operates_habit`
- `test_br_tui_011_create_habit_modal`
- `test_br_tui_011_create_habit_appears_in_grade`
- `test_br_tui_011_edit_habit_prefilled`
- `test_br_tui_011_delete_habit_confirmation`
- `test_br_tui_011_activate_routine_updates_indicator`
- `test_br_tui_011_conflict_renders_side_by_side`
- `test_br_tui_011_conflict_uses_error_color`
- `test_br_tui_011_empty_routine_message`
- `test_br_tui_011_responsive_compact_five_days`
- `test_br_tui_011_responsive_minimal_three_days`
- `test_br_tui_011_responsive_minimal_overlay_panel`
- `test_br_tui_011_refreshes_on_focus`
- `test_br_tui_011_refreshes_after_crud`
- `test_br_tui_011_go_to_habits_screen`

---

## Referências

- **ADRs:** `docs/decisions/`
- **Livro:** "Atomic Habits" - James Clear
- **Service Layer:** `src/timeblock/services/`
- **Models:** `src/timeblock/models/`
- **Enums:** `src/timeblock/models/enums.py`

---

**Última atualização em:** 25 de Fevereiro de 2026

**Total de regras:** 81 BRs
