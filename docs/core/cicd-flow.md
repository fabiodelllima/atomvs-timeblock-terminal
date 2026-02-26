# CI/CD Flow

## Visão Geral

O sistema de CI/CD do TimeBlock Organizer implementa uma estratégia de proteção em múltiplas camadas, projetada para detectar problemas de qualidade o mais cedo possível no ciclo de desenvolvimento. Esta abordagem shift-left, originária das práticas de DevSecOps, garante que código quebrado seja bloqueado antes de chegar aos repositórios remotos, economizando tempo de desenvolvimento e mantendo os branches principais sempre em estado deployável. A filosofia central é simples: quanto mais cedo um problema é detectado, menor o custo de correção. Um bug encontrado no pre-commit hook custa segundos para corrigir; o mesmo bug descoberto em produção pode custar horas ou dias.

## Arquitetura Dual-Repo

A arquitetura dual-repo estabelece o GitLab como repositório principal de desenvolvimento e o GitHub como showcase público para recrutadores e colaboradores externos. Esta separação permite manter todo o histórico de desenvolvimento, branches experimentais e discussões internas no GitLab, enquanto o GitHub apresenta apenas o código polido e pronto para demonstração. A sincronização entre os repositórios acontece automaticamente através do job sync:github, que executa após cada pipeline bem-sucedida em qualquer branch, garantindo que o showcase público e o contribution graph estejam sempre atualizados sem intervenção manual.

```
┌─────────────────────────────────────────────────────────────────┐
│                        DESENVOLVEDOR                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ git push origin <branch>
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GITLAB (Fonte de Verdade)                     │
├─────────────────────────────────────────────────────────────────┤
│ 1. Pipeline CI executa (7 jobs)                                 │
│ 2. MR criado e revisado                                         │
│ 3. Merge para develop                                           │
│ 4. Job sync:github espelha automaticamente                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ sync:github (automático)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB (Showcase Público)                    │
├─────────────────────────────────────────────────────────────────┤
│ - Espelho atualizado automaticamente                            │
│ - PRs apenas para contribuições externas                        │
│ - Merge Queue disponível para PRs externos                      │
└─────────────────────────────────────────────────────────────────┘
```

## Fluxo Completo

O fluxo de CI/CD representa a jornada completa de um commit desde sua criação local até a sincronização final com o GitHub. Cada etapa adiciona uma camada de validação, criando um sistema de defesa em profundidade onde múltiplos checkpoints garantem que apenas código de alta qualidade seja integrado. A redundância é intencional: mesmo que um desenvolvedor esqueça de rodar os testes manualmente, os hooks automáticos e as pipelines remotas funcionam como redes de segurança que impedem a propagação de código defeituoso.

```
┌─────────────────────────────────────────────────────────────────┐
│                     DESENVOLVEDOR                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ git commit
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 1: PRE-COMMIT HOOK (Local)                               │
├─────────────────────────────────────────────────────────────────┤
│ [OK] Ruff (linting)                                             │
│ [OK] Ruff format (formatting)                                   │
│ [OK] Mypy (type checking)                                       │
│ [OK] Pytest (unit + integration + bdd + e2e)                    │
├─────────────────────────────────────────────────────────────────┤
│ PASS => Commit criado                                           │
│ FAIL => Commit BLOQUEADO                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ git push origin <branch>
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 2: PRE-PUSH HOOK (Local)                                 │
├─────────────────────────────────────────────────────────────────┤
│ [OK] Pytest (suite completa)                                    │
├─────────────────────────────────────────────────────────────────┤
│ PASS => Push permitido                                          │
│ FAIL => Push BLOQUEADO                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 3: GITLAB CI (.gitlab-ci.yml)                            │
├─────────────────────────────────────────────────────────────────┤
│ Stage: test (paralelo)                                          │
│   - test:unit         (696 tests)                               │
│   - test:integration  (83 tests)                                │
│   - test:bdd          (52 tests)                                │
│   - test:e2e          (42 tests)                                │
│   - test:lint         (ruff check)                              │
│   - test:typecheck    (mypy)                                    │
│                                                                 │
│ Stage: build                                                    │
│   - build:docs        (mkdocs)                                  │
│                                                                 │
│ Stage: sync                                                     │
│   - sync:github       (espelha para GitHub)                     │
├─────────────────────────────────────────────────────────────────┤
│ PASS => Pipeline verde, sync:github executa                     │
│ FAIL => Pipeline vermelha, sync bloqueado                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Criar MR no GitLab
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 4: BRANCH PROTECTION (GitLab)                            │
├─────────────────────────────────────────────────────────────────┤
│ [OK] Push access: No one (apenas via MR)                        │
│ [OK] Merge access: Maintainers                                  │
│ [OK] Pipeline must succeed                                      │
│ [OK] Force push: Disabled                                       │
├─────────────────────────────────────────────────────────────────┤
│ PASS => Merge button ENABLED                                    │
│ FAIL => Merge button DISABLED                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Merge MR (squash)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DEVELOP BRANCH                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ sync:github (automático)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB SINCRONIZADO                          │
└─────────────────────────────────────────────────────────────────┘
```

