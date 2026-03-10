# ADR-035: Padronização de Keybindings

**Status**: Aceito

**Data**: 2026-03-08

**Relacionado**: ADR-034 (Dashboard-first CRUD), BR-TUI-004 (Global Keybindings), BR-TUI-021 (Timer no Dashboard)

## Contexto

A BR-TUI-004 foi revisada em 02/03/2026 durante a Sprint 3.2 e definiu uma política de modificadores (Ctrl para ações, sem modificador para navegação). A Sprint 4 implementou CRUD via dashboard com keybindings `n/e/x` sem Ctrl e quick actions com `Ctrl+Enter` (done), `Ctrl+S` (skip), `Ctrl+K` (complete task). Simultaneamente, o `app.py` mantinha navegação de screens duplicada em `1-5` e `d/r/h/t/m`.

Três problemas emergiram:

1. **Inconsistência entre BR e código.** A BR-TUI-004 especifica `Ctrl+K` para complete, `Ctrl+X` para deletar, `Ctrl+E` para editar. O código usa `n/e/x` sem Ctrl para CRUD e `Ctrl+K` para complete. `q` encerra sem Ctrl no código, mas a BR exige `Ctrl+Q`.

2. **Letras de navegação bloqueiam ações contextuais.** `d/r/h/t/m` na app.py reservam 5 letras para troca de screen — funcionalidade já coberta por `Ctrl+1..5`. Essas letras ficam indisponíveis para ações de domínio dentro das screens.

3. **Semântica duplicada.** `Ctrl+Enter` marca done em hábitos, mas `Ctrl+K` completa tasks — mesma ação (concluir) com bindings diferentes. O timer planejado (Sprint 4e/5) precisa de stop, que também é "concluir uma sessão". Três bindings para a mesma semântica viola o princípio de consistência.

## Decisão

### 1. Navegação entre screens via Ctrl+1..5

Remover `d/r/h/t/m` do `app.py`. A troca de screen é exclusivamente via `Ctrl+1..5` (1=Dashboard, 2=Rotinas, 3=Hábitos, 4=Tasks, 5=Timer). Números puros `1-9` ficam livres para ações contextuais dentro de cada screen (selecionar item por posição, trocar entre rotinas, etc.).

### 2. Ctrl+Enter como binding universal de "concluir"

`Ctrl+Enter` assume toda ação de conclusão:

- Hábitos: mark done
- Tasks: mark complete (substitui `Ctrl+K`)
- Timer: stop e salvar sessão

A semântica é "finalizar positivamente o item sob contexto". Elimina a necessidade de bindings separados por domínio.

### 3. Ctrl+X como binding universal de "cancelar/descartar"

`Ctrl+X` assume toda ação de cancelamento com perda de dados:

- Timer: cancel (descarta sessão) com ConfirmDialog

Substitui `Ctrl+W` (cancel timer) e unifica com a semântica já existente de "ação destrutiva".

### 4. Shift+Enter para timer start/pause-resume

`Shift+Enter` é o toggle do timer:

- No panel de hábitos: inicia timer no hábito sob cursor
- No panel de timer (timer ativo): alterna entre pause e resume

Substitui `Ctrl+S` para start (que conflitava com skip) e `Ctrl+P` para pause.

### 5. CRUD sem modificador

`n/e/x` permanecem sem Ctrl para CRUD. Essas são ações frequentes e de baixo risco (x abre ConfirmDialog antes de deletar). O padrão é consistente com vim e aplicações TUI como lazygit.

### 6. Ctrl+S exclusivo para skip

Com `Shift+Enter` assumindo start do timer, `Ctrl+S` fica exclusivo para skip de hábitos. Sem ambiguidade.

## Mapa Definitivo

```plaintext
GLOBAIS (app.py):
  Ctrl+1..5 ............ trocar screen
  Ctrl+Q ............... sair [MODAL]
  ? .................... help overlay
  Escape ............... fechar modal / voltar ao Dashboard

NAVEGAÇÃO (intra-screen):
  Tab / Shift+Tab ...... avançar/voltar entre panels
  Setas up/down ........ cursor vertical dentro do panel
  1-9 .................. livres para ações contextuais
  Enter ................ ativar placeholder / selecionar item

CRUD (contextual ao panel focado):
  n .................... novo (FormModal)
  e .................... editar (FormModal)
  x .................... deletar [MODAL]

AÇÕES DE DOMÍNIO:
  Ctrl+Enter ........... concluir (done/complete/stop timer)
  Ctrl+S ............... skip (hábitos)
  Shift+Enter .......... start timer / pause-resume timer
  Ctrl+X ............... cancelar timer [MODAL]

PROIBIDOS (reservados pelo OS):
  Ctrl+C ............... SIGINT
  Ctrl+Z ............... SIGTSTP
  Ctrl+D ............... EOF
```

## Consequências

**Positivas:**

- Uma ação = um binding em todo o app. Não há bindings diferentes para a mesma semântica.
- Números livres para ações contextuais futuras (selecionar item, trocar rotina).
- Letras `d/r/h/t/m` liberadas para uso futuro em ações de domínio.
- Timer integrado com bindings consistentes antes da implementação.

**Negativas:**

- Breaking change: `Ctrl+K` (complete task) e `q` (quit) mudam. Usuários da Sprint 4 precisam reaprender.
- `Shift+Enter` pode não ser capturado em todos os emuladores de terminal — requer teste.

**Mitigação:**

- Help overlay (`?`) atualizado com mapa completo.
- Footer contextual (BR-TUI-007) exibe bindings ativos por panel.
- Se `Shift+Enter` falhar em algum terminal, adicionar binding alternativo (ex: `s` no panel de timer).

## Alternativas Consideradas

### Manter Ctrl+K para complete

Funcional, mas cria precedente de bindings diferentes para a mesma semântica. Cada novo domínio (eventos, projetos) precisaria de mais uma combinação Ctrl+letra. Rejeitada.

### Usar letras sem Ctrl para tudo

Mais simples, mas impede uso de letras em ações contextuais e conflita com navegação. Rejeitada.

### Alt+1..5 para screens

Alternativa a Ctrl+1..5. Rejeitada porque Alt é inconsistente entre emuladores de terminal (especialmente em macOS e tmux).

## Referências

FOWLER, M. _Refactoring: Improving the Design of Existing Code_. 2nd ed. Boston: Addison-Wesley, 2018. ISBN 978-0-13-475759-9.
