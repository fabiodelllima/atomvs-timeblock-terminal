# Sobreposição e Renderização de Blocos na Agenda

- **Versão:** 1.0.0
- **Status:** Proposto
- **Decisão arquitetural:** ADR-041
- **Business rules:** BR-TUI-032 (renderização), BR-TUI-031 (scroll H), BR-TUI-030 (paginação)

---

## 1. O Problema

A Agenda Panel exibe blocos de tempo que representam instâncias de hábitos ao longo do dia. Quando dois ou mais blocos ocupam o mesmo intervalo de tempo — um hábito de leitura das 10:00 às 11:30 e um exercício das 10:30 às 12:00, por exemplo — eles se sobrepõem. O sistema precisa resolver três questões distintas: onde posicionar cada bloco lateralmente (atribuição de colunas), como agrupar blocos que compartilham espaço (grupos de sobreposição), e como desenhar cada célula da grade resultante (renderização).

Essas três fases são independentes entre si. A lógica de posicionamento e agrupamento não conhece a renderização, e a renderização não conhece o algoritmo de posicionamento — ela recebe apenas "nesta linha, nesta coluna, o bloco está em tal estado" e desenha conforme as regras. Essa separação permite alterar o visual dos blocos sem tocar na lógica de overlap, e vice-versa.

---

## 2. Modelo de Dados de Entrada

Cada instância de hábito chega à Agenda Panel como um dicionário com, no mínimo, os campos `start_minutes` e `end_minutes` (inteiros representando minutos desde meia-noite), `name` (string), `status` (string) e opcionalmente `substatus` (string). O campo `start_minutes` é inclusivo e `end_minutes` é exclusivo no sentido temporal: um bloco de 10:00-11:00 ocupa os minutos 600 a 660, significando que ele está presente nos timeslots que começam em 600, 615, 630 e 645, mas não no timeslot que começa em 660.

A granularidade temporal da grade é de 15 minutos. Cada linha visual da agenda corresponde a um intervalo de 15 minutos. Labels de hora (`HH:MM`) aparecem a cada duas linhas (30 minutos): a primeira linha do par exibe o label, a segunda não.

---

## 3. Fase 1 — Atribuição de Colunas (Greedy)

O método `_assign_columns` recebe as instâncias ordenadas por `start_minutes` e atribui a cada uma um índice de coluna (0-based). O algoritmo é greedy: para cada instância, percorre as colunas existentes na ordem e a coloca na primeira coluna cujo último bloco já terminou antes do início do novo. Se nenhuma coluna está livre, cria uma coluna nova.

O estado de cada coluna é rastreado por `col_ends`, uma lista onde `col_ends[c]` armazena o `end_minutes` do último bloco atribuído à coluna `c`. A condição para reutilizar uma coluna é `start_minutes >= col_ends[c]` — blocos que se tocam (término de um = início de outro) podem compartilhar a mesma coluna porque não há sobreposição visual.

### Exemplo concreto

Três blocos:

- Leitura 10:00-11:30 (600-690)
- Treino 10:30-13:00 (630-780)
- Meditação 11:00-12:30 (660-750).

A iteração processa na ordem de `start_minutes`:

- Leitura (600-690) é o primeiro bloco. Nenhuma coluna existe. Cria coluna 0. `col_ends = [690]`.
- Treino (630-780) tenta coluna 0: `630 >= 690`? Não, Leitura ainda não terminou. Cria coluna 1. `col_ends = [690, 780]`.
- Meditação (660-750) tenta coluna 0: `660 >= 690`? Não. Tenta coluna 1: `660 >= 780`? Não. Cria coluna 2. `col_ends = [690, 780, 750]`.

Resultado: `col_of = {Leitura: 0, Treino: 1, Meditação: 2}`.

Se houvesse um quarto bloco Alongamento 14:00-15:00 (840-900), ele reutilizaria a coluna 0 (`840 >= 690`), economizando espaço horizontal.

---

## 4. Fase 2 — Grupos de Sobreposição (Union-Find)

