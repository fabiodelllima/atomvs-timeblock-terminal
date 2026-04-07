# C4 Level 1: System Context

- **Status:** Aceito
- **Data:** 2026-04-06

```mermaid
graph TB
    User([Usuário])

    ATOMVS["ATOMVS Time Planner<br/>CLI + TUI para hábitos e agenda"]

    GitLab[GitLab CI/CD<br/>Pipeline 7 jobs, 4 stages]
    GitHub[GitHub Mirror<br/>Push Mirroring nativo]
    Calendar[Calendário Externo<br/>Google Calendar, Outlook]
    DB[(SQLite<br/>~/.local/share/atomvs/atomvs.db)]

    User -->|"CLI (Typer) / TUI (Textual)"| ATOMVS
    ATOMVS -->|Read/Write| DB
    GitLab -->|Push Mirroring| GitHub
    ATOMVS -.->|Sync futuro| Calendar

    style ATOMVS fill:#1168bd,stroke:#0b4884,color:#fff
    style GitLab fill:#fc6d26,stroke:#e24329,color:#fff
    style GitHub fill:#333,stroke:#222,color:#fff
    style Calendar fill:#999,stroke:#666,color:#fff
    style DB fill:#999,stroke:#666,color:#fff
    style User fill:#08427b,stroke:#052e56,color:#fff
```

## Elementos

**Usuário:** Pessoa organizando tempo e cultivando hábitos via terminal.

**ATOMVS Time Planner:** Sistema core — Python 3.13+, SQLite local-first. Duas interfaces: CLI (Typer) para operações rápidas e TUI (Textual) para dashboard interativo. Comando de entrada: `atomvs`.

**SQLite:** Banco local em `~/.local/share/atomvs/atomvs.db` (XDG Base Directory). Logs em JSON Lines no mesmo diretório.

**GitLab CI/CD:** Pipeline com 7 jobs em 4 stages (quality, test, coverage, security). Imagem Docker customizada no Container Registry.

**GitHub Mirror:** Showcase via Push Mirroring nativo do GitLab. GitHub não é fonte de verdade.

**Calendário Externo:** Sincronização futura com Google Calendar/Outlook via CalDAV (planejado para v2.0+).
