# Dashboard TUI - Notas de Sprint

**Atualizado:** 23 Fev 2026

**Branch:** feat/tui-phase1

**Versão:** v1.7.0-dev

---

## 1. Entregue (Commits)

### v1.7.0 - TUI Phase 1

| Commit  | Descrição                                               |
| ------- | ------------------------------------------------------- |
| ee7a7b0 | feat(tui): Implementa Dashboard com agenda vertical     |
| a09a888 | refactor(tui): Refina Dashboard com mock data           |
| d5e0fd4 | docs(tui): Atualiza arquitetura e mockup v3             |
| 52d6392 | refactor(tui): Move HeaderBar para dentro do content    |
| 96a56d6 | feat(tui): Refina visual com cards, header e CSS        |
| 888b936 | docs(tui): Notas de sprint iniciais                     |
| 1e9772b | docs(tui): Adiciona sistema de cores semânticas         |
| 9733624 | refactor(tui): Migra cores para paleta Catppuccin Mocha |
| (pend.) | refactor(tui): Ajustes visuais ADR-021 no dashboard     |

### Funcionalidades Entregues

**DashboardScreen (BR-TUI-003):**

- Layout duas colunas: agenda (esquerda) + cards (direita)
- Agenda do Dia com régua de 30min, blocos proporcionais e background colorido
- 10 cores semânticas ADR-021 + 9 backgrounds (cor a 15% sobre Base)
- Suporte completo a substatus DONE (full/partial/overdone/excessive) e NOT_DONE (justified/unjustified/ignored)
- Bold exclusivo em running e paused (nome + ícone)
- Nome herda cor do status em todos os cards (pending = neutro)
- Caracteres de fill diferenciados: ░ (done/pending), ▓ (running), ▒ (paused), ┄ (not_done)
- Card Hábitos: ícone + nome colorido + horário (06:00 - 07:00) + duração (01h30m) + barra com quadradinhos cinzas
- Card Tarefas: 4 seções (pendentes por heat de proximidade, completed com strikethrough verde, cancelled com strikethrough muted, overdue em vermelho)
- Card Timer: ASCII art grande (3 linhas, estilo relógio digital), Mauve (running) ou Yellow (paused)
- Card Métricas: streak, completude 7d/30d, heatmap semanal

**Sistema de Cores (ADR-021):**

- `docs/tui/color-system.md`: 550 linhas, referência técnica completa
- `docs/html/themes/catppuccin-mocha.html`: showcase visual interativo
- 10 cores semânticas mapeadas para Catppuccin Mocha
- Gradiente térmico quente compartilhado (substatus DONE + proximidade tasks)
- 6 classes TCSS semânticas: below-target, above-target, over-limit, passive-fail, info, accent
- Fundamentação: ISO 3864 + ANSI Z535

**HeaderBar (BR-TUI-003 regra 1):**

- border_title com space-between: DASHBOARD / Data
- Conteúdo: Rotina | progresso | N tasks | Timer
- Mock data quando banco vazio

**Helpers e Funções Module-Level:**

- `_status_color()`: status/substatus → cor semântica (12 combinações)
- `_status_bg()`: status/substatus → background a 15% (12 combinações)
- `_status_icon()`: status/substatus → ícone (✓, ✓~, ✓+, ✓!, !, ✗!, ✗?, ▶, ⏸, ·)
- `_status_label()`: status/substatus → label textual
- `_fill_char()`: status → caractere de preenchimento (░, ▓, ▒, ┄)
- `_is_bold_status()`: retorna True apenas para running/paused
- `_task_proximity_color()`: dias → cor (heat de 7 faixas)
- `_render_ascii_time()`: string MM:SS → 3 linhas ASCII art
- `_format_duration()`: para agenda (Xm, Xh, XhYY)
- `_format_duration_card()`: para card hábitos (01h30m, 00h30m)
- `_find_block_at()`: busca por slot hora:minuto
- `_spaced_title()`: space-between com traços
- `_block_style()`: compat wrapper (fill + indicator)
- `calculate_block_height()`: altura proporcional (30min = 1 slot)
- `generate_time_slots()`: geração de slots de 30min

**CSS (BR-TUI-008):**

- Agenda com borda round e border_title
- Scrollbar fino (1) com cores Catppuccin
- Cards com padding padronizado
- 6 classes semânticas TCSS (below-target, above-target, etc.)
- HeaderBar com margin-bottom

