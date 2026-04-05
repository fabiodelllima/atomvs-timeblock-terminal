# ADR-040: Unified Database Path

**Status:** Aceito

---

## Contexto

O projeto mantém dois mecanismos implícitos de resolução do path do banco de dados. A função `get_db_path()` em `database/engine.py` usa um path relativo ao pacote (`Path(__file__).parent.parent.parent / "data" / "timeblock.db"`), que resolve corretamente quando o processo é executado a partir do diretório do projeto (caso típico da CLI), mas falha silenciosamente quando executado de outro diretório de trabalho (caso da TUI lançada via `atomvs` no PATH).

O resultado é que a TUI cria um arquivo SQLite vazio no CWD do usuário, sem tabelas. Todas as operações falham com `OperationalError: no such table` — routines, tasks, time_log, habitinstance — e o `service_action` captura esses erros sem notificar o usuário. O dashboard renderiza placeholders vazios sem nenhuma indicação do problema. Os logs em `~/.local/share/atomvs/logs/atomvs.jsonl` registram dezenas de erros por sessão, mas o usuário não vê os logs durante o uso normal.

A variável de ambiente `TIMEBLOCK_DB_PATH` existe como override, mas não é documentada nem configurada por padrão. O path XDG (`~/.local/share/atomvs/atomvs.db`) é usado apenas pelo logger, nunca pelo banco.

---

## Decisão

### Path canônico via XDG Base Directory

O `get_db_path()` passa a usar o XDG Base Directory Specification como padrão, alinhando o banco com os logs que já seguem esse padrão:

```python
def get_db_path() -> str:
    db_path = os.getenv("TIMEBLOCK_DB_PATH")
    if db_path is None:
        data_dir = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "atomvs"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = str(data_dir / "atomvs.db")
    return db_path
```

### Auto-init no startup da TUI

A TUI chama `create_db_and_tables()` no `on_mount` do `DashboardScreen` se o banco não tiver tabelas. Isso garante que a TUI nunca opere sobre um banco vazio.

### Migração do banco existente

O banco antigo em `src/data/timeblock.db` permanece funcional via `TIMEBLOCK_DB_PATH`. Usuários existentes precisam migrar manualmente:

```bash
cp src/data/timeblock.db ~/.local/share/atomvs/atomvs.db
```

Uma mensagem de aviso é exibida na TUI e na CLI quando o banco antigo é detectado e o banco XDG está vazio.

---

## Consequências

### Positivas

- CLI e TUI sempre acessam o mesmo banco, independente do CWD.
- Alinhamento com XDG Base Directory Specification (freedesktop.org).
- Banco no mesmo diretório que os logs (`~/.local/share/atomvs/`).
- `TIMEBLOCK_DB_PATH` preservado como override para testes e ambientes customizados.

### Negativas

- Migração manual para usuários existentes (one-time, documentada).
- O path relativo `src/data/` deixa de funcionar sem variável de ambiente.
- Testes que dependem de `TIMEBLOCK_DB_PATH` não são afetados (já usam `:memory:`).

---

## Referências

- **XDG Base Directory Specification.** freedesktop.org. Disponível em: <https://specifications.freedesktop.org/basedir-spec/latest/\>.
- **DT-056:** TUI conecta a banco sem tabelas — falha silenciosa total.
- **BR-TUI-028:** Inicialização de banco no startup da TUI.

---

**Data:** 21 de Março de 2026
