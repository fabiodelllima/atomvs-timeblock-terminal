# Refactoring Catalog — Sprint 4

**Versão:** 1.0.0

**Status:** Planejado

**Referência principal:** FOWLER, M. _Refactoring: Improving the Design of Existing Code_. 2nd ed. Boston: Addison-Wesley, 2018.

**Referências complementares:** FOWLER, M. _Patterns of Enterprise Application Architecture_. Boston: Addison-Wesley, 2002. HUMBLE, J.; FARLEY, D. _Continuous Delivery_. Boston: Addison-Wesley, 2010.

---

## Princípio Orientador

Fowler (2018, p. 45) define refactoring como "a change made to the internal structure of software to make it easier to understand and cheaper to modify without changing its observable behavior." As refatorações catalogadas aqui são aplicadas incrementalmente durante a Sprint 4 — cada arquivo tocado para implementar CRUD passa pela refatoração correspondente antes do commit. Nenhuma refatoração é executada em isolamento sem entrega de valor funcional.

Humble e Farley (2010, p. 185) estabelecem que refatorações devem manter o commit stage abaixo de 10 minutos. Cada item abaixo é dimensionado para caber em um commit atômico sem impactar o pipeline.

---

## RF-001: Extract Delegate — Quick Actions do HabitsPanel

**Catálogo Fowler:** Extract Class (p. 182), Move Function (p. 196)

**Diagnóstico:** `HabitsPanel._action_done()` e `_action_skip()` (linhas 54-84) importam services dentro do método e chamam `service_action()` diretamente. O widget de apresentação conhece `HabitInstanceService`, violando BR-TUI-009 (Service Layer Sharing) e o princípio de que widgets renderizam, o coordinator orquestra (R1 do handoff).

O mesmo padrão se repete em `TasksPanel._action_complete()` (linhas 53-64).

**Evidência no código:**

```python
# habits_panel.py, linhas 59-60 — import lazy dentro do método
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.tui.session import service_action
```

**Ação:** Mover lógica de quick actions para o DashboardScreen. Panels emitem mensagem Textual (`self.post_message(HabitDoneRequest(item_id))`), DashboardScreen escuta e executa a operação via service. O mesmo padrão serve para CRUD: panels emitem intenção, coordinator executa.

**Impacto:** HabitsPanel e TasksPanel perdem dependência direta de services. Testes unitários de widgets não precisam mockar banco. Consistente com R2 (HUMBLE; FARLEY, 2010, p. 180-183).

**Quando aplicar:** Sprint 4a/4b, ao implementar CRUD no dashboard. Refatorar quick actions existentes junto com a adição de `n`/`e`/`x`.

**Testes afetados:** `test_habit_actions.py` — adaptar para verificar emissão de mensagem em vez de chamada direta ao service.

---

## RF-002: Extract Variable / Replace Magic Literal — Constante C_HIGHLIGHT duplicada

**Catálogo Fowler:** Extract Variable (p. 119), Remove Duplicate Code (p. 78)

**Diagnóstico:** `C_HIGHLIGHT = "#313244"` definida identicamente em `habits_panel.py:21` e `tasks_panel.py:21`. Magic literal repetido — viola DRY e dificulta mudança de tema.

**Evidência no código:**

```plaintext
habits_panel.py:21:C_HIGHLIGHT = "#313244"  # Surface0
tasks_panel.py:21:C_HIGHLIGHT = "#313244"   # Surface0
```

**Ação:** Mover para `colors.py` (já é o módulo SSOT para cores) como constante exportada. Atualizar imports nos dois panels.

**Impacto:** Mudança de cor do cursor em um único lugar. Consistente com D-005 (constantes pendente no technical-debt.md).

**Quando aplicar:** Sprint 4a, primeiro commit antes de tocar os panels.

**Testes afetados:** Nenhum — mudança puramente estrutural.

---

## RF-003: Split Phase — Data Loading no DashboardScreen

**Catálogo Fowler:** Split Phase (p. 154), Extract Function (p. 106)

**Diagnóstico:** `DashboardScreen._load_instances()` (linhas 88-128) mistura três responsabilidades: abrir sessão, executar query, transformar resultado em dict. O método tem 40 linhas e 3 níveis de indentação. O mesmo padrão se repete em `_load_tasks()` e `_get_active_timer()`.

Fowler (2018, p. 154): "When I run into code that's dealing with two different things, I look for a way to split it into separate modules."

**Evidência no código:**

```python
# dashboard.py, linhas 88-128 — load + transform misturados
@staticmethod
def _load_instances() -> list[dict]:
    try:
        today = date.today()
        result, error = service_action(
            lambda s: HabitInstanceService().list_instances(...)
        )
        # ... 20 linhas de transformação model → dict
```

**Ação:** Separar em duas fases: (1) `_fetch_instances()` retorna objetos do service; (2) `_transform_instance(inst) -> dict` converte para formato do panel. A fase de transformação fica testável em isolamento, sem banco.

**Impacto:** Testes unitários do dashboard podem testar transformação com objetos mock, sem `service_action`. Reduz complexidade ciclomática do método.

