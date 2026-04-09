# Fluxo de Atividade: Dia Típico do Usuário

- **Status:** Aceito
- **Data:** 2026-04-06

```mermaid
flowchart TD
    Start([Inicio do dia]) --> Open["Abrir ATOMVS (comando atomvs)"]
    Open --> Dashboard[Dashboard: AgendaPanel + HabitsPanel + TasksPanel]

    Dashboard --> HasPending{Tem habitos/tasks pendentes?}

    HasPending -->|Nao| Plan[Criar tasks ou habitos via modais CRUD]
    HasPending -->|Sim| Review[Revisar agenda do dia]

    Review --> Execute[Selecionar habito no HabitsPanel]

    Plan --> Execute

    Execute --> StartTimer["t: iniciar timer"]
    StartTimer --> Work[TimerPanel exibe contagem]
    Work --> Action{Acao}

    Action -->|"s - stop"| Complete[Completar: status=DONE + substatus automatico]
    Action -->|"space - pause"| Pause[Pausar timer]
    Action -->|"c - cancel"| Cancel[Cancelar sessao]

    Pause --> Resume["space - retomar"]
    Resume --> Work

    Complete --> Metrics[MetricsPanel atualiza streak e stats]
    Metrics --> More{Mais itens pendentes?}

    More -->|Sim| Execute
    More -->|Nao| End([Fim do dia])

    Cancel --> More
```

**Atalhos alternativos (HabitsPanel):** `s` skip, `v` done (sem timer), `u` undo.

**Referências:**

- ADR-034: Dashboard-first CRUD
- ADR-037: TUI keybindings standard
- ADR-038: Dashboard interaction patterns
