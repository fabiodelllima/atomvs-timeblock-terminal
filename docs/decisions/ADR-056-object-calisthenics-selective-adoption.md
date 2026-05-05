# ADR-056: Adoção Seletiva de Object Calisthenics

- **Status:** Proposto
- **Data:** 2026-04-17

---

## Contexto

Object Calisthenics é um conjunto de nove regras propostas por Jeff Bay em _The ThoughtWorks Anthology_ (2008, p. 75-91), originalmente concebido como **exercício pedagógico** para desenvolvedores experimentarem SRP, encapsulamento e Tell-Don't-Ask aplicando todas as regras simultaneamente a um projeto greenfield de até mil linhas. As regras são: um nível de indentação por método (1), sem `else` (2), wrap de primitivos e strings (3), coleções de primeira classe (4), um ponto por linha — Lei de Deméter (5), não abreviar (6), classes pequenas com até 50 linhas e 10 classes por pacote (7), no máximo duas variáveis de instância (8), sem getters/setters/properties (9).

A avaliação arquitetural de 2026-04 (`docs/reference/architecture-assessment-2026-04-srp-solid.md` v1.1.0) incorporou Calisthenics como terceira lente interpretativa junto a SOLID (conceitual) e Fowler (acional). O uso como diagnóstico provou valor em duas situações concretas já identificadas no projeto. O `EventReorderingService` usa `event_type: str` como tag de união entre `Task`, `HabitInstance` e `Event` — é o caso-livro de primitive obsession (regra 3). O `tui/screens/dashboard/loader.py` constrói queries SQLModel compostas (`select(HabitInstance.habit_id).where(...).where(col(...).in_(...))`) atravessando o grafo de objetos do ORM — é violação direta da Lei de Deméter (regra 5 no numeramento do autor, que o projeto referencia como regra 6 seguindo a ordenação canônica posterior a Bay). Nesses casos, o vocabulário Calisthenics é mais compacto que paráfrases em SOLID ("violação de OCP e DIP via discriminação de tipo por string") ou que descrições Fowler ("candidato a Replace Conditional with Polymorphism").

Nem todas as nove regras, entretanto, são compatíveis com o projeto. Três delas entram em conflito direto com decisões arquiteturais já tomadas e documentadas, ou com o idioma Python. Adotar Calisthenics de forma tácita — sem registrar quais regras valem e quais não — cria risco de conflito silencioso em revisões futuras, com reviewers divergindo sobre se determinada regra é obrigatória ou sugestiva. O propósito deste ADR é resolver essa ambiguidade antes que ela apareça.

---

## Decisão

O projeto adota Object Calisthenics como **lente diagnóstica complementar**, não como barra de conformidade em code review. Cinco regras são adotadas plenamente, uma com flexibilidade idiomática, e três são explicitamente rejeitadas com justificativa.

**Regras adotadas plenamente:**

_Regra 1 — Um nível de indentação por método._ Métodos com indentação maior que um nível sinalizam mistura de níveis de abstração. Refatoração típica: Extract Function (Fowler, 2018, p. 106). Aplicada plenamente em código novo. Código legado só é refatorado sob essa lente quando já está sendo tocado por outra razão.

_Regra 3 — Wrap primitives._ Tipos primitivos (str, int, bool) usados como parâmetros de função ou campos de classe devem ser encapsulados em value objects, enums ou Protocols quando carregam semântica de domínio. Anotação de tipo via `Literal` ou `StrEnum` é aceita como wrap leve. O caso canônico no projeto é o `event_type: str` do `EventReorderingService`, que ADR-054 resolve com Protocol `Schedulable` e enum `SchedulableKind`.

_Regra 4 — First-class collections._ Coleções (`list`, `set`, `dict`) que carregam invariantes próprias — deduplicação, ordenação específica, pertinência condicional — devem ser encapsuladas em classes dedicadas. O caso canônico é o `ConflictSet` proposto em RF-018 para substituir `list[Conflict]` em `EventReorderingService`, eliminando a dedupe manual via `tuple(sorted(...))`.

