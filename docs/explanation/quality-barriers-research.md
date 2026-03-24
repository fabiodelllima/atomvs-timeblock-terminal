# Barreiras de Qualidade de Código na Indústria

**Criado:** 2026-03-23

**Status:** Notas de pesquisa — aguardando aprofundamento

---

## 1. Camadas de Enforcement
```
Desenvolvedor local     →  Editor (LSP, linters, formatters)
Pre-commit hooks        →  ruff, mypy, testes rápidos
CI/CD pipeline          →  Testes completos, SAST, DAST, coverage gates
Code review             →  Humano ou AI-assisted
Post-merge              →  Smoke tests, canary deploy, monitoring
```

## 2. Ferramentas por Categoria

### Linters e Formatters Customizados

| Empresa | Ferramenta | Propósito |
| ------- | ---------- | --------- |
| Google | buildifier, Error Prone, clang-tidy | Formatação BUILD, análise estática Java/C++ |
| Meta | Infer | Análise estática inter-procedural |
| Uber | NullAway | Eliminação de NullPointerException |
| Airbnb | eslint-config-airbnb | Regras JS/TS opinativas |

### Architectural Fitness Functions

| Ferramenta | Linguagem | Propósito |
| ---------- | --------- | --------- |
| ArchUnit | Java | Testes de arquitetura |
| import-linter | Python | Regras de importação entre camadas |
| deptry | Python | Imports de dependências não declaradas |

### Coverage Gates

| Abordagem | Descrição |
| --------- | --------- |
| Threshold global | Pipeline falha se cobertura < X% |
| Diff coverage | Novo código deve ter >= 90% |
| Ratchet | Threshold só sobe, nunca desce |

## 3. Recomendações para ATOMVS

### Curto prazo (v1.7.0)

1. import-linter — formalizar BR-TUI-009 como regra automatizada
2. Diff coverage — novo código com >= 90%
3. Checklist por tipo de MR

### Médio prazo (v1.8.0)

4. semgrep — regras customizadas (ex: "service_action retorno não pode ser ignorado")
5. Testes de arquitetura em `tests/architecture/`
6. Quality gate no MR

### Longo prazo (v2.0)

7. SonarQube ou CodeClimate
8. Container scanning (trivy)
9. Testes de resiliência (fault injection)

## 4. Tópicos para Pesquisa Aprofundada

- import-linter: configuração detalhada para o ATOMVS
- semgrep: regras customizadas para patterns Python
- Diff coverage: integração com pytest-cov e GitLab CI
- ArchUnit for Python: alternativas maduras
