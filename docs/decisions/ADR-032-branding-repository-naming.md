# ADR-032: Branding ATOMVS e Nomenclatura de Repositórios

**Status**: Aceito

**Data**: 2026-02-05

**Relacionado**: ADR-030 (Multiplatform Architecture)

## Contexto

O projeto está em transição de repositório único para ecossistema multi-repo (ADR-030). A organização de repositórios precisa de um namespace consistente que comunique identidade do produto, escale para múltiplos componentes e funcione como branding profissional para portfolio.

O nome original "timeblock-organizer" descreve funcionalidade mas não carrega identidade própria. Com a expansão para terminal, API, web e mobile, um prefixo de branding unifica o ecossistema.

A ferramenta combina Time Blocking com princípios de Atomic Habits (James Clear), posicionando-se como híbrido entre calendar, daily planner e habit tracker. O nome deve refletir essa identidade única.

## Decisão

### 1. Branding: ATOMVS

O projeto adota **ATOMVS** como marca. A referência a "Atomic" (Atomic Habits) com estética latina (V substituindo U) comunica a filosofia do projeto sem ser literal.

### 2. Namespace de Repositórios: `atomvs-timeblock-*`

Todos os repositórios seguem o padrão `atomvs-timeblock-<componente>`:

```
atomvs-timeblock/                  # GitHub Organization
│
├── atomvs-timeblock-contracts     # OpenAPI, Protobuf, AsyncAPI
│
├── # --- BACKEND CORE ---
├── atomvs-timeblock-api           # Spring Boot (BRs, auth, CRUD)
├── atomvs-timeblock-gateway       # Spring Cloud Gateway
├── atomvs-timeblock-sync          # Go + Kafka
├── atomvs-timeblock-notifications # Spring Boot (email, push)
│
├── # --- BFFs ---
├── atomvs-timeblock-bff-web       # Spring Boot
├── atomvs-timeblock-bff-terminal  # Go ou Python
│
├── # --- CLIENTS ---
├── atomvs-timeblock-terminal      # Python (CLI + TUI)
├── atomvs-timeblock-web           # Angular + TypeScript
├── atomvs-timeblock-mobile        # Kotlin Full-Stack
├── atomvs-timeblock-desktop       # Tauri (Rust + Svelte/Angular)
│
└── # --- INFRA ---
    └── atomvs-timeblock-infra     # Docker, K8s, Terraform, Ansible
```

### 3. Comando CLI: Decisão Adiada

A mudança do comando `timeblock` para `atomvs` é uma decisão separada que pode ser tomada posteriormente. Renomear o entry point é trivial comparado à reorganização de repositórios. O branding de repositório não precisa espelhar o comando CLI 1:1.

### 4. Migração

A renomeação de repositórios acontece quando a GitHub Organization for criada (planejado para v2.0.0). Repositórios atuais (GitLab + GitHub) mantêm nomes existentes até a migração.

## Alternativas Consideradas

### atomvs-timeblocking-terminal

O gerúndio "timeblocking" enfatiza o processo/metodologia. Mais descritivo, porém adiciona caracteres sem ganho semântico. Em URLs e imports fica mais longo sem necessidade.

### atomvs-timeblocker-terminal

"timeblocker" refere ao agente (ferramenta ou usuário que bloqueia tempo). Introduz ambiguidade: é a pessoa? É o app? Menos neutro que "timeblock".

### timeblock-terminal (sem prefixo ATOMVS)

Funcional e conciso, mas sem identidade de marca. Não escala como branding para ecossistema de produto.

### timeblock-organizer (nome atual)

O sufixo "organizer" é genérico e não agrega valor ao namespace multi-repo. Cada repositório já descreve seu componente (terminal, api, web).

## Consequências

### Positivas

- Namespace unificado e profissional para ecossistema multi-repo
- "timeblock" mantém consistência com nomenclatura técnica existente (comando CLI, classes, pacotes)
- ATOMVS comunica identidade e filosofia do projeto
- Padrão `atomvs-timeblock-*` é curto, memorável e escalável
- Branding forte para portfolio e apresentação profissional

### Negativas

- Prefixo longo para URLs de repositório (mitigado: nomes individuais curtos)
- Eventual necessidade de renomear repositórios existentes (one-time cost)
- Potencial confusão se comando CLI permanecer `timeblock` enquanto repo é `atomvs-timeblock-terminal`

### Neutras

- Não afeta código existente nem estrutura interna de pacotes
- Migração acontece apenas quando GitHub Organization for criada
- Comando CLI pode ou não ser renomeado independentemente

## Referências

- [ADR-030](ADR-030-multiplatform-architecture.md) - Arquitetura Multi-Plataforma
- [architecture.md](../core/architecture.md) seção 13 - Organização de Repositórios
