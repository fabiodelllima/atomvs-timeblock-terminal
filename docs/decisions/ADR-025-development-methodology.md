# ADR-025: Engenharia de Requisitos

**Status:** Aceito (Revisado)

**Data:** 2026-02-08

**Supersedes:** Versão original (2025-11-08) que definia a hierarquia como "Docs > BDD > TDD > Code"

## Contexto

O projeto necessitava de um processo de desenvolvimento formal que garantisse rastreabilidade entre requisitos, testes e código. A versão original desta ADR definia uma hierarquia informal "Docs > BDD > TDD > Code" que, embora funcional, não referenciava disciplinas estabelecidas de engenharia de software.

A prática adotada desde o início do projeto corresponde ao ciclo clássico de Engenharia de Requisitos: elicitação e especificação formal de requisitos (BRs), validação com cenários executáveis (BDD), verificação automatizada (TDD) e implementação guiada por requisitos verificados. A revisão formaliza essa correspondência com terminologia e referências normativas adequadas.

## Decisão

Adotar técnicas de **Engenharia de Requisitos** como princípio organizador do processo de desenvolvimento, mapeando as práticas existentes para o ciclo formal da disciplina:

| Fase               | Atividade RE (29148)           | Prática no Projeto        |
| ------------------ | ------------------------------ | ------------------------- |
| Especificação      | Requirements specification     | BRs formalizadas (BR-XXX) |
| Validação          | Requirements validation        | Cenários BDD (Gherkin)    |
| Verificação        | Software verification          | TDD (unit/integ/e2e)      |
| Implementação      | Software construction          | Código em src/timeblock/  |
| Rastreabilidade    | Requirements traceability      | Matriz BR → Test → Code   |
| Gestão de mudanças | Requirements change management | ADRs                      |

**Normas de referência:**

- ISO/IEC/IEEE 29148:2018 — Systems and software engineering — Life cycle processes — Requirements engineering
- SWEBOK v4.0 — Software Engineering Body of Knowledge, Chapters 1 (Requirements) and 10 (Testing)
- ISO/IEC 12207:2017 — Systems and software engineering — Software life cycle processes

**Princípios imutáveis:**

1. Requisitos são especificados antes de testes e código
2. Testes validam requisitos; quando falham, o código está errado
3. Rastreabilidade bidirecional BR ↔ Test ↔ Code é obrigatória
4. Mudanças em requisitos são gerenciadas via ADRs e versionamento de business-rules.md

## Consequências

**Positivas:**

- Terminologia profissional alinhada com corpo de conhecimento de engenharia de software
- Referência normativa clara para justificar decisões de processo
- Mesmas práticas que já funcionavam, agora com enquadramento acadêmico e profissional adequado
- Facilita comunicação em contextos de portfólio, currículo e entrevistas técnicas

**Negativas:**

- Documentação existente precisa ser atualizada para refletir nova terminologia
- Curva de aprendizado para manter consistência terminológica

**Neutras:**

- As práticas concretas (BRs, Gherkin, TDD, vertical slicing) permanecem idênticas
- Ferramentas e processos não mudam, apenas o framing conceitual

## Documentos Atualizados

| Documento       | Mudança                                                     |
| --------------- | ----------------------------------------------------------- |
| development.md  | SSOT de processo, v2.0.0 com framing RE                     |
| architecture.md | Seção 11 atualizada                                         |
| workflows.md    | Seção 1.3 atualizada                                        |
| roadmap.md      | Princípio 4 já referenciava ISO/IEC/IEEE 29148 (inalterado) |
| ADR-025         | Esta revisão                                                |
