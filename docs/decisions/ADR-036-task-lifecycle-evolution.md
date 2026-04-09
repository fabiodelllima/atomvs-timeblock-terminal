# ADR-036: Evolução do Ciclo de Vida de Tasks

- **Status:** Aceito
- **Data:** 2026-03-14

---

## 1. Contexto

**Contexto técnico:** ADR-036 amenda BR-TASK-001 (estrutura) e BR-TASK-002 (conclusão), evolui BR-TASK-006 (simplicidade mantida com extensões rastreáveis), e introduz BR-TASK-007 a BR-TASK-010.

O modelo `Task` foi projetado como "checkbox com data" (BR-TASK-006), intencionalmente simples para o MVP. O status era derivado de um único campo:

```plaintext
completed_datetime is None      =>  pendente
completed_datetime is not None  =>  concluída
```

Três limitações emergiram com o uso real:

1. **Invisibilidade pós-conclusão.** Tasks concluídas desapareciam do dashboard instantaneamente (DT-018). O `TasksPanel` tem formatação para `completed` e `cancelled` (strikethrough, contadores, ordenação — BR-TUI-003-R20/R22/R23), mas o loader nunca entregava esses dados.

2. **Adiamento sem rastro.** O comando `task edit --datetime` alterava `scheduled_datetime` destrutivamente. Não havia como saber se uma task foi adiada, quantas vezes, nem por quantos dias. A análise posterior de padrões de procrastinação era impossível.

3. **Exclusão como único cancelamento.** `delete_task()` removia o registro permanentemente. Sem soft delete, não havia distinção entre "desisti desta task" e "esta task nunca existiu". Métricas de abandono ficavam irrecuperáveis.

---

## 2. Decisão

Evoluir o modelo `Task` de "checkbox com data" para "entidade com lifecycle rastreável", adicionando três campos ao modelo e derivando status de forma determinística.

### 2.1 Comparativo do Modelo

#### Antes (v1.6.0)

```python
class Task(SQLModel, table=True):
    id: int | None
    title: str
    scheduled_datetime: datetime
    completed_datetime: datetime | None
    description: str | None
    color: str | None
    tag_id: int | None
```

Status derivado: 2 estados (`pending`, `completed`), campo único.

#### Depois (v1.7.0)

```python
class Task(SQLModel, table=True):
    id: int | None
    title: str
    scheduled_datetime: datetime
    original_scheduled_datetime: datetime     # NOVO — imutável, fixado na criação
    completed_datetime: datetime | None
    cancelled_datetime: datetime | None       # NOVO — soft delete
    postponement_count: int = 0               # NOVO — incrementado a cada adiamento
    description: str | None
    color: str | None
    tag_id: int | None
```

Status derivado: 4 estados (`pending`, `overdue`, `completed`, `cancelled`), com metadados de adiamento ortogonais ao status.

### 2.2 Derivação de Status

A derivação é determinística e sem ambiguidade — a ordem de avaliação importa:

```plaintext
1. cancelled_datetime is not None        =>  CANCELLED
2. completed_datetime is not None        =>  COMPLETED
3. scheduled_datetime < now()            =>  OVERDUE
4. else                                  =>  PENDING
```

Cancelamento tem precedência sobre conclusão (cenário: task concluída e depois cancelada por engano — o cancel prevalece como última ação).

### 2.3 Metadados de Adiamento

Adiamento é ortogonal ao status: uma task pode ser `PENDING`, `OVERDUE`, ou `COMPLETED` e ainda assim ter histórico de adiamentos.

```plaintext
was_postponed     = postponement_count > 0
days_postponed    = (scheduled_datetime - original_scheduled_datetime).days
```

Para tasks `COMPLETED`, métricas adicionais:

```plaintext
time_to_completion = completed_datetime - original_scheduled_datetime
completed_on_time  = completed_datetime.date() <= original_scheduled_datetime.date()
days_late          = max(0, (completed_datetime.date() - original_scheduled_datetime.date()).days)
```

### 2.4 Impacto em Operações Existentes

