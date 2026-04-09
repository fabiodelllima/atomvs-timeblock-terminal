# ADR-051: Estratégia de Backup do Banco de Dados

- **Status:** Proposto
- **Data:** 2026-04-09

---

## Contexto

O banco SQLite em `~/.local/share/atomvs/atomvs.db` contém todos os dados do usuário sem mecanismo de proteção. A perda do banco significa perda de todo o histórico. O `backup_service.py` já existe com implementação via `shutil.copy2`, mas não está exposto via CLI nem integrado ao startup da TUI.

Duas abordagens para backup de SQLite: `shutil.copy2` (cópia de arquivo) e `sqlite3 .backup()` (API nativa do SQLite que garante consistência mesmo com escrita concorrente).

## Decisão

**Mecanismo:** Manter `shutil.copy2` para Fase 1 (CLI manual). Para Fase 2 (auto-backup no startup), migrar para `sqlite3 .backup()` via `connection.backup(dest)` do Python — garante snapshot consistente mesmo que a TUI esteja escrevendo.

**Fases:**

1. **Fase 1 (v1.8.0):** Comandos CLI via Typer. `atomvs backup`, `atomvs backup list`, `atomvs backup restore`. Flag `--output` para path arbitrário.
2. **Fase 2 (v1.8.0, toggle):** Auto-backup no startup com rotação de 5. Usa `sqlite3 .backup()`.
3. **Fase 3 (v2.0+):** Export para cloud via rclone ou similar. Sync nativo com API REST.

**Rotação:** MAX_BACKUPS separado por tipo — 50 manuais, 5 automáticos. Nomes com label distinguem: `timeblock-...-manual.db` vs `timeblock-...-startup.db`.

**Restauração:** Sempre cria backup de segurança (pre-restore) antes de sobrescrever. Exige confirmação no CLI (`--yes` para skip).

## Consequências

- Dados do usuário protegidos desde a v1.8.0
- `shutil.copy2` suficiente para Fase 1 (operação manual, sem concorrência)
- Fase 2 requer refactor para `sqlite3 .backup()` (poucas linhas)
- Flag `--output` resolve caso de disco externo/pasta sync sem complexidade de cloud
- Referência: issue #22, issue #38, BR-DATA-001