## Camada 1: Pre-Commit Hook

A primeira linha de defesa é o hook pre-commit, que executa automaticamente antes de cada commit ser criado localmente. Esta camada é crucial porque fornece feedback imediato ao desenvolvedor enquanto o contexto do código ainda está fresco em sua mente. O hook executa quatro verificações essenciais: linting com Ruff para detectar problemas de estilo e anti-patterns, formatação automática para manter consistência visual, type checking com Mypy para validar anotações de tipo, e a suite completa de 873 testes para garantir que nenhuma funcionalidade foi quebrada. Se qualquer verificação falhar, o commit é bloqueado completamente e o desenvolvedor recebe mensagens claras sobre o que precisa ser corrigido. O tempo de execução de 13-15 segundos é um investimento mínimo comparado ao custo de descobrir problemas mais tarde no ciclo.

## Camada 2: Pre-Push Hook

O hook pre-push adiciona uma segunda camada de proteção local, executando imediatamente antes do código ser enviado para os repositórios remotos. Esta camada executa novamente a suite completa de 873 testes, garantindo que mudanças incrementais desde o último commit não introduziram regressões. Embora possa parecer redundante executar os mesmos testes duas vezes, esta redundância é intencional: commits podem ser feitos em sequência rápida, e o pre-push garante que o estado final antes do push está correto. O custo de 13-15 segundos de execução local é insignificante comparado ao tempo que seria perdido se testes falhassem no CI remoto, onde o feedback demora aproximadamente 1m30s.

## Camada 3: GitLab CI

A pipeline do GitLab CI representa a validação autoritativa do código, executando em um ambiente limpo e reproduzível que elimina variações do ambiente local do desenvolvedor. Os 778 testes executam em um único job consolidado (test:all) junto com lint, typecheck, coverage, security (bandit + deps) e sync, totalizando 7 jobs. O stage sync espelha automaticamente o código para o GitHub após cada pipeline bem-sucedida em qualquer branch. Esta separação em stages garante que a sincronização só ocorra quando todo o código passou por todas as validações.

## Camada 4: Branch Protection

A proteção de branch é a camada final implementada diretamente na plataforma Git, funcionando como última barreira antes do merge. No GitLab, a branch develop está configurada para bloquear push direto (todo código deve passar por MR), exigir que a pipeline seja bem-sucedida antes do merge, e desabilitar force push para preservar o histórico. Esta configuração garante que mesmo um mantenedor com pressa não consiga bypassar acidentalmente as validações. O botão de merge só é habilitado quando todas as condições são satisfeitas, tornando impossível integrar código que não passou por todo o pipeline de qualidade.

## GitHub Actions e Merge Queue

O GitHub Actions está configurado para validar Pull Requests de contribuidores externos e suportar o recurso Merge Queue para times que precisam de alta velocidade de integração. O evento merge_group permite que múltiplos PRs sejam testados juntos antes do merge, garantindo que não há conflitos entre mudanças concorrentes. Para o fluxo interno de desenvolvimento, onde o GitLab é a fonte de verdade, o GitHub Actions serve principalmente como validação secundária e para demonstrar aos recrutadores que o projeto mantém padrões de qualidade em ambas as plataformas.

```yaml
on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]
  merge_group:
    branches: [develop, main]
```

### Proteção do GitHub

