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
