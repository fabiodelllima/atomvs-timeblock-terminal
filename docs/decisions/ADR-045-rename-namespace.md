# ADR-045: Rename do Namespace timeblock para atomvs

- **Status:** Proposto (v2.0)

**Date:** 2026-03-23

## Context

O código usa `from timeblock.xxx` mas o produto se chama ATOMVS Time Planner Terminal. O repo é `atomvs-timeblock-terminal` mas o package Python é `timeblock`. Inconsistência entre nome externo e namespace interno.

## Decision

Renomear `src/timeblock/` para `src/atomvs/` na v2.0, antes da API REST (que expõe o namespace publicamente).

## Impact

~190 arquivos afetados (imports em src/ e tests/, pyproject.toml, CI/CD, Dockerfiles, mkdocs.yml, README, docs, logger namespace, conftest). Script automatizado de find-and-replace + validação completa.

## Consequences

Alinhamento completo entre branding e código. Sprint dedicado de ~4h. Histórico de blame perde continuidade nos arquivos renomeados. Não é bloqueador para v1.7.0.
