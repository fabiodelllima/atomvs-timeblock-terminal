# ADR-046: Padrão de Datas e Versionamento em Documentos

**Status:** Proposed

**Date:** 2026-03-23

## Context

Documentos em `docs/` têm inconsistência: alguns têm data, outros não. Alguns têm versão, outros não. Não há regra sobre quais campos são obrigatórios. Dificulta saber se um documento está atualizado ou abandonado.

## Decision

Regra geral: se o documento tem campo `Versão:`, deve ter `Última atualização:`.

Por categoria Diátaxis:

| Categoria        | Campos obrigatórios                     |
| ---------------- | --------------------------------------- |
| Reference (SSOT) | Versão, Última atualização, Changelog   |
| Reference (BRs)  | Última atualização                      |
| Decisions (ADRs) | Date (formato Nygard)                   |
| Explanation      | Criado em, Última revisão (se revisado) |
| Tutorial/Howto   | Criado em, Última validação             |

Formato de data: `DD de Mês de AAAA` em cabeçalhos, `AAAA-MM-DD` (ISO 8601) em tabelas e ADRs.

## Consequences

Todos os documentos ficam rastreáveis temporalmente. Implementação requer sprint de padronização (`docs/standardize-headers`). Possível validação automatizada no CI.
