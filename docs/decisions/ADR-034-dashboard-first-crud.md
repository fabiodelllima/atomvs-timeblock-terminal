# ADR-034: Dashboard-first CRUD

- **Status:** Aceito
- **Data:** 2026-03-05
- **Relacionado:** ADR-031 (TUI Implementation), BR-TUI-003 (Dashboard Screen), BR-TUI-005 (CRUD Operations Pattern)

## Contexto

O planejamento original da Sprint 4 (sprints.md v2.0.0) previa CRUD implementado em screens dedicadas — RoutinesScreen, HabitsScreen e TasksScreen — cada uma com formulários inline e keybindings próprios. O dashboard serviria apenas como visão resumida, sem capacidade de criação ou edição.

Na prática, isso cria dois problemas:

1. **Experiência fragmentada.** O usuário abre a TUI, vê o dashboard vazio (sem rotina, sem hábitos), e precisa navegar para 2-3 screens diferentes para popular dados antes de poder usar o dashboard como ferramenta de trabalho. O fluxo de primeira utilização é: Dashboard → Routines (criar rotina) → Habits (criar hábitos) → Tasks (criar tarefas) → voltar ao Dashboard.

2. **Dashboard como hub não-funcional.** A Sprint 3.2 investiu em tornar o dashboard interativo (dados reais, quick actions, navegação entre panels). Mas sem CRUD, ele permanece read-only — o usuário vê dados mas não pode modificá-los sem sair.

A filosofia do projeto é que o dashboard seja o hub central onde o usuário gerencia seu dia completo. Quick actions (Ctrl+Enter done, Ctrl+S skip, Ctrl+K complete) já implementam a metade "write" mais frequente. Falta a metade "CRUD" (criar, editar, deletar).

## Decisão

### 1. CRUD via Modais no Dashboard

Todas as operações CRUD são acessíveis diretamente no dashboard através de modais contextuais. O panel focado determina o tipo de operação:

- Header focado + `n` → criar rotina
- Panel hábitos focado + `n` → criar hábito
- Panel tarefas focado + `n` → criar tarefa
- `e` → editar item sob cursor no panel focado
- `x` → deletar item sob cursor com ConfirmDialog

### 2. Keybindings Contextuais por Panel

As teclas `n`, `e`, `x` são globais no dashboard mas seu comportamento depende do panel focado. O footer contextual (BR-TUI-007) já exibe keybindings por panel — basta adicionar as operações CRUD.

Este padrão é consistente com a BR-TUI-005, que define `n`=novo, `e`=editar, `x`=deletar como padrão CRUD. A mudança é apenas onde essas teclas operam (dashboard em vez de screens dedicadas).

### 3. Widgets Reutilizáveis: ConfirmDialog e FormModal

Dois widgets genéricos sustentam todo o CRUD:

- **ConfirmDialog** (BR-TUI-019): modal de confirmação com título, mensagem, Enter/Esc. Reutilizável por qualquer operação destrutiva.
- **FormModal** (BR-TUI-020): modal de formulário com campos tipados, validação inline, Tab entre campos, Enter salva, Esc cancela.

Ambos são widgets Textual montados/desmontados no DashboardScreen, sem troca de screen.

### 4. Screens Dedicadas como Visão Expandida

RoutinesScreen, HabitsScreen e TasksScreen permanecem como visões expandidas para cenários que exigem mais espaço ou detalhe (ex: grade semanal de rotinas, lista completa de hábitos com filtros). Essas screens poderão reutilizar os mesmos ConfirmDialog e FormModal. Implementação em sprint futura.

### 5. Orquestração: DashboardScreen como Coordinator

O DashboardScreen já funciona como coordinator (carrega dados, distribui para panels). Para CRUD, o padrão se mantém:

- DashboardScreen intercepta keybindings CRUD
- Identifica panel focado e item selecionado
- Monta o modal apropriado (FormModal ou ConfirmDialog)
- Ao confirmar, chama o service correspondente via `service_action()`
- Executa `refresh_data()` para atualizar todos os panels

Widgets de panel nunca acessam services diretamente (BR-TUI-009). A DashboardScreen é a boundary entre apresentação e lógica de aplicação, alinhado com o padrão Service Layer (FOWLER, 2002, p. 133).

## Consequências

**Positivas:**

- Fluxo de primeira utilização em uma única screen: abrir TUI → `n` criar rotina → `n` criar hábitos → pronto
- Dashboard funcional como hub completo de gerenciamento do dia
- Widgets ConfirmDialog e FormModal reutilizáveis em todo o projeto
- Consistente com quick actions já implementadas (mesma screen, mesmo fluxo)

**Negativas:**

- DashboardScreen ganha responsabilidade de orquestração CRUD (aumento de complexidade)
- Modais no Textual exigem gerenciamento cuidadoso de foco (modal trap)
- Screens dedicadas ficam temporariamente como placeholder

**Mitigação:**

- Extrair lógica de orquestração CRUD em mixin ou helper se DashboardScreen ultrapassar 300 linhas (BR-TUI-015)
- Testes unitários de modal cobrem edge cases de foco (Esc fecha, Tab navega)

## Alternativas Consideradas

### CRUD apenas em screens dedicadas

Abordagem original do sprints.md. Funcional, mas fragmenta a experiência e deixa o dashboard como read-only. Rejeitada por conflitar com a filosofia "dashboard é o hub central".

### CRUD via CLI apenas

A CLI já suporta CRUD completo. Forçar o usuário a alternar entre TUI e CLI para criar dados derrota o propósito da TUI. Rejeitada.

### CRUD inline (sem modal)

Formulários inline no próprio panel, sem overlay. Funcionaria para campos simples (nome da rotina), mas fica confuso para formulários com múltiplos campos (hábito: título, horário, duração, recorrência). Rejeitada por não escalar.

## Referências

FOWLER, M. _Patterns of Enterprise Application Architecture_. Boston: Addison-Wesley, 2002, p. 133.

HUMBLE, J.; FARLEY, D. _Continuous Delivery_. Boston: Addison-Wesley, 2010, p. 179-183.
