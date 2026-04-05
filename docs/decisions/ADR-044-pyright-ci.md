# ADR-044: Pyright como Job CI de Qualidade

**Status:** Proposed

**Date:** 2026-03-23

## Context

O projeto usa mypy como type checker bloqueante no CI (0 erros). Basedpyright roda localmente no Zed (modo basic) para feedback em tempo real. Porém, basedpyright no modo standard reporta ~190 warnings não capturados pelo mypy.

## Decision

Adotar estratégia de promoção gradual em 3 fases:

**Fase 1 (v1.7.0):** Job CI com `allow_failure: true`. Reporta warnings sem bloquear merge.

**Fase 2 (v1.8.0):** Script wrapper com threshold decrescente. Começa em 150 (abaixo dos 190), reduz 20-30 por sprint.

**Fase 3 (v2.0):** Bloqueante. Zero warnings no modo standard.

## Consequences

Detecção precoce de type errors. Job adicional no pipeline (~3-4min). Considerar migrar de mypy para apenas basedpyright em v2.0.
