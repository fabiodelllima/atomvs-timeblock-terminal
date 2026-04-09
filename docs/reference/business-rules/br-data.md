# Dados

O domínio Data cobre persistência, integridade e recuperação dos dados do usuário. O banco SQLite em `~/.local/share/atomvs/atomvs.db` é a única fonte de verdade — não há servidor, não há sync (até v3.0). A perda do banco significa perda de todo o histórico de hábitos, streaks e métricas. As regras abaixo garantem que o sistema protege esses dados proativamente.

---

### BR-DATA-001: Backup do Banco de Dados

**Descrição:** O sistema oferece backup do SQLite em três modalidades: manual via CLI, automático no startup da TUI, e exportação para path arbitrário.

**Motivação:** Operações de quick action (done, skip, complete) alteram dados diretamente. Backup garante recuperação em caso de corrupção, bug no código ou operação indevida.

**Regras — Fase 1 (CLI manual, v1.8.0):**

1. `atomvs backup` cria cópia timestamped do banco
2. `atomvs backup list` lista backups existentes com data e tamanho
3. `atomvs backup restore <path>` restaura banco a partir de backup
4. Antes de restaurar, cria backup de segurança (label: pre-restore)
5. Backups armazenados em `~/.local/share/atomvs/backups/`
6. Formato do nome: `timeblock-YYYYMMDD-HHMMSS-{label}.db`
7. Flag `--output <path>` permite salvar backup em path arbitrário (disco externo, pasta sincronizada)

**Regras — Fase 2 (automático, v1.8.0, atrás de toggle):**

8. Backup criado automaticamente no startup da TUI (label: startup)
9. Rotação automática mantém no máximo 5 backups automáticos
10. Habilitado por padrão, desabilitável via Settings (issue #14)
11. Banco inexistente no startup não gera erro — backup silenciosamente ignorado

**Regras — Fase 3 (remoto, v2.0+):**

12. Integração com rclone ou similar para upload em S3/GDrive/cloud
13. Sync nativo quando API REST existir (v3.0)

**Implementação existente:**

`src/timeblock/services/backup_service.py` já implementa: `create_backup(label)`, `restore_backup(path)`, `list_backups()`, rotação com MAX_BACKUPS=50. Faltam: comandos CLI (Typer), auto-backup no startup, flag `--output`.

**Testes:**

- `test_br_data_001_backup_creates_timestamped_file`
- `test_br_data_001_backup_with_label`
- `test_br_data_001_restore_creates_pre_restore`
- `test_br_data_001_list_returns_sorted`
- `test_br_data_001_rotation_removes_oldest`
- `test_br_data_001_missing_db_returns_none`
- `test_br_data_001_output_flag_copies_to_path`
- `test_br_data_001_auto_backup_on_startup`
- `test_br_data_001_auto_backup_disabled_via_settings`

---

### BR-DATA-002: Integridade do Banco

**Descrição:** O sistema verifica integridade do SQLite na inicialização.

**Regras:**

1. Executar `PRAGMA integrity_check` no startup
2. Se falhar, notificar o usuário e sugerir restore do último backup
3. Log do resultado da verificação em `atomvs.jsonl`

**Testes:**

- `test_br_data_002_integrity_check_on_startup`
- `test_br_data_002_corrupt_db_warns_user`