A proteção da branch develop no GitHub está configurada de forma a permitir a sincronização automática do GitLab enquanto mantém validações para PRs externos. A opção strict está desabilitada para evitar que a sincronização exija re-execução de testes que já passaram no GitLab. A opção enforce_admins também está desabilitada para permitir que o token de sincronização faça push sem ser bloqueado pelas regras de proteção. Force push permanece desabilitado para segurança, garantindo que o histórico não seja reescrito acidentalmente.

| Configuração           | Valor    | Motivo                  |
| ---------------------- | -------- | ----------------------- |
| required_status_checks | 5 checks | lint, test (4x)         |
| strict                 | false    | Permite sync sem re-run |
| enforce_admins         | false    | Permite sync automático |
| allow_force_pushes     | false    | Segurança               |

## Sincronização Automática

O job sync:github é o componente que conecta os dois repositórios, executando automaticamente após cada pipeline bem-sucedida em qualquer branch. O job executa no container Docker padrão (python:3.13), adiciona o remote GitHub dinamicamente, e faz push forçado para o GitHub usando um token com scopes repo e workflow. A opção --mirror garante que tags, branches e todas as referências sejam sincronizadas, mantendo os dois repositórios como cópias idênticas. O uso de when: on_success garante que a sincronização só ocorre quando todos os testes passaram, evitando que código quebrado seja publicado no showcase.

```yaml
sync:github:
  stage: sync
  image: alpine:latest
  before_script:
    - apk add --no-cache git
  script:
    - git clone --mirror "$CI_REPOSITORY_URL" repo.git
    - cd repo.git
    - git remote add github "https://x-access-token:${GITHUB_TOKEN}@github.com/..."
    - git push github --mirror --force
  only:
    - develop
    - main
  when: on_success
```

### Requisitos do Token

O token armazenado na variável GITHUB_TOKEN no GitLab CI/CD deve ter permissões adequadas para realizar a sincronização completa. O scope repo fornece controle total sobre repositórios, permitindo push para branches protegidas quando enforce_admins está desabilitado. O scope workflow é necessário porque a sincronização inclui arquivos em .github/workflows, e o GitHub bloqueia atualizações nesses arquivos sem permissão explícita. O token deve ser configurado como variável masked e protected no GitLab para evitar exposição em logs.

## Matriz de Bloqueios

Esta matriz resume onde cada camada atua, qual gatilho a dispara, se ela bloqueia ativamente o fluxo, quantos testes executa e se existe forma de bypass. A existência de bypass (--no-verify) para hooks locais é intencional para emergências, mas seu uso é fortemente desencorajado e deve ser justificado. As camadas remotas não possuem bypass acessível a desenvolvedores regulares, garantindo que as proteções não possam ser contornadas por conveniência.

| Etapa             | Trigger          | Bloqueia     | Testes | Bypass        |
| ----------------- | ---------------- | ------------ | ------ | ------------- |
| Pre-commit        | `git commit`     | SIM (local)  | 873    | `--no-verify` |
| Pre-push          | `git push`       | SIM (local)  | 873    | `--no-verify` |
| GitLab CI         | Push to remote   | NÃO (marca)  | 873    | N/A           |
| Branch Protection | Merge MR         | SIM (remoto) | N/A    | Admin         |
| sync:github       | Pipeline success | N/A          | N/A    | N/A           |

## Tempos de Execução

O tempo total desde o commit local até a sincronização com o GitHub é de aproximadamente 3 minutos, sendo que a maior parte desse tempo é ocupada pela pipeline remota. Os hooks locais executam em 13-15 segundos cada, fornecendo feedback rápido durante o desenvolvimento. A pipeline GitLab executa em paralelo, completando em aproximadamente 1m30s. O job de sincronização adiciona cerca de 30 segundos ao final do processo. Este tempo total é otimizado para permitir iteração rápida sem sacrificar qualidade.

| Etapa                       | Duração | Testes |
| --------------------------- | ------- | ------ |
| Pre-commit                  | 13-15s  | 873    |
| Pre-push                    | 13-15s  | 873    |
| GitLab CI (paralelo)        | ~1m30s  | 873    |
| sync:github                 | ~30s    | N/A    |
| **Total (local => GitHub)** | ~3min   | 873    |

## Cobertura de Testes

