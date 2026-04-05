# Streak

O Streak é a métrica motivacional central do TimeBlock Planner. Ele conta dias consecutivos em que o hábito foi executado (status DONE), e sua simples existência cria um poderoso incentivo psicológico: quanto maior a sequência, maior o custo percebido de quebrá-la. Jerry Seinfeld popularizou esse conceito como "don't break the chain" — marque um X no calendário todo dia, e a corrente de Xs se torna a motivação.

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
