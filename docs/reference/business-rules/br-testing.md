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
