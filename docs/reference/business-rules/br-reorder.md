# Event Reordering

O Event Reordering trata do problema mais frequente no uso diário de time blocking: o que acontece quando a realidade diverge do plano. Um hábito atrasou quinze minutos, uma reunião invadiu o horário da leitura, o almoço se estendeu. Em um sistema rígido, esses desvios gerariam erros ou bloqueios. O TimeBlock Planner adota a abordagem oposta: conflitos são permitidos, detectados, apresentados e — crucialmente — nunca resolvidos automaticamente.

Essa filosofia reflete o princípio de Controle do Usuário: o sistema informa, o usuário decide. Quando dois eventos ocupam o mesmo intervalo de tempo, o sistema detecta a sobreposição e a apresenta visualmente (blocos lado a lado na timeline, borda vermelha), mas não move nenhum evento. Não sugere novos horários. Não aplica regras de prioridade. A razão é simples: o sistema não tem informação suficiente para tomar essa decisão. Só o usuário sabe se a reunião que invadiu o horário de leitura é mais importante que a leitura, ou se prefere encurtar ambas, ou se vai compensar no dia seguinte.

Conflitos são calculados dinamicamente por comparação temporal entre eventos, não armazenados como entidade separada. Isso garante que, ao ajustar o horário de uma instância, os conflitos se recalculam automaticamente. O algoritmo de sugestão de reordenamento automático (Simple Cascade) está planejado para v2.0, mas seguirá o mesmo princípio: o sistema _sugerirá_, nunca _imporá_.

### BR-REORDER-001: Definição de Conflito

**Descrição:** Conflito ocorre quando dois eventos tem sobreposição temporal no mesmo dia.

**Detecção:**

```plaintext
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

```plaintext
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
