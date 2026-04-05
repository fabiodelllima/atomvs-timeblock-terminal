# CLI

A CLI (Command Line Interface) é a interface primária do TimeBlock Planner e a única que existia antes da TUI. Toda funcionalidade do sistema é acessível via comandos no terminal, seguindo o padrão resource-first definido no ADR-005: o substantivo vem antes do verbo (`habit create`, `routine activate`, `task list`). Esse padrão torna os comandos previsíveis e autodescritivos — um usuário que sabe usar `habit create` adivinha corretamente que `habit list`, `habit edit` e `habit delete` existem.

A CLI serve dois públicos com necessidades distintas. Para uso interativo diário, ela oferece atalhos, flags curtas e outputs formatados com Rich. Para automação e scripts, ela garante códigos de saída consistentes, outputs parseáveis e comportamento determinístico (sem prompts interativos quando o input é completo). As regras desta seção formalizam comportamentos que cruzam domínios: validação de flags dependentes (se informou `--start`, deve informar `--end`), formatos de data/hora aceitos e padrões de output entre comandos.

### BR-CLI-001: Validação de Flags Dependentes

**Descrição:** Flags que dependem de outras devem ser validadas antes da execução do comando.

**Pares Obrigatórios:**

| Flag Principal | Requer  | Comando Afetado |
| -------------- | ------- | --------------- |
| --start        | --end   | habit create    |
| --end          | --start | habit create    |
| --from         | --to    | report \*       |
| --to           | --from  | report \*       |

**Comportamento:**

- Se apenas uma flag do par for fornecida: ERROR
- Mensagem clara indicando a dependência

**Exemplo de Erro:**

```bash
$ habit create --title "Academia" --start 07:00
[ERROR] --start requer --end (e vice-versa)
```

**Testes:**

- `test_br_cli_001_start_requires_end`
- `test_br_cli_001_end_requires_start`
- `test_br_cli_001_from_requires_to`
- `test_br_cli_001_to_requires_from`

---

### BR-CLI-002: Formatos de Datetime Aceitos

**Descrição:** Sistema aceita múltiplos formatos de data e hora para flexibilidade do usuário.

**Formatos de Datetime (--datetime):**

| Formato          | Exemplo          |
| ---------------- | ---------------- |
| YYYY-MM-DD HH:MM | 2025-12-25 14:30 |
| YYYY-MM-DD HHhMM | 2025-12-25 14h30 |
| YYYY-MM-DD HHh   | 2025-12-25 14h   |
| DD-MM-YYYY HH:MM | 25-12-2025 14:30 |
| DD-MM-YYYY HHhMM | 25-12-2025 14h30 |
| DD-MM-YYYY HHh   | 25-12-2025 14h   |
| DD/MM/YYYY HH:MM | 25/12/2025 14:30 |
| DD/MM/YYYY HHhMM | 25/12/2025 14h30 |
| DD/MM/YYYY HHh   | 25/12/2025 14h   |

**Formatos de Date (--date, --from, --to):**

| Formato    | Exemplo    |
| ---------- | ---------- |
| YYYY-MM-DD | 2025-12-25 |
| DD-MM-YYYY | 25-12-2025 |
| DD/MM/YYYY | 25/12/2025 |

**Comportamento:**

- Parser tenta cada formato em ordem
- Primeiro match válido é usado
- Formato inválido: ERROR com mensagem "Veja formatos aceitos com --help"

**Testes:**

- `test_br_cli_002_datetime_iso_format`
- `test_br_cli_002_datetime_brazilian_format`
- `test_br_cli_002_date_multiple_formats`

### BR-CLI-003: Padronização de Idioma

**Descrição:** Todas as mensagens, helps e textos exibidos ao usuário devem estar em Português Brasileiro (PT-BR).

**Referência:** ADR-018-language-standards.md

**Escopo:**

| Elemento             | Idioma Obrigatório | Exemplo                     |
| -------------------- | ------------------ | --------------------------- |
| Mensagens de erro    | PT-BR              | "Erro ao criar evento"      |
| Mensagens de sucesso | PT-BR              | "Hábito criado com sucesso" |
| Help de comandos     | PT-BR              | help="Título do hábito"     |
| Help de flags        | PT-BR              | help="Hora início (HH:MM)"  |
| Prompts interativos  | PT-BR              | "Confirmar? [S/n]"          |
| Docstrings CLI       | PT-BR              | """Cria um novo hábito."""  |

**Exceções (permitido inglês):**

| Elemento                     | Motivo                |
| ---------------------------- | --------------------- |
| Nomes de variáveis           | Padrão de código      |
| Nomes de funções/classes     | Padrão de código      |
| Tipos em commits             | Conventional commits  |
| Termos técnicos sem tradução | Ex: "timer", "status" |

**Estado Atual:** PARCIALMENTE IMPLEMENTADO (ver DT-006 em roadmap.md)

**Testes:**

- `test_br_cli_003_error_messages_ptbr`
- `test_br_cli_003_success_messages_ptbr`
- `test_br_cli_003_help_texts_ptbr`

---

### BR-CLI-004: Logging Estruturado nos Commands (NOVA 21/03/2026)

**Descrição:** Todos os commands da CLI devem gerar log entries estruturados (JSON Lines), registrando entrada, saída e erros de cada operação. Operações via CLI que modifiquem o banco devem ser rastreáveis nos logs, assim como as operações da TUI já são via `service_action`.

**Decisão arquitetural:** DT-058

**Regras:**

1. Cada command Typer deve logar: nome do comando, parâmetros recebidos, resultado (sucesso/erro)
2. Formato: JSON Lines no mesmo arquivo da TUI (`~/.local/share/atomvs/logs/atomvs.jsonl`)
3. Implementação via decorator ou middleware aplicável a todos os commands
4. Erros devem incluir traceback completo no log (sem exibir ao usuário)
5. Operações de leitura (list, show) logam em nível DEBUG; operações de escrita (create, delete, update) em nível INFO
6. Logger compartilhado com a TUI (`timeblock.utils.logger.get_logger`)

**Testes:**

- `test_br_cli_004_create_command_logs_info`
- `test_br_cli_004_delete_command_logs_info`
- `test_br_cli_004_error_logs_traceback`
- `test_br_cli_004_list_command_logs_debug`
