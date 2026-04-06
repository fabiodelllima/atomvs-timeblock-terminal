# ADR-007: Padrão Service Layer

- **Status:** Aceito
- **Data:** 2025-09-20

## Contexto

**Atualização:** 2026-01-17

Commands acessando models diretamente cria acoplamento e dificulta:

- Validação de regras de negócio
- Testes unitários
- Reutilização de lógica

## Decisão

Implementar camada de Services entre Commands e Models.

```
Commands (CLI) => Services => Models (DB)
```

## Alternativas Consideradas

**Repository Pattern**

- Prós: Abstrai DB completamente
- Contras: Overhead para SQLite simples

**Commands diretos em Models**

- Prós: Menos código
- Contras: Lógica dispersa, difícil testar

**Domain Services (DDD)**

- Prós: Separação clara
- Contras: Over-engineering para o escopo

## Consequências

**Positivas:**

- Business logic centralizada
- Commands enxutos
- Testes unitários isolados
- Transações controladas

**Negativas:**

- Camada adicional
- Boilerplate moderado

## Critérios de Validação

- 100% cobertura em services
- Commands < 30 linhas
- Zero lógica de negócio em commands

## Implementação

Services usam dependency injection com session:

```python
class HabitService:
    def __init__(self, session: Session):
        self.session = session

    def create_instances(self, habit: Habit) -> list[HabitInstance]:
        ...
```

**API Contract completo:** Ver `docs/explanation/architecture.md` seção 4.2.1