**Testes (104 no dashboard):**

- `_format_duration`: 5 cenários
- `_format_duration_card`: 5 cenários
- `_find_block_at`: 7 cenários
- `_status_color`: 12 parametrizações
- `_status_bg`: 4 parametrizações
- `_status_icon`: 11 parametrizações
- `_is_bold_status`: 5 parametrizações
- `_fill_char`: 5 parametrizações
- `_block_style`: 10 indicadores + 9 cores + 3 extras (bg, bold running, bold paused, no bold done)
- `_task_proximity_color`: 12 parametrizações
- `_render_ascii_time`: 3 cenários
- Mock data: 10 validações (estrutura, status, substatus, overlap)
- `_spaced_title`: 2 cenários

**Métricas:**

- 1071 testes totais (todos passando)
- 104 testes específicos do dashboard
- 0 erros ruff, 0 warnings

---

## 2. Decisões Tomadas Nesta Sprint

### D-001: Granularidade da Agenda (30 minutos)

- **Decisão:** Régua de tempo com intervalos de 30min
- **BR atualizada:** BR-TUI-003 regra 2
- **Razão:** Blocos proporcionais à duração real; 30min = 1 slot visual

### D-002: Formatação de Duração (Agenda)

- **Decisão:** < 60 = Xm, >= 60 exata = Xh, >= 60 com resto = XhYY
- **BR atualizada:** BR-TUI-003 regra 2

### D-003: Indicadores de Prioridade por Cor (Tarefas)

- **Decisão:** Cor do indicador comunica urgência, sem texto
- **Esquema:** Heat de proximidade com 7 faixas (ver D-013)
- **Pendente:** Documentar como BR formal

### D-004: Mock Data como Rotina Demo

- **Decisão:** Mock data simula rotina completa "Rotina Demo" ativa por padrão
- **Composição:** 9 hábitos (todos status/substatus), 9 tasks (todos estados), timer ativo
- **Propósito:** Referência visual durante desenvolvimento, showcase para recrutadores
- **Status:** Implementado inline, pendente extração para `mock_data.py`

### D-005: Constantes em Módulo (PEP 8)

- **Decisão:** Cores, constantes de background, WEEKDAYS_PT, MONTHS_PT em módulo separado
- **Status:** Pendente refactor → `colors.py`

### D-006: Layout da Agenda (Blocos)

- **Decisão:** Nome/status/duração na primeira linha, barras com background abaixo
- **Referência:** Mockup v4

### D-007: Agenda border_title

- **Decisão:** Apenas "Agenda do Dia" (data já no header)

### D-008: Scrollbar

- **Decisão:** Largura 1, cores Catppuccin

### D-009: Paleta Catppuccin Mocha (ADR-021)

- **Decisão:** Substituir Material-like por Catppuccin Mocha como paleta base
- **Documentação:** `docs/tui/color-system.md`, showcase HTML
- **Fundamentação:** ISO 3864 + ANSI Z535
- **Pendente:** Formalizar como BR-TUI-008-Rxx ou ADR próprio

### D-010: 10 Cores Semânticas

- **Decisão:** 10 funções semânticas mapeadas para Catppuccin Mocha:
  - success (Green), below-target (Rosewater), above-target (Flamingo), over-limit (Peach)
  - warning (Yellow), error (Red), passive-fail (Maroon), info (Blue)
  - accent (Mauve), muted (Overlay0)
- **Pendente:** BR formal

### D-011: Substatus DONE com Gradiente Térmico

- **Decisão:** done/full (Green) → done/partial (Rosewater) → done/overdone (Flamingo) → done/excessive (Peach)
- **Thresholds:** full (90-110%), partial (<90%), overdone (110-150%), excessive (>150%)
- **Pendente:** BR-HABIT-xxx formal

### D-012: Substatus NOT_DONE

- **Decisão:** justified (Yellow), unjustified (Red), ignored (Maroon)
- **Pendente:** BR-HABIT-xxx formal

### D-013: Heat de Proximidade Tasks (7 Faixas)

- **Decisão:** Gradient quente para pendentes, vermelho para overdue:
  - Hoje = Yellow, Amanhã = Peach, 2-3d = Flamingo, 4-7d = Rosewater
  - 1-2sem = Subtext1, 2+sem = Subtext0, 1+mês = Overlay0
