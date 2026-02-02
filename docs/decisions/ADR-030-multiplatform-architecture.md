# ADR-030: Arquitetura Multi-Plataforma e Organização de Repositórios

**Status:** Proposto

**Data:** 31 de Janeiro de 2026

**Contexto:** Planejamento v2.0+

---

## Contexto

O TimeBlock Organizer precisa evoluir de CLI local para ecossistema multi-plataforma:

- Terminal (CLI + TUI) - Python
- Web - Angular + TypeScript
- Mobile - Kotlin (frontend e backend)
- Desktop - Tauri (Rust + frontend web)

Cada plataforma tem requisitos específicos de UX, performance e stack tecnológica. Um aplicativo mobile precisa funcionar offline e sincronizar quando houver conexão; uma interface web pode assumir conectividade constante; um CLI precisa ser leve e rápido. Essas diferenças fundamentais exigem backends especializados para cada tipo de cliente.

A arquitetura deve suportar essa diversidade sem criar acoplamento desnecessário, permitindo que cada componente evolua independentemente enquanto mantém consistência através de contratos bem definidos.

### Questões a Resolver

1. Como organizar repositórios?
2. Qual stack para cada componente?
3. Como compartilhar lógica de negócio entre stacks diferentes?
4. Como sincronizar dados offline-first?

## Decisão

### 1. GitHub Organization

Criar organização `timeblock-org` para agrupar todos os repositórios.

A decisão de usar uma GitHub Organization em vez de repositórios pessoais segue as melhores práticas da indústria. Organizações oferecem controle de acesso granular, visibilidade centralizada de todos os projetos relacionados, e refletem a estrutura encontrada em ambientes corporativos. A transferência de repositórios existentes para uma organization é gratuita e preserva todo o histórico, issues e pull requests. O GitHub redireciona automaticamente URLs antigas, minimizando quebras de links externos.

**Justificativa:**

- Controle de acesso granular por repositório
- Visibilidade centralizada de projetos relacionados
- Features de segurança e administração superiores a repos pessoais
- Estrutura escalável para crescimento do projeto

### 2. Um Repositório por Serviço/Client

A estratégia de um repositório por serviço é o padrão estabelecido para arquiteturas de microsserviços. Cada serviço tem seu próprio ciclo de vida, pipeline de CI/CD, e pode ser deployado independentemente. Isso permite que diferentes componentes evoluam em paralelo sem conflitos de merge ou dependências de release.

A estrutura proposta separa claramente backend core (lógica de negócio), BFFs (adaptadores por plataforma), clients (interfaces de usuário), e infraestrutura (IaC e configuração). Essa separação facilita a navegação e deixa explícita a responsabilidade de cada componente.
```
timeblock-org/
│
├── timeblock-contracts       # OpenAPI, Protobuf, AsyncAPI
│
├── # ─── BACKEND CORE ────────────────────────────
├── timeblock-api             # Spring Boot (BRs, auth, CRUD)
├── timeblock-gateway         # Spring Cloud Gateway
├── timeblock-sync            # Go + Kafka
├── timeblock-notifications   # Spring Boot (email, push)
│
├── # ─── BFFs ────────────────────────────────────
├── timeblock-bff-web         # Spring Boot
├── timeblock-bff-terminal    # Go ou Python
│
├── # ─── CLIENTS ─────────────────────────────────
├── timeblock-terminal        # Python (CLI + TUI)
├── timeblock-web             # Angular + TypeScript
├── timeblock-mobile          # Kotlin Full-Stack
├── timeblock-desktop         # Tauri (Rust + Svelte/Angular)
│
└── # ─── INFRA ───────────────────────────────────
    └── timeblock-infra       # Docker, K8s, Terraform, Ansible
```

### 3. Stacks por Componente

A escolha de stack para cada componente considera adequação técnica ao problema e adoção no mercado. Java/Spring domina backends enterprise devido ao ecossistema maduro, tooling excelente e vasta documentação. Go é o padrão para infraestrutura cloud-native, usado em Docker, Kubernetes e Prometheus. Kotlin é a linguagem oficial para Android e oferece Multiplatform para compartilhar código entre cliente e servidor.

