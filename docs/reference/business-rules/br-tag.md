# Tag

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

```plaintext
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
