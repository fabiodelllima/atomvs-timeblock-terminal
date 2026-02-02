# ADR-029: Package by Feature para Organização de Código

**Status**: Aceito

## Contexto

O arquivo `cli/src/timeblock/commands/habit.py` cresceu para ~700 linhas com múltiplas responsabilidades:

- CRUD de hábitos (create, list, update, delete)
- Ações pontuais (adjust, skip)
- Comandos de instância (atom list, atom log)
- Helpers de formatação e validação

Isso viola o Single Responsibility Principle (SRP) e dificulta manutenção.

Duas abordagens foram consideradas:

1. **Package by Layer**: Separar em `commands/`, `utils/`, `helpers/`
2. **Package by Feature**: Agrupar por domínio funcional

## Decisão

Adotamos **Package by Feature** (também conhecido como Screaming Architecture).

### Estrutura Adotada

```
commands/
  habit/
    __init__.py      # Composição e exports (~15 linhas)
    crud.py          # create, list, update, delete (~150 linhas)
    actions.py       # adjust, skip (~100 linhas)
    atom.py          # atom list, atom log (~80 linhas)
    display.py       # Helpers de formatação (~80 linhas)
```

### Princípios

1. **Coesão por domínio**: Tudo relacionado a `habit` fica junto
2. **~100-150 linhas por arquivo**: Facilita navegação e manutenção
3. **Helpers colocalizados**: `display.py` fica no package, não em `utils/` centralizado
4. **SRP por arquivo**: Cada arquivo tem uma responsabilidade clara

## Alternativas Consideradas

### Package by Layer (Rejeitada)

```
commands/habit.py
utils/habit_display.py
helpers/habit_validators.py
```

**Problemas:**

- `utils/` vira "junk drawer" (gaveta de tralhas)
- Baixa coesão
- Difícil navegar ("onde está X?")
- Para deletar feature, precisa caçar em N pastas

### CQRS (Rejeitada)

Command Query Responsibility Segregation seria overengineering para:

- Usuário único
- SQLite local
- Queries simples
- Sem event sourcing

## Consequências

### Positivas

- **Navegação intuitiva**: "Tudo de habit está em habit/"
- **Manutenção facilitada**: Arquivos pequenos e focados
- **Deletar feature**: Basta remover 1 pasta
- **Acoplamento explícito**: Dependências claras entre módulos
- **Screaming Architecture**: Estrutura "grita" o domínio, não o framework

### Negativas

- Mais arquivos para gerenciar
- Imports ligeiramente mais longos

## Referências

- **Clean Architecture** (Robert C. Martin) - Cap. 21 "Screaming Architecture"
- **Patterns of Enterprise Application Architecture** (Martin Fowler)
- **Domain-Driven Design** (Eric Evans) - Bounded Contexts

## Notas

Este padrão será aplicado progressivamente a outros domínios (timer, task, routine) conforme necessidade de refatoração surgir.
