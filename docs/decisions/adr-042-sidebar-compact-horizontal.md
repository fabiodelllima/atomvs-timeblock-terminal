# ADR-042: Sidebar compacto — horizontal no header ou oculto com overlay

**Status:** Proposto

## Contexto

O sidebar vertical atual ocupa ~15 colunas (~12% de um terminal 120 cols) com labels textuais completos ("Dash", "Rotin", "Habit", "Tasks", "Timer"). O conteúdo é exclusivamente navegação entre 5 screens — funcionalidade que não justifica espaço permanente, especialmente considerando que a Agenda Panel e os panels direitos competem por largura.

As screens já são acessíveis via atalhos diretos (keybindings numéricos 1-5 planejados). O sidebar serve como mapa visual, não como controle primário.

## Decisão

Implementar `sidebar_mode` configurável com 3 opções:

### a) "horizontal" (recomendado como padrão)

Tabs integradas na linha do header: `◉ D R H T ⏱`. Zero colunas perdidas. Screen ativa destacada visualmente (bold/underline/cor diferente). As tabs fazem parte do widget de header existente.

### b) "hidden"

Sem sidebar visível. Navegação via atalhos numéricos 1-5 ou overlay.

### c) "vertical"

Sidebar compacto com ícones (3-4 cols). Estilo atual reduzido.

### Overlay (em todos os modos)

F1 abre overlay flutuante sobre o conteúdo (não empurra layout) com nomes completos das screens + atalhos numéricos. Conteúdo por trás fica dimmed. Esc ou seleção fecha o overlay. O keybinding `?` permanece no help overlay (sem conflito).

### Atalhos globais

Teclas numéricas 1-5 navegam entre screens em todos os modos:
1 = Dashboard, 2 = Rotinas, 3 = Hábitos, 4 = Tasks, 5 = Timer.

## Consequências

### Positivas

- Modo horizontal: zero perda de espaço, navegação visível.
- Overlay via F1 como referência expandida funciona em qualquer modo.
- Atalhos numéricos dispensam sidebar para navegação rápida.
- Configurável: usuário escolhe o modo preferido.

### Negativas

- Header widget precisa de refatoração para acomodar tabs.
- Overlay flutuante requer implementação de z-ordering no Textual.
- Testes e2e que dependem do sidebar vertical precisam de atualização.
- Configuração `sidebar_mode` precisa de mecanismo de persistência (futuro: config file).

## Referências

- DT-060: Refatoração do sidebar para modo compacto/oculto

---

**Data:** 2026-03-22