| Componente        | Stack                    | Justificativa                                   |
| ----------------- | ------------------------ | ----------------------------------------------- |
| **API Core**      | Java/Spring Boot         | Regras complexas, ecossistema enterprise maduro |
| **Gateway**       | Spring Cloud Gateway     | Consistência com API, features enterprise       |
| **Sync**          | Go + Kafka               | Performance, concorrência, padrão cloud-native  |
| **Notifications** | Spring Boot              | Compartilha libs com API                        |
| **BFF Web**       | Spring Boot              | Alinha com backend Java                         |
| **BFF Terminal**  | Go ou Python             | Leve, alinha com clients                        |
| **Terminal**      | Python (Typer + Textual) | Projeto atual, produtividade                    |
| **Web**           | Angular + TypeScript     | Framework enterprise, tipagem forte             |
| **Mobile**        | Kotlin Full-Stack        | Kotlin Multiplatform (app + backend)            |
| **Desktop**       | Tauri + Rust             | Binário nativo, baixo consumo de recursos       |

### 4. Padrão BFF (Backend For Frontend)

O padrão Backend For Frontend resolve um problema fundamental: diferentes tipos de clientes têm necessidades diferentes. Um app mobile em rede 3G precisa de payloads compactos e paginação agressiva. Uma SPA web pode carregar mais dados de uma vez. Um CLI precisa de respostas estruturadas para parsing.

Netflix, Uber e Spotify adotaram BFF precisamente porque um único backend genérico força compromissos que prejudicam todas as plataformas. Com BFF, cada cliente tem um backend dedicado que entende suas necessidades específicas e otimiza as respostas adequadamente. O BFF também isola mudanças: atualizar a API do app mobile não afeta a web, permitindo evolução independente de cada plataforma.
```
┌────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                │
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│   Web    │  Mobile  │   CLI    │   TUI    │      Desktop       │
└────┬─────┴────┬─────┴────┬─────┴──────┬───┴──────────┬─────────┘
     │          │          └──────┬─────┘              │
     ↓          ↓                 ↓                    ↓
┌──────────┐ ┌────────────┐ ┌──────────────┐     ┌─────────────┐
│ BFF Web  │ │ BFF Mobile │ │ BFF Terminal │     │ BFF Desktop │
│ Spring   │ │   Kotlin   │ │   Go/Python  │     │    Go       │
└────┬─────┘ └────┬───────┘ └─────┬────────┘     └─────┬───────┘
     └────────────┴───────────────┴────────────────────┘
                            │
                            ↓
              ┌─────────────────────────┐
              │      API GATEWAY        │
              │  Spring Cloud Gateway   │
              └───────────┬─────────────┘
                          │
     ┌────────────────────┼────────────────────┐
     ↓                    ↓                    ↓
┌──────────┐       ┌──────────┐        ┌──────────┐
│ API Core │       │   Sync   │        │  Notif   │
│  Spring  │       │   Go     │        │  Spring  │
└──────────┘       └──────────┘        └──────────┘
```

### 5. Mobile com Kotlin Full-Stack

O repositório mobile usa Kotlin Multiplatform para compartilhar código entre o app Android e seu BFF. Essa abordagem elimina divergências entre modelos de dados do cliente e servidor - um problema comum que causa bugs sutis em runtime.

Ktor, o framework web da JetBrains, integra naturalmente com o ecossistema Kotlin. O resultado é type-safety end-to-end: se um campo muda no backend, o app não compila até ser atualizado, transformando erros de runtime em erros de compilação.
```
timeblock-mobile/
├── app/                      # Android (Jetpack Compose)
├── backend/                  # Ktor (BFF Mobile)
└── shared/                   # Modelos compartilhados
```

### 6. Contratos Compartilhados

Em arquiteturas distribuídas, contratos são a cola que mantém tudo junto. O repositório `timeblock-contracts` é a fonte de verdade para todas as interfaces entre serviços. Mudanças incompatíveis são detectadas antes do deploy através de validação automatizada no CI/CD.

OpenAPI documenta as REST APIs de forma que ferramentas podem gerar clients automaticamente. Protobuf define mensagens binárias eficientes para comunicação gRPC entre serviços internos. AsyncAPI documenta eventos Kafka, especificando producers e consumers. JSON Schema valida payloads em runtime.

Essa abordagem contract-first inverte o fluxo tradicional: em vez de implementar e depois documentar, define-se o contrato primeiro e implementa-se contra ele.