- **Pendente:** BR-TASK-xxx formal

### D-014: Bold Exclusivo Running/Paused

- **Decisão:** Apenas running e paused usam bold no nome e ícone
- **Razão:** Destaca os dois estados que requerem atenção imediata do usuário
- **Pendente:** BR-TUI-008-Rxx formal

### D-015: Nome Herda Cor do Status

- **Decisão:** Em todos os cards, o nome do hábito/task herda a cor semântica do status. Exceção: pending mantém cor neutra (Text)
- **Pendente:** BR-TUI-008-Rxx formal

### D-016: Formatação de Duração no Card Hábitos

- **Decisão:** Zero-padded com unidade: 01h30m, 00h30m (diferente da agenda que usa 1h30, 30m)
- **Razão:** Alinhamento visual em coluna tabular
- **Pendente:** Atualizar D-002

### D-017: Horário com Espaço no Card Hábitos

- **Decisão:** `06:00 - 07:00` com espaço ao redor do hífen (não `06:00-07:00`)
- **Razão:** Legibilidade

### D-018: Background Colorido nos TimeBlocks

- **Decisão:** Fills na agenda usam background (cor a 15% sobre Base #1E1E2E)
- **Implementação:** 9 constantes BG\_\* calculadas, Rich markup `[cor on bg]`
- **Referência:** Showcase HTML (catppuccin-mocha.html)
- **Pendente:** BR formal

### D-019: Timer em ASCII Art

- **Decisão:** Elapsed renderizado em 3 linhas de ASCII art (estilo relógio digital)
- **Caracteres:** █, ▀, ▄ para dígitos, · para separador
- **Cores:** Mauve bold (running), Yellow bold (paused), Overlay0 (idle)
- **Pendente:** BR-TUI-006-Rxx formal

### D-020: Slots Uniformes na Agenda

- **Decisão:** Cada slot de 30min ocupa exatamente 2 linhas, independente de estar livre ou ocupado
- **Razão:** Altura proporcional uniforme, alinhamento visual consistente

### D-021: Ícones por Substatus (ADR-021)

- **Decisão:** Ícones diferenciados por substatus conforme tabela:
  - DONE: ✓ (full), ✓~ (partial), ✓+ (overdone), ✓! (excessive)
  - NOT_DONE: ! (justified), ✗! (unjustified), ✗? (ignored)
  - RUNNING: ▶, PAUSED: ⏸, PENDING: ·
- **Pendente:** BR formal

### D-022: Barra de Progresso com Quadradinhos Cinzas

- **Decisão:** Barras de progresso no card hábitos preenchem com cor do status e completam com quadradinhos cinzas (dim) até max_bars=4
- **Status não realizado:** Exibe traços (────)
- **Status pending:** Todos cinzas
- **Pendente:** BR formal

### D-023: Renomear Card para Panel

- **Decisão:** Substituir nomenclatura "card" por "panel" em todo o projeto
- **Escopo:** Código (classes, IDs CSS, variáveis), documentação (BRs, mockups, sprint notes), testes
- **Razão:** "Card" implica Material Design; "Panel" é semanticamente correto para Textual (painel de conteúdo em layout)
- **Status:** Pendente - será aplicado durante refactor SOLID dos widgets
- **Impacto:** IDs CSS (#card-habits → #panel-habits), classes (HabitsCard → HabitsPanel), BRs (atualizar referências)' >> docs/tui/dashboard-sprint-notes.md

---

## 3. Mock Data - Rotina Demo

O mock data simula uma rotina ativa completa para desenvolvimento e showcase. Quando o banco está vazio, o dashboard renderiza automaticamente esta rotina, permitindo visualizar todos os estados visuais sem necessidade de dados reais.

### 3.1. MOCK_INSTANCES (9 hábitos)

```
Nome              Horário      Status     Substatus    Minutos
─────────────────────────────────────────────────────────────
Despertar         06:00-07:00  done       full         60
Academia          07:00-08:00  done       partial      45
Trabalho          09:00-12:00  running    -            47
Almoço            12:00-13:00  done       overdone     75
Estudo            14:00-16:00  paused     -            12
Café da Tarde     16:00-17:00  done       excessive    50
Organização       17:00-18:00  not_done   unjustified  -
Jantar            19:00-20:00  not_done   ignored      -
Leitura           21:00-22:00  pending    -            -
```

**Cobertura de status:** done (4), not_done (2), running (1), paused (1), pending (1)

**Cobertura de substatus DONE:** full, partial, overdone, excessive (todos os 4)

**Cobertura de substatus NOT_DONE:** unjustified, ignored (2 de 3; justified ausente no mock)

### 3.2. MOCK_TASKS (9 tasks)

```
Nome              Proximidade  Data     Hora   Status      Dias
──────────────────────────────────────────────────────────────
Dentista          Hoje         23 Feb   15:00  pending     0
Email cliente     Amanhã       24 Feb   09:00  pending     1
Deploy staging    3 dias       26 Feb   10:00  pending     3
Code review       5 dias       28 Feb   14:00  pending     5
Retrospectiva     2 mês        25 Apr   --:--  pending     61
Comprar domínio   Hoje         23 Feb   09:30  completed   -
Evento cancelado  ---          20 Feb   16:00  cancelled   -
Enviar relatório  1 sem        16 Feb   --:--  overdue     -
Revisar PR #142   3 dias       20 Feb   14:00  overdue     -
```

**Cobertura de status:** pending (5), completed (1), cancelled (1), overdue (2)

**Cobertura de heat:** 5 faixas de proximidade exercitadas (0d, 1d, 3d, 5d, 61d)

### 3.3. MOCK_TIMER

```
elapsed: "47:23"
name: "Trabalho"
status: "running"
```

### 3.4. Extração Planejada

O mock data será extraído para `src/timeblock/tui/mock_data.py` no refactor SOLID, incluindo:

- Constante `DEMO_ROUTINE_NAME = "Rotina Demo"`
- `MOCK_INSTANCES`, `MOCK_TASKS`, `MOCK_TIMER`
- Funções factory opcionais para gerar variações de teste

---

## 4. Pendente Para Fechar Dashboard v1

### Commit Imediato

- [ ] Commit visual: substatus + backgrounds + ASCII timer + nome herda cor (arquivos prontos, 104 testes passando)

### Refactor SOLID (próximo commit)

- [ ] Extrair `src/timeblock/tui/colors.py`: constantes C*\*, BG*_, funções *status*_
- [ ] Extrair `src/timeblock/tui/formatters.py`: \_format_duration, \_format_duration_card, \_spaced_title, \_render_ascii_time
- [ ] Extrair `src/timeblock/tui/mock_data.py`: MOCK_INSTANCES, MOCK_TASKS, MOCK_TIMER
- [ ] Dashboard.py resultante: apenas compose + render (delegando para helpers)
- [ ] Atualizar imports nos testes

### Documentação (após refactor)

- [ ] BR formal para substatus DONE (D-011): BR-HABIT-xxx com thresholds 90/110/150%
- [ ] BR formal para substatus NOT_DONE (D-012): BR-HABIT-xxx
- [ ] BR formal para heat de proximidade tasks (D-013): BR-TASK-xxx
- [ ] BR formal para bold exclusivo running/paused (D-014): BR-TUI-008-Rxx
- [ ] BR formal para nome herda cor do status (D-015): BR-TUI-008-Rxx
- [ ] BR formal para background colorido (D-018): BR-TUI-008-Rxx
- [ ] BR formal para timer ASCII art (D-019): BR-TUI-006-Rxx
- [ ] BR formal para ícones por substatus (D-021): BR-TUI-008-Rxx
- [ ] BR formal para barra com quadradinhos cinzas (D-022): BR-TUI-008-Rxx
- [ ] Atualizar ADR-021 status de "Proposto" para "Aceito"
- [ ] Atualizar mockup v4 com layout final

### Visual (baixa prioridade)

- [ ] HeaderBar com dados reais da rotina (integração RoutineService)
- [ ] Card Métricas com dados reais (integração com services)
- [ ] Footer/StatusBar 3 seções (BR-TUI-007)

---

## 5. Changelog do Documento

| Data       | Versão | Mudanças                                                |
| ---------- | ------ | ------------------------------------------------------- |
| 2026-02-22 | 1.0.0  | Criação inicial com 6 commits e 28 testes               |
| 2026-02-23 | 2.0.0  | ADR-021 integrado, D-009 a D-022, mock data, 104 testes |

---

**Próxima revisão:** Após refactor SOLID

**Última atualização:** 23 de Fevereiro de 2026