O greedy atribui colunas, mas não garante que blocos no mesmo "cluster" de sobreposição usem a mesma contagem total de colunas. Considere o exemplo das três instâncias acima: Leitura e Treino se sobrepõem diretamente (10:30-11:30), Treino e Meditação se sobrepõem diretamente (11:00-12:30), mas Leitura e Meditação não se sobrepõem diretamente (Leitura termina em 11:30, Meditação começa em 11:00 — há sobreposição indireta via Treino). Sem agrupamento, cada bloco poderia renderizar com uma contagem de colunas diferente, quebrando o alinhamento visual.

O Union-Find resolve isso. O algoritmo constrói um mapa `slot → [blocos]` usando a granularidade de 30 minutos (slots da régua interna). Para cada slot com dois ou mais blocos, faz `union()` dos IDs. Ao final, todos os blocos conectados — direta ou indiretamente — pertencem ao mesmo grupo.

Para cada grupo (identificado pelo `find()` da raiz), calcula-se `max(col + 1)` entre todos os membros. Esse valor é o `total_cols` do grupo: o número de colunas que todos os blocos daquele grupo devem usar na renderização.

### Exemplo concreto (continuação)

Mapa de slots (30min) para os três blocos:

| Slot | Minutos | Blocos presentes           |
| ---- | ------- | -------------------------- |
| 20   | 600-630 | Leitura                    |
| 21   | 630-660 | Leitura, Treino            |
| 22   | 660-690 | Leitura, Treino, Meditação |
| 23   | 690-720 | Treino, Meditação          |
| 24   | 720-750 | Treino, Meditação          |
| 25   | 750-780 | Treino                     |

Slot 21 tem Leitura e Treino → `union(Leitura, Treino)`. Slot 22 tem os três → `union(Leitura, Treino)` (já unidos) e `union(Leitura, Meditação)`. Resultado: os três pertencem ao mesmo grupo com `total_cols = 3`.

Se existisse um bloco isolado Alongamento 14:00-15:00, ele ficaria sozinho no grupo com `total_cols = 1`, ocupando toda a largura disponível.

---

## 5. Fase 3 — Renderização por Linha

A renderização é independente das Fases 1 e 2. Ela recebe, para cada célula (linha × coluna), uma informação de estado: o bloco está começando, continuando, terminando, ou a célula está vazia. A partir desse estado, aplica as regras visuais definidas em BR-TUI-032.

### Grade de renderização

A grade tem dois eixos. O eixo vertical são as linhas de 15 minutos, iteradas de `range_start` até `range_end` (calculados por `compute_agenda_range`). O eixo horizontal são as colunas atribuídas pela Fase 1, com largura mínima de 18 caracteres e gap de 1 caractere entre colunas.

Para cada linha de 15 minutos, a renderização consulta cada coluna e determina o estado do bloco naquele timeslot:

- **Início do bloco.** A linha corresponde ao `start_minutes` do bloco. Renderiza `▌{título} · {ícone_status}` — accent bar (`▌`) na cor do status, título em C_TEXT (branco), ícone na cor do status. Se o título excede a largura da coluna, trunca o nome com reticências mas preserva o ícone (ex: `▌Medita… · ○`).
- **Corpo do bloco.** A linha está entre `start_minutes` (exclusivo) e `end_minutes` (inclusivo) do bloco. Renderiza `▌{fill_char × largura}` — accent bar (`▌`, U+258C) na cor saturada do status seguido de caracteres de preenchimento (`fill_char()`) na cor do status. O `▌` é um caractere literal colorido, não bgcolor.
- **Fora de qualquer bloco (coluna vazia).** Se nenhuma outra coluna tem bloco ativo nessa linha, renderiza pontilhado sutil como representação de área livre. Se outra coluna tem bloco ativo, renderiza espaço vazio para não poluir visualmente.

### Regra de término (BR-TUI-032-R10)

A linha correspondente ao `end_minutes` do bloco **ainda exibe corpo com cor** (`▌{fill}`). A linha seguinte é que fica livre. Exemplo: um bloco de 10:00-11:00 tem corpo colorido nas linhas 10:15, 10:30, 10:45 e 11:00. A linha 11:15 é a primeira livre.

