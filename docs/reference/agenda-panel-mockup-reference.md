# Mockup de referência — Agenda Panel (aprovado sessão 9)

Este mockup é a referência visual para implementação de ADR-041, DT-062 e BR-TUI-032.

## Regra de renderização por linha (15min)

```
CASO 1 — Linha é o INÍCIO do bloco:
  → "{título} {ícone}"  (sem ▌, sem cor)

CASO 2 — Linha está DENTRO do bloco (inclui linha do horário de término):
  → "▌{cor_sólida}"

CASO 3 — Linha está FORA de qualquer bloco:
  → "· · · ·" ou vazio
```

## Cenário principal: 3 horários em conflito

```
 ┌─ Agenda do Dia ───────────────────────────────────────────┐
 │                                                           │
 │  09:00  │ ·                                               │
 │         │                                                 │
 │  09:30  │ ·                                               │
 │         │                                                 │
 │  10:00  │ Leitura ·                                       │
 │         │ ▌░░░░░░░░░░░░░░                                 │
 │  10:30  │ ▌░░░░░░░░░░░░░░ Treino ·                      │
 │         │ ▌░░░░░░░░░░░░░░ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒                 │
 │  11:00  │ ▌░░░░░░░░░░░░░░ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Meditação ·    │
 │         │ ▌░░░░░░░░░░░░░░ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │  11:30  │ ▌░░░░░░░░░░░░░░ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │         │ · · · · · · · · ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │  12:00  │ · · · · · · · · ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │         │                 ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │  12:30  │ · · · · · · · · ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ▌▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
 │         │                 ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ · · · · · · · · │
 │  13:00  │ · · · · · · · · ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒ · · · · · · · · │
 │         │                 · · · · · · · · · · · · · · · · │
 │  13:30  │ ·                                               │
 │         │                                                 │
 │  14:00  │ ·                                               │
 │         │                                                 │
 └───────────────────────────────────────────────────────────┘

 Horários:
 - Leitura:        10:00 - 11:30 (░)
 - Treino:       10:30 - 13:00 (▒)
 - Meditação:    11:00 - 12:30 (▓)
```

## Cenário: blocos consecutivos sem gap

```
 │  10:30  │ ▌░░░░░░░░░░░░░░░░░░░░░░░ │    ← 10:30 (Leitura)
 │         │ ▌░░░░░░░░░░░░░░░░░░░░░░░ │    ← 10:45
 │  11:00  │ Exercício ·              │    ← bloco 1 termina, bloco 2 começa
 │         │ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │    ← 11:15
 │  11:30  │ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │    ← 11:30
 │         │ ▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │    ← bloco 2 termina 11:45
 │  12:00  │ ·                        │    ← livre
```

## Cenário: bloco alinhado (10:00 - 11:00)

```
 │  10:00  │ Leitura ·                 │    ← início do bloco
 │         │ ▌░░░░░░░░░░░░░░░░░░░░░░░░ │    ← 10:15
 │  10:30  │ ▌░░░░░░░░░░░░░░░░░░░░░░░░ │    ← 10:30
 │         │ ▌░░░░░░░░░░░░░░░░░░░░░░░░ │    ← 10:45
 │  11:00  │ ▌░░░░░░░░░░░░░░░░░░░░░░░░ │    ← 11:00 (última linha COM cor)
 │         │                           │    ← 11:15 livre
```

## Cenário: bloco mínimo 15min (10:00 - 10:15)

```
 │  10:00  │ Leitura ·                  │    ← título (única linha)
 │         │ ·                          │    ← 10:15 livre
```
