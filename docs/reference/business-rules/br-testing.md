# Testing

### BR-TEST-001: Fixture scope="session" com Rollback Transacional (NOVA 05/03/2026)

**Regra:** Testes de integração compartilham engine e schema por sessão de teste. Cada teste individual roda em transação isolada com rollback automático ao final.

**Motivação:** Criação de schema por teste (`scope="function"`) é O(N) e torna pipeline insustentável com crescimento da suíte. Rollback transacional reduz para O(1) mantendo isolamento. Referência: HUMBLE; FARLEY, 2010, p. 375; ADR-033.

**Requisitos:**

1. `integration_engine` com `scope="session"` — engine e `create_all` executados uma vez
2. `integration_session` com `scope="function"` — cada teste recebe sessão em transação
3. Transação revertida automaticamente ao final de cada teste (rollback)
4. Testes **NÃO podem** chamar `session.commit()` — usar `session.flush()` para materializar dados
5. Para testar constraints de unicidade, usar `session.begin_nested()` (savepoint)
6. Compatível com `pytest-xdist` — cada worker recebe engine independente (session scope é por-worker)
7. Foreign keys habilitadas via pragma (SQLite)
8. CI valida ausência de `session.commit()` em arquivos de teste de integração

**Testes esperados:** 5

- `test_br_test_001_schema_created_once`
- `test_br_test_001_rollback_isolates_tests`
- `test_br_test_001_flush_materializes_data`
- `test_br_test_001_commit_not_used_in_tests`
- `test_br_test_001_foreign_keys_enforced`

---

### BR-TEST-002: Cobertura Obrigatória de Caminhos de Erro (NOVA 23/03/2026)

**Regra:** Cada Business Rule DEVE ter, no mínimo, 1 teste de erro por regra definida.

**Motivação:** O projeto possui 1284 testes (mar/2026) com ~82% de cobertura, mas DTs de severidade ALTA escaparam para produção porque os testes cobriam happy paths sem cobrir error paths. Exemplo: DT-057 — `delete_routine` com hábitos vinculados não tinha teste para o cenário de falha. Referências: BECK, 2003, cap. 26; HUMBLE; FARLEY, 2010, p. 186-190; SWEBOK v4.0, cap. 4.4.

**Requisitos:**

1. A seção "Testes" de cada BR deve listar testes de sucesso E testes de erro
2. Se uma BR não lista testes de erro, ela está incompleta
3. Testes de validação de input: strings vazias, acima do limite, tipo errado, formato inválido, ID inexistente
4. Testes de violação de regras de negócio: FK violation, constraint única, estado inválido, operação bloqueada
5. Testes de propagação na TUI: `service_action` retorna erro, `app.notify` exibe, Esc cancela modal
6. Razão mínima happy:error por BR: >= 1:1 (v1.7.0), >= 1:2 (v2.0)

**Checklist para novas BRs:**

- Pelo menos 1 teste de erro por regra definida na BR
- Testes de input inválido para cada campo aceito
- Testes de recurso inexistente (ID inválido)
- Testes de estado inválido (operação fora de sequência)
- Na TUI: teste de que o erro é exibido via `app.notify()`

**Testes esperados:** 1

- `test_br_test_002_all_brs_have_error_tests` (meta-teste — verifica cobertura)

---

### BR-TEST-003: Isolamento Absoluto do Banco de Produção (NOVA 30/05/2026)

**Regra:** Nenhum teste, em nenhuma camada (unit, integration, e2e, bdd), pode resolver `get_db_path()` para o banco de produção XDG (`~/.local/share/atomvs/atomvs.db`). A suíte deve garantir, por construção, que `TIMEBLOCK_DB_PATH` aponta sempre para um banco efêmero (arquivo temporário ou `:memory:`) antes de qualquer acesso a banco.

**Motivação:** O isolamento anterior era parcial e por-camada — `tests/unit/test_tui/conftest.py` forçava `:memory:` apenas para a TUI, `tests/integration/conftest.py` usava `integration_engine` próprio, e os testes CLI dependiam da fixture `isolated_db` (scope função). Qualquer teste que não usasse essas fixturas caía no path XDG default. Com uma instância ATOMVS concorrente tocando esse banco, a contenção de lock SQLite gerava falhas intermitentes (`exit_code 2`), diagnosticadas no DT-078 após eliminação de cinco hipóteses. A ausência de uma guarda global tornava a fragilidade silenciosa: o teste passava ou falhava conforme o ambiente, não conforme o código. Referências: DT-078; ADR-026; ADR-040; HUMBLE; FARLEY, 2010, p. 375.

**Requisitos:**
1. Uma fixture `autouse` de escopo sessão no `tests/conftest.py` (raiz) força `TIMEBLOCK_DB_PATH` para um arquivo temporário caso a variável não esteja definida no ambiente.
2. A guarda usa arquivo temporário (não `:memory:`) por padrão, pois processos CLI via `CliRunner` não compartilham bancos `:memory:` entre conexões.
3. Fixturas mais específicas (`test_tui` com `:memory:`, `isolated_db` com tmp próprio) podem sobrescrever a env por cima — a guarda define apenas o piso seguro.
4. A guarda salva e restaura o valor original de `TIMEBLOCK_DB_PATH` ao final da sessão, sem efeitos colaterais no ambiente do desenvolvedor.
5. Um teste-guarda asserta que `get_db_path()` jamais retorna o path XDG de produção durante a execução da suíte, transformando qualquer regressão de isolamento em falha determinística.
6. A guarda é compatível com `pytest-xdist` (cada worker recebe seu próprio tmp via `tmp_path_factory` com escopo de sessão por-worker).

**Testes esperados:** 2
- `test_br_test_003_db_path_never_resolves_to_production`
- `test_br_test_003_env_var_is_set_during_suite`