Essa regra existe porque o `end_minutes` é exclusivo temporalmente (o bloco não ocupa o minuto 660), mas visualmente a linha que representa o timeslot do término precisa mostrar que o bloco "acabou de terminar" — caso contrário, blocos curtos ficariam visualmente menores do que sua duração real.

### Blocos consecutivos sem gap (BR-TUI-032-R12)

Quando o bloco A termina em 11:00 e o bloco B começa em 11:00 na mesma coluna, a regra R12 tem prioridade sobre a R10: o título do bloco B substitui a linha que seria corpo de A. Não há gap nem cor residual do bloco anterior. O efeito visual é de transição direta — o bloco A termina uma linha antes e o título de B aparece imediatamente.

```
 │  10:30  │ ▌░░░░░░░░░░░░░░░░░░░░░░░ │    ← Leitura corpo
 │         │ ▌░░░░░░░░░░░░░░░░░░░░░░░ │    ← Leitura corpo
 │  11:00  │ ▌Exercício ·             │    ← título de B substitui corpo de A
 │         │ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │    ← Exercício corpo
```

### Colunas são independentes

Cada coluna resolve seu estado de forma autônoma. Numa mesma linha de 15 minutos, a coluna 0 pode estar exibindo corpo de um bloco que está terminando, a coluna 1 pode estar no meio de um bloco que continua, e a coluna 2 pode estar exibindo o título de um bloco que está começando. As regras de renderização (início, corpo, término, vazio) aplicam-se por célula, não por linha.

```
 │  11:00  │ ▌░░░░░░░░░░░░░░ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Meditação ·    │
             col 0: corpo    col 1: corpo    col 2: início
             (Leitura)       (Treino)        (Meditação)
```

---

## 6. Cenários de Referência

### Cenário 1: Três blocos em conflito

Leitura 10:00-11:30, Treino 10:30-13:00, Meditação 11:00-12:30. Três colunas, grupo único com `total_cols = 3`.

```
 │  10:00  │ ▌Leitura ·                                     │
 │         │ ▌░░░░░░░░░░░░░░                                │
 │  10:30  │ ▌░░░░░░░░░░░░░░ ▌Treino ·                      │
 │         │ ▌░░░░░░░░░░░░░░ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒                │
 │  11:00  │ ▌░░░░░░░░░░░░░░ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌Meditação ·   │
 │         │ ▌░░░░░░░░░░░░░░ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │  11:30  │ ▌░░░░░░░░░░░░░░ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │         │ · · · · · · · · ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │  12:00  │ · · · · · · · · ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │         │                 ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │  12:30  │ · · · · · · · · ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │         │                 ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ · · · · · · ·  │
 │  13:00  │ · · · · · · · · ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ · · · · · · ·  │
 │         │                 · · · · · · · · · · · · · · ·  │
```

Análise linha a linha do trecho 11:00-13:15:

| Linha | Col 0 (Leitura)           | Col 1 (Treino)         | Col 2 (Meditação)      |
| ----- | ------------------------- | ---------------------- | ---------------------- |
| 11:00 | corpo (R10: end=11:30)    | corpo                  | **início** (título)    |
| 11:15 | corpo                     | corpo                  | corpo                  |
| 11:30 | corpo (R10: linha do end) | corpo                  | corpo                  |
| 11:45 | vazio (livre)             | corpo                  | corpo                  |
| 12:00 | vazio                     | corpo                  | corpo                  |
| 12:15 | vazio                     | corpo                  | corpo                  |
| 12:30 | vazio                     | corpo                  | corpo (R10: end=12:30) |
| 12:45 | vazio                     | corpo                  | vazio (livre)          |
| 13:00 | vazio                     | corpo (R10: end=13:00) | vazio                  |
| 13:15 | vazio                     | vazio (livre)          | vazio                  |

### Cenário 2: Blocos consecutivos sem gap (mesma coluna)

Leitura 10:00-11:00, Exercício 11:00-12:00. Mesma coluna (sem sobreposição), `total_cols = 1`.

