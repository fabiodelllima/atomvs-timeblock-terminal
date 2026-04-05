# Validações Globais

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