- **OpenAPI** - REST APIs
- **Protobuf** - gRPC entre serviços
- **AsyncAPI** - Eventos Kafka
- **JSON Schema** - Validação de dados

### 7. Infrastructure as Code (IaC)

O repositório `timeblock-infra` centraliza toda configuração de infraestrutura como código. Isso garante que ambientes são reproduzíveis, versionados e auditáveis - eliminando configurações manuais não documentadas.

Terraform provisiona recursos cloud (VMs, redes, databases) de forma declarativa. Ansible configura esses recursos após criados (instalar Docker, configurar firewall). Kubernetes orquestra containers em produção. Docker Compose simplifica desenvolvimento local e deployments em homelab.
```
timeblock-infra/
├── terraform/                # Provisioning (cloud resources)
│   ├── modules/
│   │   ├── networking/
│   │   ├── database/
│   │   ├── kubernetes/
│   │   └── monitoring/
│   └── environments/
│       ├── dev/
│       ├── staging/
│       └── prod/
│
├── ansible/                  # Configuration Management
│   ├── playbooks/
│   │   ├── setup-pi.yml      # Raspberry Pi setup
│   │   └── deploy-app.yml
│   └── roles/
│       ├── docker/
│       ├── postgresql/
│       └── monitoring/
│
├── kubernetes/               # Orquestração (v3.0+)
│   ├── base/
│   │   ├── api/
│   │   ├── gateway/
│   │   ├── sync/
│   │   └── notifications/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── prod/
│
├── docker/                   # Compose para dev/homelab
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   └── docker-compose.pi.yml
│
└── scripts/                  # Automação
    ├── deploy.sh
    ├── backup.sh
    └── restore.sh
```

**Progressão de IaC por versão:**

| Versão | Ferramenta               | Uso                                |
| ------ | ------------------------ | ---------------------------------- |
| v1.5.0 | Docker Compose           | Dev local, CI/CD                   |
| v2.0.0 | Docker Compose + Ansible | Raspberry Pi homelab               |
| v2.0.0 | Terraform (opcional)     | Cloud (DigitalOcean, AWS)          |
| v3.0.0 | Kubernetes + Helm        | Orquestração de microsserviços     |

### 8. Estratégia de Migração

A migração para a arquitetura multi-plataforma será incremental, validando cada fase antes de prosseguir. Cada repositório é criado quando há código pronto para ele, evitando estruturas vazias.

- **Fase 1 (Atual):** Finalizar CLI + TUI no repo atual
- **Fase 2:** Criar organization, transferir repo como `timeblock-terminal`
- **Fase 3:** Criar `timeblock-api` (Spring Boot) e `timeblock-contracts`
- **Fase 4:** Criar demais serviços conforme necessidade

## Consequências

### Positivas

- **Diversidade tecnológica:** Java/Spring, Go, Kotlin, Rust, Angular, Terraform, Kubernetes
- **Arquitetura escalável:** BFF, API Gateway, Event-Driven, IaC
- **Independência de deploy:** Cada serviço evolui independentemente
- **Padrão de mercado:** Arquitetura similar a Netflix, Uber, Spotify

### Negativas

- Complexidade de gestão de múltiplos repos
- Overhead de manter contratos sincronizados
- Curva de aprendizado de múltiplas stacks

### Neutras

- Requer disciplina de documentação
- CI/CD por repositório

## Referências

- [Netflix BFF Pattern](https://netflixtechblog.com/seamlessly-swapping-the-api-backend-of-the-netflix-android-app-3d4317155187)
- [Sam Newman - Backends For Frontends](https://samnewman.io/patterns/architectural/bff/)
- [GitHub Best Practices for Organizations](https://github.blog/enterprise-software/devops/best-practices-for-organizations-and-teams-using-github-enterprise-cloud/)
- [Microservices Best Practices](https://github.com/katopz/best-practices/blob/master/best-practices-for-building-a-microservice-architecture.md)
- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [Ansible Documentation](https://docs.ansible.com/)

## Notas

Esta ADR complementa:

- **ADR-023:** Microservices de domínio (MedBlock, EventBlock)
- **ADR-012:** Sync Strategy (Kafka)
- **ADR-006:** Textual TUI
- **ADR-024:** Homelab Infrastructure

A implementação será incremental, começando pelo terminal (CLI + TUI) antes de migrar para organization.
