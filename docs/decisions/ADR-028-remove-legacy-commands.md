# ADR-028: Remoção de Comandos Legados (add/list)

**Status:** Aceito

**Data:** 2026-01-30

## Contexto

O TimeBlock Organizer evoluiu de uma arquitetura de comandos genéricos (`add`, `list`) para comandos por recurso (`routine`, `habit`, `task`, `timer`, `tag`).

Os comandos legados operavam sobre a entidade `Event`, que foi substituída por entidades específicas:

- `HabitInstance` - instâncias de hábitos recorrentes
- `Task` - tarefas pontuais

## Decisão

Remover os comandos legados:

- `timeblock add` - criava Event genérico
- `timeblock list` - listava Events

Manter o modelo `Event` para uso interno (detecção de conflitos em `EventReorderingService`).

## Consequências

### Positivas

- CLI mais limpo e consistente
- Menor superfície de manutenção
- Arquitetura alinhada com modelo de domínio atual

### Negativas

- Quebra compatibilidade (não há usuários externos)
- 18 testes removidos

## Arquivos Removidos

### Comandos

- `cli/src/timeblock/commands/add.py`
- `cli/src/timeblock/commands/list.py`

### Utilitários (órfãos)

- `cli/src/timeblock/utils/queries.py`
- `cli/src/timeblock/utils/event_list_presenter.py`
- `cli/src/timeblock/utils/event_date_filters.py`
- `cli/src/timeblock/utils/formatters.py`

### Testes

- `cli/tests/e2e/test_list_command.py` (12 testes)
- `cli/tests/integration/commands/test_add_edge_cases.py` (6 testes)

## Alternativas Consideradas

1. **Manter como visão unificada** - Refatorar `list` para mostrar HabitInstance + Task
   - Rejeitado: duplicaria funcionalidade dos comandos por recurso

2. **Deprecar mas manter** - Avisar usuário que comandos serão removidos
   - Rejeitado: sem usuários externos, complexidade desnecessária