_Regra 5 — First-class behavior em enums e value objects._ Comportamento que opera exclusivamente sobre atributos de um enum ou value object deve viver como método dessa entidade, não como função externa que a inspeciona. O caso canônico é o `HabitInstanceService._should_create_for_date(recurrence, target_date)` movido para `Recurrence.matches(target_date)` em RF-013. Corresponde ao smell Feature Envy de Fowler (2018, p. 76).

_Regra 6 — Lei de Deméter (one dot per line)._ A regra não é sobre contar pontos literalmente — é sobre não navegar por grafos de objetos alheios. Módulos de apresentação e de comandos não devem construir queries de ORM nem acessar métodos protegidos de services. O caso canônico é o `loader.py` do dashboard, que a Camada 3 da priorização da avaliação arquitetural seala via RF-015.

**Regra adotada com flexibilidade:**

_Regra 2 — Sem `else`._ Aceita em dois casos idiomáticos no projeto. Primeiro, `elif` em switches de enum quando cada branch mapeia um valor do enum para um resultado simples — o bloco if/elif é preferível a cadeia de `if ... return` quando transmite "eis o mapeamento completo" de forma mais clara. Segundo, `else` em guard clauses com retorno antecipado (`if not valid: raise ...`), onde o `else` implícito é o corpo principal da função. Proibido: `if/else` aninhado com lógica em ambos os branches, que é o alvo original da regra.

**Regras rejeitadas:**

_Regra 7 — Classes pequenas (até 50 linhas, 10 classes por pacote)._ Incompatível com ADR-029 (Package by Feature), que opera com arquivos de 100-150 linhas por granularidade de feature. Incompatível com o limite documentado nos padrões do projeto de 300 linhas soft e 1000 hard. Adotar os 50 de Bay forçaria fragmentação artificial dos services e widgets em dezenas de micro-classes, gerando indireção sem ganho.

_Regra 8 — No máximo duas variáveis de instância._ Inaplicável a modelos SQLModel, que são agregações relacionais por natureza — `TimeLog` tem doze campos, `HabitInstance` tem dez, e nenhum deles é defeito. Bay reconhece a limitação da regra a classes de comportamento; aplicada a entidades persistentes geraria value objects artificiais do tipo `TimeLogTiming` contendo `TimeLogDuration`, sem valor semântico.

_Regra 9 — Sem getters, setters, properties._ Incompatível com o uso idiomático de `@property` em Python. Properties são a forma canônica de expor comportamento ligado a dado em Python; forçar `tell_me_if_you_match_today()` no lugar de `matches_today` é anti-pythônico. Bay escreveu no contexto Java, onde a regra combate o anti-padrão Java-específico de getters/setters como bypass de encapsulamento. Python não compartilha esse anti-padrão.

---

## Consequências

Análises arquiteturais e code reviews podem usar vocabulário Calisthenics ("primitive obsession", "Deméter violation", "first-class collection") para nomear smells com densidade maior que paráfrases. A nomeação deixa claro o diagnóstico sem ambiguidade sobre categoria de severidade — por si só, a regra Calisthenics não qualifica a mudança como obrigatória; quem qualifica é o registro formal via DT, RF ou ADR.

DTs e RFs ganham anotação Calisthenics quando aplicável. O `technical-debt.md` e o `refactoring-catalog.md` passam a ter coluna ou campo opcional "Calisthenics" referenciando a regra Bay quando ela nomeia o smell com maior densidade. Ausência da anotação indica que o DT ou RF é diagnóstico por outras lentes (SRP, DIP, Extract Function, etc.).

Leitor futuro não precisa inferir a política. Um colaborador novo que encontre "wrap primitives" mencionado em uma ADR ou code review sabe, por este documento, que se trata de lente diagnóstica compartilhada pelo projeto, sabe quais regras o projeto adota e, importante, sabe quais regras o projeto explicitamente **não** adota e por quê. A rejeição registrada é tão importante quanto a adoção, porque elimina a expectativa de que toda regra Calisthenics vale.

