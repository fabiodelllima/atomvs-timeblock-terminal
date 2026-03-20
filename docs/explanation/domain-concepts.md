# Introdução e Fundamentos

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

```plaintext
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

```plaintext
Exercício Matinal:
████████████████░░░░  15/20 dias este mês (75%)
```

**2. Streak Tracking:**

```plaintext
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

```plaintext
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

```plaintext
[ ] Exercício 7:00-8:00

 ↓ (ao completar)

[✓] Exercício 7:00-8:00  ← Dopamina!
```

**2. Relatórios de Progresso:**

```plaintext
SEMANA 1: ███████ 7/7 dias (100%)
SEMANA 2: ██████░ 6/7 dias (86%)
SEMANA 3: ███████ 7/7 dias (100%)
```

**3. Identity Reinforcement:**

Cada instância completada reforça: "Sou o tipo de pessoa que [FAZ ISSO]"

#### Arquitetura Conceitual

```plaintext
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
│           (scheduled)     (tracked)          │
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

```plaintext
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

## Conceitos do Domínio

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

```plaintext
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
