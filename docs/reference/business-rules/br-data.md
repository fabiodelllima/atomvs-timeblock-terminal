# Data

### BR-DATA-001: Backup Automático do Banco de Dados (NOVA 02/03/2026)

**Regra:** O sistema DEVE criar backup automático do SQLite no startup e shutdown da TUI, mantendo rotação de N cópias mais recentes.

**Motivação:** Operações de quick action (done, skip, complete) alteram dados diretamente via TUI. Backup garante recuperação em caso de corrupção, bug no código ou operação indevida.

**Requisitos:**

1. Backup criado automaticamente no shutdown da TUI (label: shutdown)
2. Backups armazenados em diretório `backups/` ao lado do banco principal
3. Formato do nome: `timeblock-YYYYMMDD-HHMMSS-{label}.db`
4. Rotação automática mantém no máximo 10 cópias (MAX_BACKUPS = 10)
5. Backups mais antigos removidos automaticamente ao exceder limite
6. Função `restore_backup(path)` cria backup de segurança (label: pre-restore) antes de restaurar
7. Banco inexistente no startup não gera erro — backup silenciosamente ignorado

**Testes esperados:** 8

- Backup criado com timestamp correto
- Label aparece no nome do arquivo
- Rotação remove backups excedentes
- Banco inexistente retorna None sem erro
- Restore cria pre-restore antes de sobrescrever
- list_backups retorna ordenado por data
- Diretório de backups criado automaticamente
- MAX_BACKUPS respeitado
