# Histórico de Mudanças

Todas as mudanças importantes do TimeBlock Organizer serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [Não Lançado]

### Planejado

- Refatoração HabitAtom (renomear HabitInstance para HabitAtom)
- Documentação Viva com BDD
- Funcionalidades avançadas de relatórios

---

## [1.1.0] - 2025-11-01

### Adicionado em 2025-11-01

#### **Sistema de Reordenamento de Eventos - Implementação Completa**

- Detecção automática de conflitos entre eventos agendados
- Cálculo de prioridades baseado em status e prazos (CRITICAL, HIGH, NORMAL, LOW)
- Algoritmo de reordenamento sequencial que respeita prioridades
- Confirmação interativa antes de aplicar mudanças
- Novo comando CLI: `timeblock reschedule [preview] [--auto-approve]`

**Services Aprimorados:**

- `TaskService.update_task()` agora retorna tupla com ReorderingProposal opcional
- `HabitInstanceService.adjust_instance_time()` integrado com detecção de conflitos
- `TimerService.start_timer()` detecta conflitos ao iniciar timers

**Novos Componentes:**

- `EventReorderingService` - Lógica central de reordenamento (90% cobertura de testes)
- `event_reordering_models.py` - Estruturas de dados (EventPriority, Conflict, ProposedChange, ReorderingProposal)
- `proposal_display.py` - Saída CLI formatada com Rich para propostas
- `reschedule.py` - Implementação do comando CLI

**Testes:**

- 78 novos testes (219 total, +55% de aumento)
- 100% cobertura em event_reordering_models
- 90% cobertura em event_reordering_service
- Testes de integração para todos os services afetados

**Documentação:**

- Documentação técnica completa em `docs/10-meta/event-reordering-completed.md`
- Retrospectiva de sprints em `docs/10-meta/sprints-v2.md`
- Arquitetura e documentação de API atualizadas

### Alterado

- Services agora retornam tuplas onde apropriado para incluir propostas de reordenamento
- Mensagens de erro aprimoradas com informações de conflito

### Corrigido

- Nenhum (sem bugs corrigidos, este é um release puramente de features)

### Mudanças Incompatíveis

- Nenhuma

### Performance

- Detecção de conflitos otimizada para complexidade O(n log n)
- Consultas eficientes de eventos em intervalos de datas

### Guia de Migração

Nenhuma migração necessária. Todas as mudanças são retrocompatíveis.

---

## [1.0.0] - 2025-10-16

### Adicionado em 2025-10-16

- Release baseline inicial
- Inicialização do banco de dados SQLite
- Operações CRUD básicas para eventos
- Listagem de eventos com filtros (dia, semana)
- Suporte a formato brasileiro de tempo (7h, 14h30)
- Detecção básica de conflitos (apenas aviso, não bloqueante)
- Suporte para eventos que cruzam meia-noite
- 141 testes com 99% de cobertura

**Comandos CLI:**

- `timeblock init` - Inicializar banco de dados
- `timeblock add` - Criar eventos
- `timeblock list` - Listar eventos com filtros

### Limitações Conhecidas

- Sem hábitos recorrentes
- Sem reordenamento automático
- Sem relatórios ou analytics
- CLI básica (sem TUI)

---

[Não Lançado]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/fabiodelllima/timeblock-organizer/releases/tag/v1.0.0