Não há impacto imediato em `src/`. Esta decisão é de governança; afeta processo de análise e de review, não código em produção. Refatorações que aplicam as regras adotadas são materializadas em DTs, RFs e ADRs específicos (ADR-054 para regra 3; RF-013 para regra 5; RF-015 para regra 6; RF-018 para regra 4), com seus próprios ciclos de implementação e teste.

A decisão também não cria obrigação retroativa. Código legado que viola uma das regras adotadas não é automaticamente débito técnico — torna-se débito apenas quando o achado é registrado formalmente via DT referenciando a regra. Isso preserva o princípio do `technical-debt.md` como SSOT explícito, não implícito.

---

## Alternativas Consideradas

**Adoção integral das nove regras.** Rejeitada. As incompatibilidades das regras 7, 8 e 9 com ADR-029, com SQLModel e com idiomaticidade Python foram examinadas em detalhe e considerou-se que o custo de aplicá-las supera o benefício. Aplicar a regra 7 forçaria reversão parcial de ADR-029. Aplicar a regra 8 forçaria introdução de value objects sem valor semântico sobre entidades relacionais. Aplicar a regra 9 geraria code reviews recorrentes onde `@property` idiomática precisaria ser defendida caso a caso.

**Não adotar Calisthenics de forma alguma.** Rejeitada. O vocabulário das cinco regras adotadas é genuinamente mais compacto que paráfrases equivalentes em SOLID ou Fowler. "Primitive obsession em `event_type`" é mais direto que "uso de string literal como discriminante de união de tipos, violando OCP e DIP"; "Deméter violation em `loader.py`" é mais direto que "camada de apresentação navega pelo grafo de objetos do ORM atravessando encapsulamento de camada adjacente". Recusar o vocabulário por rejeição total custaria densidade analítica.

**Adoção tácita em análises e reviews, sem ADR.** Rejeitada. Criaria conflito silencioso em revisões futuras. Reviewers divergiriam sobre se a regra 7 é obrigatória (porque "é Calisthenics") ou sugestiva (porque "o projeto já tem limites diferentes"), e cada conflito precisaria ser resolvido caso a caso. O custo de redigir este ADR uma vez é menor que o custo recorrente dessa ambiguidade.

**Adoção de Calisthenics como regra de linter.** Rejeitada por ora. Não existe linter Python maduro que implemente Calisthenics de forma confiável — a regra 4 (first-class collections) exige análise semântica além do escopo de analisadores estáticos padrão, e a regra 5 (behavior em enums) exige entender intenção de design. Ferramentas como `ruff` ou `pylint` capturam alguns dos smells relacionados (`too-many-instance-attributes` aproxima a regra 8, que o projeto rejeita), mas não o conjunto adotado. Lente diagnóstica humana é a forma praticável hoje.

---

## Referências

BAY, J. Object Calisthenics. In: **The ThoughtWorks Anthology: Essays on Software Technology and Innovation.** Raleigh: Pragmatic Bookshelf, 2008, p. 75-91.

FOWLER, M. **Refactoring: Improving the Design of Existing Code.** 2. ed. Boston: Addison-Wesley, 2018.

### ADRs Relacionados

- ADR-007: Service Layer (precedente de governança de padrões de código)
- ADR-029: Package by Feature (motivo de rejeição da regra 7)
- ADR-053: Uniformização do Service Pattern (decisão técnica, não relacionada)
- ADR-054: Schedulable Protocol (materializa a regra 3 no `EventReorderingService`)
- ADR-055: Extração de Regras Puras (independente, mas consistente com regra 1)

### Documentos de Projeto Relacionados

- `docs/reference/architecture-assessment-2026-04-srp-solid.md` v1.1.0 (documento-mãe que propôs este ADR)
- `docs/guides/refactoring-catalog.md` (destino das RFs anotadas com regra Calisthenics)
- `docs/reference/technical-debt.md` (destino dos DTs anotados com regra Calisthenics)