| Operação               | Antes                            | Depois                                                                                    |
| ---------------------- | -------------------------------- | ----------------------------------------------------------------------------------------- |
| `task add`             | Cria com `scheduled_datetime`    | Cria com `scheduled_datetime` e `original_scheduled_datetime` (mesmo valor)               |
| `task edit --datetime` | Sobrescreve `scheduled_datetime` | Sobrescreve `scheduled_datetime`, incrementa `postponement_count` se nova data > anterior |
| `task complete`        | Seta `completed_datetime`        | Sem mudança                                                                               |
| `task delete`          | Remove do banco (hard delete)    | Seta `cancelled_datetime` (soft delete)                                                   |
| `load_tasks()`         | Retorna apenas pendentes         | Retorna pendentes + overdue + concluídas (últimas 24h) + canceladas (últimas 24h)         |

---

## 3. Justificativa

### 3.1 Por que não um enum `TaskStatus`?

O HabitInstance usa `Status` enum (PENDING/DONE/NOT_DONE) com substatus. Para Tasks, a derivação a partir de datetimes é preferível porque:

- **Auditabilidade.** Os timestamps são fatos imutáveis; um enum é uma interpretação que pode divergir dos dados.
- **Consistência com BR-TASK-002.** A convenção `completed_datetime` como fonte de verdade já estava estabelecida. Estendê-la para `cancelled_datetime` e `original_scheduled_datetime` mantém o mesmo padrão.
- **Métricas nativas.** Com timestamps, as métricas (tempo até conclusão, dias de adiamento) são cálculos diretos, sem precisar de campos adicionais.

### 3.2 Por que `postponement_count` se já temos o delta?

O delta `scheduled - original` captura o adiamento total, mas não distingue "adiou uma vez por 7 dias" de "adiou 7 vezes por 1 dia". O `postponement_count` complementa o delta para análise de padrões comportamentais — adiamentos frequentes de poucos dias indicam um padrão diferente de um único adiamento longo.

### 3.3 Por que soft delete e não status enum para cancelamento?

Mesma filosofia dos demais campos: `cancelled_datetime` é um fato (quando foi cancelada), não uma classificação. Permite reverter cancelamento (nullificar o campo) e fornece timestamp para métricas sem campo adicional.

---

## 4. Migração

- **Estratégia:** Alembic migration adicionando os 3 campos com defaults compatíveis.
- **`original_scheduled_datetime`:** Populado com valor de `scheduled_datetime` para tasks existentes.
- **`cancelled_datetime`:** Default `None` (nenhuma task existente é cancelada).
- **`postponement_count`:** Default `0` (sem histórico retroativo — dados anteriores são irrecuperáveis).
- **Backward compatibility:** Nenhum campo existente muda de semântica. Código que só lê `completed_datetime` continua funcionando.

---

## 5. Consequências

### Positivas

- Dashboard pode mostrar tasks concluídas e canceladas recentes (DT-018 resolvido)
- Métricas de produtividade: tempo médio até conclusão, taxa de adiamento, padrões semanais
- Base de dados para o futuro MetricsPanel (DT-017)
- Análise de procrastinação: tasks mais adiadas, correlação com tags/horários

### Negativas

- BR-TASK-006 (simplicidade) é relaxada — Tasks ganham complexidade incremental
- Migração de banco necessária para dados existentes
- `task delete` muda de semântica (soft delete) — necessário `task purge` para hard delete futuro

### Neutras

- Tamanho da tabela cresce marginalmente (3 campos, sem índices novos no MVP)
- Sem impacto em performance para o volume esperado (<1000 tasks)

---

## 6. Referências

- BR-TASK-001 a BR-TASK-006 (domínio Task original)
- BR-TUI-003-R20/R22/R23 (formatação de status no TasksPanel)
- DT-018 (load_tasks omite completed/cancelled)
- DT-017 (MetricsPanel stub)
- CLEAR, James. _Atomic Habits_. Avery, 2018. Cap. 16: "How to make good habits inevitable and bad habits impossible."