```
 │  10:00  │ ▌Leitura ·               │
 │         │ ▌░░░░░░░░░░░░░░░░░░░░░░░ │
 │  10:30  │ ▌░░░░░░░░░░░░░░░░░░░░░░░ │
 │         │ ▌░░░░░░░░░░░░░░░░░░░░░░░ │
 │  11:00  │ ▌Exercício ·             │    ← R12: título substitui corpo
 │         │ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │
 │  11:30  │ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │
 │         │ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │
 │  12:00  │ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │    ← R10: end line com cor
 │         │ ·                        │
```

Na linha 11:00, Leitura terminaria com corpo (R10), mas Exercício inicia exatamente ali (R12). A regra R12 tem prioridade: título do novo bloco aparece, corpo do anterior é suprimido.

### Cenário 3: Bloco mínimo de 15 minutos

Leitura 10:00-10:15. `total_cols = 1`.

```
 │  10:00  │ Leitura ·                │    ← início (única linha do bloco)
 │         │ ·                        │    ← livre
```

Um bloco de 15 minutos ocupa apenas uma linha: a de início. Não há corpo porque não existe timeslot entre `start_minutes` (exclusivo) e `end_minutes` (inclusivo) — o próximo timeslot (10:15) já está fora.

### Cenário 4: Bloco de 30 minutos

Leitura 10:00-10:30. `total_cols = 1`.

```
 │  10:00  │ ▌Leitura ·               │    ← início
 │         │ ▌░░░░░░░░░░░░░░░░░░░░░░░ │    ← corpo
 │  10:30  │ ▌░░░░░░░░░░░░░░░░░░░░░░░ │    ← end line com cor
```

Três linhas: título na primeira (10:00), corpo na segunda (10:15), e corpo na terceira (10:30 — linha do `end_minutes`, ainda com cor conforme R10). A próxima linha livre seria 10:45.

---

## 7. Invariantes

Estas propriedades devem ser verdadeiras em qualquer estado da agenda:

1. Um bloco sempre ocupa pelo menos uma linha (a de início, com título).
2. A linha de início tem accent bar (`▌`) na cor do status, título em C_TEXT, ícone na cor do status.
3. Todas as linhas entre o início (exclusivo) e o término (inclusivo) exibem accent bar com cor.
4. Nenhuma linha horizontal (`───`, `─┼─`, `─┬─`) atravessa um bloco de tempo.
5. Blocos em colunas diferentes nunca interferem visualmente entre si.
6. Todos os blocos de um mesmo grupo de sobreposição usam o mesmo `total_cols`.
7. A largura de cada coluna nunca é inferior a 18 caracteres.
8. O ícone de status é sempre preservado no truncamento de título.

---

## 8. Relação com Outros Subsistemas

O módulo `colors.py` é a fonte de verdade para mapeamento de status para cor, ícone e caractere de preenchimento. A Agenda Panel nunca define cores diretamente — sempre delega para `status_color()`, `status_icon()`, `fill_char()` e `fill_color()`. O `color-system.md` documenta o sistema semântico completo de cores, incluindo a tabela "Mapeamento Status → Cor do Bloco" que governa a aparência visual de cada estado.

O `compute_agenda_range()` calcula o intervalo visível da régua (range mínimo 05:00-23:30, expansível para eventos de madrugada ou noite) e é independente da lógica de overlap.

O scroll horizontal (BR-TUI-031, implementação futura) adiciona uma camada de viewport sobre a grade de renderização, mas não altera a lógica das Fases 1-3. A coluna de horas permanece fixa enquanto as colunas de blocos scrollam horizontalmente.

---

## Referências

- CLEAR, J. **Atomic Habits: An Easy & Proven Way to Build Good Habits & Break Bad Ones.** Nova York: Avery, 2018. (Fundamentação conceitual do sistema de hábitos)
- ADR-041: Redesign da Agenda Panel — blocos contínuos, scroll horizontal e granularidade 15min
- BR-TUI-032: Renderização de Blocos de Tempo na Agenda
- BR-TUI-031: Scroll Horizontal da Agenda
- BR-TUI-030: Paginação Temporal da Agenda
- `docs/reference/tui/color-system.md`: Sistema de cores semânticas
- `docs/reference/agenda-panel-mockup-reference.md`: Mockups visuais aprovados

---

**Data:** 22 de Março de 2026
