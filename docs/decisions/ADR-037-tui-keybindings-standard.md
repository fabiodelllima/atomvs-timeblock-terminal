# ADR-037: Padrão de Keybindings da TUI

- **Status:** Aceito
**Contexto:** Definir padrão consistente de teclas para o ATOMVS Time Planner Terminal

---

## Contexto

A TUI precisa de um mapa de teclas intuitivo para uso diário. A pesquisa
cobriu calcurse, calcure, gitui, taskwarrior-tui, superfile, kabmat e
outros projetos listados em awesome-tuis e vim-keybindings-everywhere.

---

## Padrões identificados

### Convenções universais em TUIs produtivas

Navegação vim-like (j/k/h/l ou setas) é o padrão dominante. Tab alterna
entre panels/regiões. Números (1-5) alternam screens/tabs. ? abre help.
q ou Ctrl+Q sai. A barra de status mostra ações disponíveis no contexto.

### Calcure (calendário+tarefas TUI, Python)

a = adicionar, e = editar, d = deletar, v = marcar como done, u = desmarcar,
h/l = prioridade alta/baixa, m = mover, space = alternar entre panels,
/ = toggle split, ? = help, q = sair, g = ir para data.

### Calcurse (calendário TUI, C/ncurses)

a = adicionar, e = editar, d = deletar, Tab = alternar panels,
? = help, C = configuração, o = anexar nota, i = importar.
Status bar mostra ações contextuais.

### GitUI (git TUI, Rust)

Enter = expandir/confirmar, j/k = navegar, Tab = alternar panels,
c = commit, s = stage, e = edit. Contexto determina a ação.

### Padrão mnemônico com letras simples

A tendência principal é letras minúsculas para ações comuns, maiúsculas
para variantes ou ações batch. Modificadores (Ctrl) reservados para
ações de sistema (sair, salvar) ou ações "perigosas" (cancelar timer,
completar item).

---

## Decisão

### Mapa de keybindings do ATOMVS

#### Globais (qualquer screen)

| Tecla  | Ação                                         |
| ------ | -------------------------------------------- |
| 1..5   | Trocar screen (Dash/Rotin/Habit/Tasks/Timer) |
| Tab    | Navegar entre panels                         |
| ?      | Help overlay                                 |
| Ctrl+Q | Sair                                         |
| /      | Command bar (futuro — DT-019)                |

#### Navegação dentro de panels

| Tecla          | Ação                  |
| -------------- | --------------------- |
| j / seta baixo | Próximo item          |
| i / seta cima  | Item anterior         |
| t              | Ir para topo da lista |
| b              | Ir para fim da lista  |

#### CRUD contextual (panel focado)

| Tecla | Ação                    |
| ----- | ----------------------- |
| n     | Novo item (new/create)  |
| e     | Editar item sob cursor  |
| x     | Deletar item sob cursor |

#### Habits panel

| Tecla | Ação                           |
| ----- | ------------------------------ |
| v     | Marcar como done               |
| s     | Skip (com motivo)              |
| t     | Iniciar timer para o hábito    |
| u     | Desfazer (revert para pending) |

#### Tasks panel

| Tecla | Ação                   |
| ----- | ---------------------- |
| v     | Marcar como completa   |
| s     | Adiar (postpone)       |
| c     | Cancelar task          |
| u     | Reabrir task cancelada |

#### Timer panel

| Tecla | Ação             |
| ----- | ---------------- |
| space | Pausar / Resumir |
| c     | Cancelar timer   |

#### Agenda panel

| Tecla                    | Ação               |
| ------------------------ | ------------------ |
| j/k ou setas baixo/cimad | Scroll por slots   |
| a                        | Ir para hora atual |

### Princípios

1. Mnemônico em inglês: v=veritas (verified), s=skip, t=timer, n=new, e=edit, x=delete
2. Sem Ctrl para ações comuns — Ctrl reservado para sistema
3. Contexto determina ação: mesma tecla, comportamento diferente por panel
4. ? sempre mostra help contextual com teclas disponíveis
5. Status bar mostra hint das ações mais comuns

---

## Notas sobre limitações VTE

Conforme ADR-035, o GNOME Terminal (VTE) não transmite Ctrl+número,
Ctrl+Enter e Shift+Enter. Todos os bindings acima usam apenas teclas
que o VTE suporta.

---

## Sobre testes de TUI

### Textual pilot (atual)

O Textual oferece run_test() com pilot que simula teclas, cliques e
queries no DOM. É o equivalente do Puppeteer para TUIs Textual. Os
testes atuais subutilizam esse recurso — testam fragmentos isolados
em vez de fluxos completos.

### pexpect (futuro)

Para testes de integração da CLI real num pseudo-terminal, pexpect
permite controlar o processo como um usuário real: enviar input,
capturar output, verificar rendering. Mais lento, mas testa tudo
integrado incluindo a renderização real no terminal.

### Estratégia recomendada

Testes unit via pilot (rápidos, focados em lógica de interação).
Testes e2e via pilot com fluxos completos (criar hábito, completar,
verificar métricas). Testes smoke via pexpect (app abre, renderiza,
responde a input básico). A branch test/tui-panel-flows cobrirá isso.

---

## Referências

- calcurse: <https://calcurse.org/files/manual.html>
- calcure keybindings: <https://github.com/anufrievroman/calcure/wiki/Key-bindings>
- awesome-tuis: <https://github.com/rothgar/awesome-tuis>
- vim-keybindings-everywhere: <https://github.com/erikw/vim-keybindings-everywhere-the-ultimate-list>
- ADR-035: VTE terminal limitations

---

- **Data:** 2026-03-15
