# Observabilidade

**Última atualização:** 2026-03-23

**BRs neste documento:** BR-OBS-001

---

### BR-OBS-001: Política de Visibilidade de Erros e Observabilidade

**Descrição:** Define onde e como erros, warnings e informações operacionais são exibidos em cada camada do sistema. O princípio é: o usuário só vê o que é acionável. Todo o resto vai para o log.

**ADR relacionada:** ADR-044 (a criar)

**Regras — CLI (`src/timeblock/commands/`):**

1. `stdout` recebe apenas output do comando solicitado (dados, confirmações de sucesso)
2. `stderr` recebe erros de validação, erros de operação, warnings acionáveis
3. Log file recebe tudo — debug, info, warning, error, critical
4. Exit codes: 0 = sucesso, 1 = erro de validação, 2 = erro interno
5. Mensagens de erro em português, sem stack trace (exceto com `--verbose`)
6. Nunca `print()` direto — sempre logger ou `typer.echo`/stderr

**Regras — TUI (`src/timeblock/tui/`):**

7. Erros de operação exibidos via `app.notify(error, severity="error")`
8. Warnings via `app.notify(msg, severity="warning")`
9. Confirmações via `app.notify(msg, severity="information")`
10. Log file recebe tudo, inclusive operações bem-sucedidas
11. stdout/stderr: NADA durante execução da TUI. Zero output fora do Textual
12. Nunca `print()`, `sys.stdout.write()`, ou logging para console handler durante TUI

**Regras — Service Layer (`src/timeblock/services/`):**

13. `ValueError` para erros de validação (nome vazio, rotina inexistente, FK violation prevenida)
14. Retorno `None` para recurso não encontrado (sem exceção)
15. `logger.warning` para operações recusadas por regra de negócio
16. `logger.error` para falhas inesperadas
17. `logger.info` para operações bem-sucedidas (auditoria)
18. Nunca `print()`, `sys.stdout.write()`, ou acesso direto a UI

**Regras — Database/Migrations (`src/timeblock/database/`):**

19. `logger.info` para migração aplicada, tabela criada, engine inicializado
20. `logger.error` para migração falhou, schema incompatível
21. Nunca `print()`, stdout, stderr — toda saída via logger

**Regras — Padrão TUI para `service_action`:**

22. Toda chamada a `service_action` em código TUI DEVE verificar o `error` retornado
23. Ignorar o segundo elemento da tupla `(result, error)` é violação desta BR

**Configuração de logging:**

| Modo | Console (stderr) | Arquivo (JSON Lines) | Nível mínimo |
| ---- | ---------------- | -------------------- | ------------ |
| CLI | Habilitado | Habilitado | INFO |
| TUI | Desabilitado | Habilitado | INFO |
| Testes | Desabilitado | Desabilitado | CRITICAL |
| Debug | Habilitado | Habilitado | DEBUG |

**Evolução planejada:**

- v1.7.0: Logs locais JSON Lines + notificações TUI + CLI stderr
- v2.0: Structured logging centralizado, Prometheus, health check, correlation ID
- v3.0: Distributed tracing (OpenTelemetry), alerting
- v4.0: Crash reporting, analytics opt-in, remote logging

**Testes:**

- `test_br_obs_001_tui_no_stdout`
- `test_br_obs_001_service_action_error_returns_tuple`
- `test_br_obs_001_migration_no_console`
- `test_br_obs_001_cli_error_on_stderr`