**Quando aplicar:** Sprint 4b, ao adicionar CRUD de rotinas que precisa de `refresh_data()`.

**Testes afetados:** `test_dashboard_helpers.py` — adicionar testes para `_transform_instance()` isoladamente.

---

## RF-004: Remove Dead Code — @staticmethod duplicado

**Catálogo Fowler:** Remove Dead Code (p. 237)

**Diagnóstico:** `dashboard.py` linhas 155-156 contém `@staticmethod` duplicado antes de `_get_active_timer`. Erro de merge ou edição.

**Evidência no código:**

```python
# dashboard.py, linhas 155-156
@staticmethod
@staticmethod
def _get_active_timer() -> dict | None:
```

**Ação:** Remover o `@staticmethod` duplicado.

**Impacto:** Zero risco. Correção trivial.

**Quando aplicar:** Sprint 4.0, primeiro commit da branch.

**Testes afetados:** Nenhum.

---

## RF-005: Introduce Parameter Object — Dados de instância como dict

**Catálogo Fowler:** Introduce Parameter Object (p. 140), Replace Primitive with Object (p. 174)

**Diagnóstico:** Instâncias são passadas entre DashboardScreen e panels como `list[dict]` com chaves string (`"id"`, `"name"`, `"status"`, `"substatus"`, `"start_hour"`, `"end_hour"`, `"actual_minutes"`). Erros de chave são silenciosos (`.get()` retorna None). Não há validação de schema nem autocomplete no IDE.

Fowler (2018, p. 140): "I see groups of data items that regularly travel together, appearing in function after function. Such a group is a data clump, and I can usually replace it with a single data structure."

**Evidência no código:**

```python
# habits_panel.py, _format_instance — acessa 7 chaves sem type safety
name = inst["name"][:16]
st = inst["status"]
sub = inst.get("substatus")
actual = inst.get("actual_minutes")
sh = inst.get("start_hour", 0)
eh = inst.get("end_hour", 0)
```

**Ação:** Criar `@dataclass` ou `TypedDict` em `tui/models.py` (não confundir com `models/` do ORM). Ex: `HabitInstanceView`, `TaskView`, `TimerView`. DashboardScreen produz esses objetos na fase de transformação (RF-003). Panels recebem objetos tipados.

**Impacto:** Type safety end-to-end na TUI. IDE autocomplete. Erros de chave viram erros de compilação (mypy). Fowler (2018, p. 174): "That way I can move behavior into the new object."

**Quando aplicar:** Sprint 4b/4c, junto com RF-003 (Split Phase). A transformação já produz o dataclass em vez do dict.

**Testes afetados:** Todos os testes de panels que criam dicts manualmente — atualizar para usar dataclass.

---

## RF-006: Replace Conditional with Polymorphism — Format por status

**Catálogo Fowler:** Replace Conditional with Polymorphism (p. 272)

**Diagnóstico:** `TasksPanel._format_task()` (linhas 105-114) despacha por status com cadeia if/elif para 4 métodos diferentes. `HabitsPanel._build_bar()` (linhas 152-172) tem cadeia similar para 4 status. A cada novo status, ambos precisam de mais branches.

Fowler (2018, p. 272): "I find I can clarify such code by replacing the conditional with polymorphism."

**Avaliação:** Para a Sprint 4, a cadeia é pequena (4 branches) e estável — os status não vão mudar. Polimorfismo aqui seria over-engineering. O custo de manter 4 if/elif é menor que o custo de uma hierarquia de classes.

**Ação:** **Não aplicar agora.** Registrar como candidato para revisão na Sprint 6 (BR-TUI-015 Code Quality Audit). Se durante Sprint 4 os branches crescerem, reavaliar.

**Quando aplicar:** Sprint 6 ou se branches ultrapassarem 6.

---

## RF-007: Parameterize Function — Empty state nos panels

**Catálogo Fowler:** Parameterize Function (p. 310)

**Diagnóstico:** `HabitsPanel._build_lines()` (linhas 106-111) e `TasksPanel._build_lines()` (linhas 92-96) têm blocos quase idênticos para estado vazio — 3-4 linhas de placeholder com texto diferente.

**Evidência no código:**

```python
# habits_panel.py
lines.append("  [dim]---              · --:-- · --min[/dim]")
lines.append("  [dim]---              · --:-- · --min[/dim]")
lines.append("  [dim]---              · --:-- · --min[/dim]")
lines.append("  [dim]Crie uma rotina: atomvs routine add[/dim]")

# tasks_panel.py
lines.append("  [dim]---                --/--   --:--[/dim]")
lines.append("  [dim]---                --/--   --:--[/dim]")
lines.append("  [dim]Crie uma task: atomvs task add[/dim]")
```

**Ação:** Extrair método `_build_empty_state(placeholder: str, hint: str, count: int = 3) -> list[str]` em `FocusablePanel` (classe base). Panels chamam `self._build_empty_state("---  · --:-- · --min", "Crie uma rotina: n criar")`.

**Impacto:** Com BR-TUI-013 (placeholders editáveis) na Sprint 4e, o empty state ganha comportamento (Enter abre form). Centralizar agora facilita essa implementação.