A distribuição de testes segue a pirâmide de testes tradicional, com a maioria dos testes sendo unitários (79.7%) que executam rapidamente e testam componentes isolados. Os testes de integração (9.5%) validam a interação entre componentes, enquanto os testes BDD (6.0%) documentam comportamentos em linguagem natural. Os testes E2E (4.8%) validam fluxos completos da aplicação CLI. A cobertura total de 76% indica que a maior parte do código está sendo exercitada pelos testes, com margem para melhorias em áreas específicas identificadas pela análise de cobertura.

```
test:unit         => 696 tests => 79.7%
test:integration  =>  83 tests =>  9.5%
test:bdd          =>  52 tests =>  6.0%
test:e2e          =>  42 tests =>  4.8%
─────────────────────────────────────────
TOTAL             => 873 tests => Cobertura: 76%
```

## Workflow Recomendado

### Desenvolvimento Normal

O fluxo de desenvolvimento interno utiliza o GitLab como plataforma principal. O desenvolvedor cria uma feature branch, desenvolve e commita normalmente (os hooks validam automaticamente), faz push para o GitLab, cria um Merge Request através da CLI ou interface web, aguarda a pipeline passar e então faz merge. Após o merge, o job sync:github sincroniza automaticamente o código para o GitHub, eliminando a necessidade de qualquer intervenção manual para manter o showcase atualizado.

```bash
# 1. Criar feature branch
git checkout -b feat/nova-funcionalidade

# 2. Desenvolver e commitar (pre-commit valida)
git add .
git commit -m "feat(scope): Descrição"

# 3. Push para GitLab (pre-push valida)
git push origin feat/nova-funcionalidade

# 4. Criar MR no GitLab
glab mr create --target-branch develop

# 5. Aguardar pipeline e fazer merge
glab mr merge <number> --squash --yes

# 6. GitHub sincronizado automaticamente
```

### Contribuições Externas

Contribuidores externos que não têm acesso ao GitLab podem contribuir através do GitHub. Eles fazem fork do repositório, criam uma branch com suas mudanças, e abrem um Pull Request. O GitHub Actions valida o código e, se aprovado, um mantenedor pode fazer merge usando o Merge Queue. O código será então sincronizado de volta para o GitLab na próxima sincronização manual ou através de um processo de integração reversa configurado pelo mantenedor.

```bash
# 1. Fork e clone
# 2. Criar branch e PR
# 3. GitHub Actions valida
# 4. Merge Queue processa (se habilitado)
# 5. Maintainer sincroniza para GitLab
```

## Arquivos de Configuração

A configuração do CI/CD está distribuída em três arquivos principais que trabalham em conjunto para implementar todas as camadas de proteção. O .pre-commit-config.yaml define os hooks locais que executam ruff, mypy e pytest. O .gitlab-ci.yml define a pipeline completa do GitLab incluindo todos os stages de test, build e sync. O .github/workflows/ci.yml define os checks do GitHub Actions e habilita o suporte a Merge Queue através do evento merge_group.

```
.pre-commit-config.yaml       => Hooks locais (ruff, mypy, pytest)
.gitlab-ci.yml                => Pipeline GitLab (7 jobs incluindo sync)
.github/workflows/ci.yml      => GitHub Actions (6 checks + merge_group)
```

## Troubleshooting

### Sync Falhou

Quando o job sync:github falha, o primeiro passo é verificar os logs da pipeline para identificar a causa. Os problemas mais comuns são token expirado ou com scopes insuficientes, branch protection bloqueando o push, ou problemas de rede. O token pode ser verificado e atualizado através das variáveis do GitLab CI/CD. Se o problema for branch protection, verifique se enforce_admins está desabilitado no GitHub.

```bash
# Verificar logs
glab ci view -b develop

# Verificar token
glab variable list | grep GITHUB_TOKEN

# Re-executar
glab api --method POST "projects/:id/pipelines/<id>/retry"
```

### Branch Protection Bloqueando

Se a sincronização está sendo bloqueada pela proteção de branch do GitHub, verifique a configuração enforce_admins. Esta opção deve estar desabilitada (false) para permitir que tokens façam push sem passar pelos required status checks. A configuração pode ser verificada e alterada através da API do GitHub ou interface web.

```bash
# Verificar proteção GitHub
gh api repos/<owner>/<repo>/branches/develop/protection | jq '.enforce_admins'

# Deve ser {"enabled": false} para sync funcionar
```

---

**Versão:** 2.0

**Última atualização:** 2026-02-03
