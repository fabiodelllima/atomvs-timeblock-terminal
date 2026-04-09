# ADR-049: Rastreamento de Atividade em Pausas — Duas Fases

- **Status:** Proposto
- **Data:** 2026-04-09

---

## Contexto

Durante uso real do dashboard, foi identificado que pausas no timer representam tempo não rastreado. O modelo `PauseLog` já existe em `src/timeblock/models/event.py` com campos `pause_start` e `pause_end`, mas NÃO está conectado ao `timer_service.py`. O service implementa pause/resume usando apenas `TimeLog.pause_start` e `TimeLog.paused_duration` (linhas 240-315).

BR-TIMER-009 já prevê categorização do motivo da pausa (foco_perdido, redes_sociais, etc.). Esta ADR trata de um problema complementar: rastrear o que o usuário _fez_ durante a pausa — alinhado com Atomic Habits (CLEAR, 2018, Cap. 16) sobre tornar o tempo visível.

A feature completa (atribuição retroativa de tempo) depende de ADR-041 (AgendaPanel redesign) para renderização. Para entregar valor sem esperar, a implementação é dividida em duas fases.

## Decisão

**Fase 1 (v1.8.0):** Registro descritivo.

- Ao dar resume, exibir modal com opções: selecionar habit/task ativo ou nota livre
- Modal opcional — "Continuar sem registrar" fecha imediatamente
- Persistir no `PauseLog` com novo campo `note: str | None`
- Conectar `PauseLog` ao `timer_service`: criar em `pause_timer()`, completar em `resume_timer()`
- AgendaPanel NÃO é alterado
- Formalizado em BR-TIMER-010

**Fase 2 (futuro, atrás de feature toggle — ADR-048):**

- Tempo da pausa atribuído retroativamente como sessão de outro habit/task
- Blocos atribuídos aparecem no AgendaPanel
- Depende de ADR-041 para renderização

**Descoberta técnica — como conectar PauseLog:**

Em `timer_service.pause_timer()`: criar `PauseLog(timelog_id=id, pause_start=now)`.
Em `timer_service.resume_timer()`: buscar último `PauseLog` sem `pause_end`, preencher `pause_end=now`.

**Campos novos em PauseLog:**

- `note: str | None` — texto livre ou nome do item selecionado
- `activity_type: str | None` — "habit", "task", "free"
- `activity_id: int | None` — FK para habit_instance ou task (Fase 2)

## Consequências

- Fase 1 entrega valor imediato sem tocar no AgendaPanel
- Infraestrutura já existe (PauseLog no modelo, exportado em `__init__.py`)
- Requer migração de banco (novos campos em PauseLog)
- Fase 2 fica atrás de toggle até ADR-041 ser implementado
- Referência: issue #21, BR-TIMER-010