**Quando aplicar:** Sprint 4e, junto com BR-TUI-013.

**Testes afetados:** Testes de empty state dos panels — apontar para método base.

---

## RF-008: Consolidate Conditional Expression — Status counting

**Catálogo Fowler:** Consolidate Conditional Expression (p. 263)

**Diagnóstico:** `TasksPanel._refresh_content()` (linhas 71-87) faz 4 list comprehensions separadas para contar tasks por status. `HabitsPanel._refresh_content()` (linhas 86-98) faz sum() com generator para contar done.

**Evidência no código:**

```python
# tasks_panel.py — 4 comprehensions separadas
pending = [t for t in tasks if t.get("status") == "pending"]
completed = [t for t in tasks if t.get("status") == "completed"]
cancelled = [t for t in tasks if t.get("status") == "cancelled"]
overdue = [t for t in tasks if t.get("status") == "overdue"]
```

**Ação:** Consolidar em `Counter` ou single-pass: `counts = Counter(t.get("status") for t in tasks)`. Reduz 4 iterações para 1.

**Impacto:** Micro-otimização, mas melhora legibilidade. Aplica-se durante o toque normal no arquivo.

**Quando aplicar:** Sprint 4d, ao tocar `_refresh_content()` para CRUD tasks.

**Testes afetados:** Nenhum — comportamento idêntico.

---

## RF-009: Encapsulate Variable — Service imports lazy nos widgets

**Catálogo Fowler:** Encapsulate Variable (p. 132)

**Diagnóstico:** Quick actions em `HabitsPanel` e `TasksPanel` fazem imports lazy dentro dos métodos (linhas 59-60, 75-76 do habits_panel; linhas 58-59 do tasks_panel). Isso é um workaround para evitar circular imports, mas esconde dependências.

Fowler (2018, p. 132): "Data is more awkward to manipulate than functions... If I move data around, I have to change all the references to the data in a single cycle."

**Ação:** Resolvido automaticamente por RF-001 (Extract Delegate). Quando quick actions migrarem para o DashboardScreen, os imports lazy nos widgets desaparecem. O DashboardScreen já importa todos os services no top-level.

**Quando aplicar:** Junto com RF-001.

---

## RF-010: Separate Query from Modifier — timer_service.py

**Catálogo Fowler:** Separate Query from Modifier (p. 306)

**Diagnóstico:** `timer_service.py` tem 535 linhas — acima do threshold CRITICAL de 500 (BR-TUI-015). Métodos como `stop_timer()` (linhas 138-226, ~88 linhas) fazem query + validação + mutação + cálculo de substatus + commit em sequência monolítica.

Fowler (2018, p. 306): "It is a good idea to clearly signal the difference between functions with side effects and those without."

**Avaliação:** Este service não é tocado na Sprint 4 (CRUD é sobre rotinas, hábitos e tarefas). Refatorar agora seria escopo creep.

**Ação:** **Não aplicar agora.** Registrar em technical-debt.md como DT-009. Aplicar na Sprint 5 (Timer) quando o service for modificado para timer live.

**Quando aplicar:** Sprint 5.

---

## Matriz de Aplicação por Sprint

| ID     | Refatoração                       | Fowler (2018)                      | Sprint       | Prioridade |
| ------ | --------------------------------- | ---------------------------------- | ------------ | ---------- |
| RF-004 | Remove @staticmethod duplicado    | Remove Dead Code, p. 237           | 4.0          | Trivial    |
| RF-002 | C_HIGHLIGHT para colors.py        | Extract Variable, p. 119           | 4a           | Baixa      |
| RF-001 | Quick actions → coordinator       | Extract Class, p. 182              | 4b           | Alta       |
| RF-003 | Split load/transform no dashboard | Split Phase, p. 154                | 4b           | Alta       |
| RF-005 | Dict → dataclass nos panels       | Introduce Parameter Object, p. 140 | 4b-4c        | Média      |
| RF-008 | Counter em \_refresh_content      | Consolidate Conditional, p. 263    | 4d           | Baixa      |
| RF-007 | Empty state centralizado          | Parameterize Function, p. 310      | 4e           | Média      |
| RF-009 | Imports lazy eliminados           | Encapsulate Variable, p. 132       | (via RF-001) | —          |
| RF-006 | Polimorfismo por status           | Replace Conditional, p. 272        | Sprint 6     | Adiada     |
| RF-010 | timer_service.py split            | Separate Query/Modifier, p. 306    | Sprint 5     | Adiada     |

---

## Referências

FOWLER, M. _Refactoring: Improving the Design of Existing Code_. 2nd ed. Boston: Addison-Wesley, 2018. ISBN 978-0-13-475759-9.

FOWLER, M. _Patterns of Enterprise Application Architecture_. Boston: Addison-Wesley, 2002. ISBN 0-321-12742-0.

HUMBLE, J.; FARLEY, D. _Continuous Delivery_. Boston: Addison-Wesley, 2010. ISBN 978-0-321-60191-9.

---

**Última atualização:** 05 de Março de 2026
